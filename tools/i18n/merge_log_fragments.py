#!/usr/bin/env python3
"""Merge log translation fragments into th.json without overwriting existing values."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TH = REPO / "BetterGenshinImpact" / "User" / "I18n" / "th.json"
DONE = REPO / "tools" / "i18n" / "batches" / "th" / "done"

GLOBS = [
    "batch-manual-log-*-th.json",
    "batch-000-log-priority-th.json",
    "batch-101-log-th.json",
    "batch-102-log-th.json",
]


def main() -> None:
    th = json.loads(TH.read_text(encoding="utf-8"))
    before = len(th)
    added = 0
    skipped_existing = 0
    empty_skipped = 0

    paths: list[Path] = []
    for g in GLOBS:
        paths.extend(sorted(DONE.glob(g)))

    for path in paths:
        frag = json.loads(path.read_text(encoding="utf-8"))
        for k, v in frag.items():
            if not isinstance(v, str) or not v.strip():
                empty_skipped += 1
                continue
            if k in th and str(th[k]).strip():
                skipped_existing += 1
                continue
            th[k] = v
            added += 1
        print(f"  {path.name}: processed {len(frag)}")

    TH.write_text(json.dumps(th, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"th.json {before} -> {len(th)} | added={added} skipped_existing={skipped_existing} empty={empty_skipped}")


if __name__ == "__main__":
    main()
