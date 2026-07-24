#!/usr/bin/env python3
"""Merge translated JSON batch fragments into a single locale file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object")
    return {str(k): str(v) if v is not None else "" for k, v in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", default="th", help="Target locale (default: th)")
    parser.add_argument(
        "--fragments",
        type=Path,
        nargs="+",
        help="Translated JSON fragment files (batch outputs)",
    )
    parser.add_argument(
        "--fragments-dir",
        type=Path,
        help="Directory containing batch-*-{locale}.json files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (default: BetterGenshinImpact/User/I18n/{locale}.json)",
    )
    parser.add_argument(
        "--drop-empty",
        action="store_true",
        help="Omit keys whose translation is blank",
    )
    args = parser.parse_args()

    paths: list[Path] = list(args.fragments or [])
    if args.fragments_dir:
        paths.extend(sorted(args.fragments_dir.glob(f"batch-*-{args.locale}.json")))
        # Also accept Gemini / scan outputs that are not named batch-NNN
        paths.extend(sorted(args.fragments_dir.glob(f"*-{args.locale}.json")))
        paths.extend(sorted(args.fragments_dir.glob("missing-*-batch.json")))
        # de-dupe while preserving order
        seen: set[Path] = set()
        uniq: list[Path] = []
        for p in paths:
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            uniq.append(p)
        paths = uniq

    if not paths:
        print("Provide --fragments and/or --fragments-dir")
        return 1

    merged: dict[str, str] = {}
    output = args.output or Path(f"BetterGenshinImpact/User/I18n/{args.locale}.json")
    if output.exists():
        merged.update(load_json(output))

    for path in paths:
        fragment = load_json(path)
        for key, value in fragment.items():
            if key in merged and merged[key] != value and value:
                print(f"Warning: duplicate key with different value in {path.name}: {key[:40]}...")
            if value or key not in merged:
                merged[key] = value

    if args.drop_empty:
        merged = {k: v for k, v in merged.items() if v.strip()}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    filled = sum(1 for v in merged.values() if v.strip())
    print(f"Wrote {len(merged)} keys ({filled} translated) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
