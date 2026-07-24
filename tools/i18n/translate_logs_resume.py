#!/usr/bin/env python3
"""Translate remaining log keys via Gemini with long cooldown; resume-friendly."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "i18n"))

from translate_gemini import (  # noqa: E402
    get_client,
    load_batch,
    load_rules,
    translate_chunk,
)

MISSING = ROOT / "tools" / "i18n" / "reports" / "missing-log-keys-th.json"
DONE_DIR = ROOT / "tools" / "i18n" / "batches" / "th" / "done"
TH = ROOT / "BetterGenshinImpact" / "User" / "I18n" / "th.json"
CHUNK = 35
PAUSE = 8


def merge_into_th(fragment: dict[str, str]) -> tuple[int, int]:
    th = json.loads(TH.read_text(encoding="utf-8"))
    before = len(th)
    added = 0
    for k, v in fragment.items():
        if not str(v).strip():
            continue
        if k not in th or not str(th.get(k, "")).strip():
            th[k] = v
            added += 1
    TH.write_text(json.dumps(th, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return added, len(th) - before


def main() -> int:
    missing = json.loads(MISSING.read_text(encoding="utf-8"))
    th = json.loads(TH.read_text(encoding="utf-8"))
    todo = {k: "" for k in missing if k not in th or not str(th.get(k, "")).strip()}
    print(f"todo: {len(todo)}")
    if not todo:
        return 0

    DONE_DIR.mkdir(parents=True, exist_ok=True)
    client = get_client()
    rules = load_rules()
    keys = list(todo.keys())
    total_added = 0
    batch_idx = 0
    for i in range(0, len(keys), CHUNK):
        batch_idx += 1
        chunk = {k: "" for k in keys[i : i + CHUNK]}
        print(f"batch {batch_idx}: {len(chunk)} keys (offset {i})")
        translated = translate_chunk(
            client,
            model="models/gemini-3.6-flash",
            keys=chunk,
            rules=rules,
            max_output_tokens=65536,
            thinking_level="low",
            retries=12,
        )
        out = DONE_DIR / f"batch-log-resume-{batch_idx:03d}-th.json"
        out.write_text(json.dumps(translated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # re-read th before merge (sibling-safe)
        added, _ = merge_into_th(translated)
        total_added += added
        print(f"  wrote {out.name}; added {added}; total_added {total_added}")
        time.sleep(PAUSE)
    print(f"DONE total_added={total_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
