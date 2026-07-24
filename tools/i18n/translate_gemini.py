#!/usr/bin/env python3
"""Translate i18n batch JSON files using Google Gemini API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

PROMPT_PATH = Path(__file__).with_name("agent_prompt_th.md")
ENV_PATH = Path(__file__).with_name(".env")
DEFAULT_MODEL = "models/gemini-3.6-flash"


def load_dotenv(path: Path = ENV_PATH) -> None:
    """Load KEY=VALUE pairs from tools/i18n/.env into os.environ (no overwrite)."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_rules() -> str:
    if PROMPT_PATH.exists():
        text = PROMPT_PATH.read_text(encoding="utf-8")
        # Drop the copy-paste header; keep rules + format guidance.
        if "## Rules" in text:
            return text[text.index("## Rules") :]
    return (
        "Translate Chinese UI strings to Thai. Preserve {0}, \\n, HTML, keyboard names. "
        "Keep proper names in English (Fontaine, Liyue, Jean, Medaka)."
    )


def load_batch(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def keys_to_translate(batch: dict[str, str], *, retranslate: bool) -> dict[str, str]:
    if retranslate:
        return dict(batch)
    return {k: v for k, v in batch.items() if not v.strip()}


def build_prompt(keys: dict[str, str], rules: str) -> str:
    payload = json.dumps(keys, ensure_ascii=False, indent=2)
    return (
        f"{rules}\n\n"
        "## Task\n"
        "Translate every value in the JSON below from Chinese to Thai.\n"
        "Return ONLY a valid JSON object with the exact same keys.\n"
        "Do not wrap in markdown code fences.\n\n"
        f"{payload}"
    )


def extract_json(text: str) -> dict[str, str]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("Model response does not contain JSON object")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("Model response JSON is not an object")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def get_client():
    load_dotenv()
    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit(
            "Missing package: pip install -r tools/i18n/requirements-gemini.txt"
        ) from exc

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set GEMINI_API_KEY in tools/i18n/.env or environment (see .env.example)"
        )
    return genai.Client(api_key=api_key)


def translate_chunk(
    client,
    *,
    model: str,
    keys: dict[str, str],
    rules: str,
    max_output_tokens: int,
    thinking_level: str,
    retries: int,
) -> dict[str, str]:
    prompt = build_prompt(keys, rules)
    generation_config = {
        "max_output_tokens": max_output_tokens,
        "thinking_level": thinking_level,
    }
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            interaction = client.interactions.create(
                model=model,
                input=prompt,
                generation_config=generation_config,
            )
            output = getattr(interaction, "output_text", None) or ""
            if not output.strip():
                raise ValueError("Empty model response")
            result = extract_json(output)
            missing = set(keys) - set(result)
            if missing:
                sample = ", ".join(list(missing)[:3])
                raise ValueError(f"Missing {len(missing)} keys in response (e.g. {sample})")
            return result
        except Exception as exc:  # noqa: BLE001 - retry loop
            last_error = exc
            msg = str(exc)
            if attempt < retries:
                wait = 2 * attempt
                # Free-tier 429: honor "Please retry in Ns" when present
                m = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)s", msg, re.I)
                if m or "429" in msg or "too_many_requests" in msg or "RESOURCE_EXHAUSTED" in msg:
                    wait = max(wait, float(m.group(1)) + 2 if m else 65.0)
                    print(f"      rate-limited; sleeping {wait:.0f}s (attempt {attempt}/{retries})")
                time.sleep(wait)
    assert last_error is not None
    raise last_error


def chunk_dict(items: dict[str, str], size: int) -> list[dict[str, str]]:
    if size <= 0:
        return [items]
    keys = list(items.keys())
    return [{k: items[k] for k in keys[i : i + size]} for i in range(0, len(keys), size)]


def translate_batch_file(
    path: Path,
    *,
    client,
    model: str,
    rules: str,
    chunk_size: int,
    max_output_tokens: int,
    thinking_level: str,
    retries: int,
    retranslate: bool,
    dry_run: bool,
    chunk_pause: float = 3.0,
) -> dict[str, str]:
    batch = load_batch(path)
    todo = keys_to_translate(batch, retranslate=retranslate)
    if not todo:
        print(f"  skip (already translated): {path.name}")
        return batch

    print(f"  translating {len(todo)} keys in {path.name}")
    if dry_run:
        return batch

    merged = dict(batch)
    chunks = chunk_dict(todo, chunk_size)
    for idx, chunk in enumerate(chunks, start=1):
        print(f"    chunk {idx}/{len(chunks)} ({len(chunk)} keys)")
        translated = translate_chunk(
            client,
            model=model,
            keys=chunk,
            rules=rules,
            max_output_tokens=max_output_tokens,
            thinking_level=thinking_level,
            retries=retries,
        )
        merged.update(translated)
        if chunk_pause > 0 and idx < len(chunks):
            time.sleep(chunk_pause)
    return merged


def resolve_inputs(inputs: list[Path], glob_pattern: str | None) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.glob(glob_pattern or "batch-*-th.json")))
        else:
            paths.append(item)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Batch JSON file(s) or directory (default: tools/i18n/batches/th)",
    )
    parser.add_argument("--glob", default="batch-*-th.json", help="Glob when input is a directory")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tools/i18n/batches/th/done"),
        help="Where to write translated batches",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL})")
    parser.add_argument("--chunk-size", type=int, default=50, help="Keys per API call (default: 50)")
    parser.add_argument("--max-output-tokens", type=int, default=65536)
    parser.add_argument("--thinking-level", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--retries", type=int, default=8)
    parser.add_argument(
        "--chunk-pause",
        type=float,
        default=3.0,
        help="Seconds to sleep between successful chunks (rate-limit friendly)",
    )
    parser.add_argument("--retranslate", action="store_true", help="Re-translate non-empty values too")
    parser.add_argument("--dry-run", action="store_true", help="Show work only; do not call API")
    parser.add_argument(
        "--from-scan",
        action="store_true",
        help="Translate tools/i18n/reports/missing-all-th-batch.json (from scan_all_th.py)",
    )
    args = parser.parse_args()

    load_dotenv()
    if args.from_scan:
        inputs = [Path("tools/i18n/reports/missing-all-th-batch.json")]
    else:
        inputs = args.inputs or [Path("tools/i18n/batches/th")]
    paths = resolve_inputs(inputs, args.glob)
    if not paths:
        print("No batch files found")
        return 1

    rules = load_rules()
    client = None if args.dry_run else get_client()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for path in paths:
        try:
            result = translate_batch_file(
                path,
                client=client,
                model=args.model,
                rules=rules,
                chunk_size=args.chunk_size,
                max_output_tokens=args.max_output_tokens,
                thinking_level=args.thinking_level,
                retries=args.retries,
                retranslate=args.retranslate,
                dry_run=args.dry_run,
                chunk_pause=args.chunk_pause,
            )
            if not args.dry_run:
                out = args.output_dir / path.name
                out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"  wrote {out}")
            ok += 1
        except Exception as exc:  # noqa: BLE001 - batch-level failure
            print(f"  FAILED {path.name}: {exc}", file=sys.stderr)

    print(f"Done: {ok}/{len(paths)} batch(es)")
    return 0 if ok == len(paths) else 1


if __name__ == "__main__":
    raise SystemExit(main())
