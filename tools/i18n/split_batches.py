#!/usr/bin/env python3
"""Split i18n scan CSVs into fixed-size batches for parallel translation agents."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_keys(csv_path: Path) -> list[str]:
    keys: list[str] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        field = "key" if "key" in (reader.fieldnames or []) else (reader.fieldnames or ["key"])[0]
        for row in reader:
            value = (row.get(field) or "").strip()
            if value:
                keys.append(value)
    return keys


def write_batch(out_dir: Path, batch_id: int, keys: list[str], locale: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"batch-{batch_id:03d}"
    json_path = out_dir / f"{stem}-{locale}.json"
    payload = {k: "" for k in keys}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    csv_path = out_dir / f"{stem}-{locale}.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "translation", "notes"])
        for key in keys:
            writer.writerow([key, "", ""])
    return json_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("tools/i18n/reports/missing-json-keys-th.csv"),
        help="CSV from scan_missing.py (default: missing-json-keys-th.csv)",
    )
    parser.add_argument("--locale", default="th", help="Target locale code (default: th)")
    parser.add_argument("--batch-size", type=int, default=150, help="Keys per batch (default: 150)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tools/i18n/batches"),
        help="Output directory for batch files",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        print("Run: python tools/i18n/scan_missing.py --target-locale th")
        return 1

    keys = read_keys(args.input)
    if not keys:
        print(f"No keys found in {args.input}")
        return 1

    out_root = args.output_dir / args.locale
    manifest: list[dict] = []
    batch_id = 0
    for i in range(0, len(keys), args.batch_size):
        batch_id += 1
        chunk = keys[i : i + args.batch_size]
        json_path = write_batch(out_root, batch_id, chunk, args.locale)
        manifest.append(
            {
                "batch": batch_id,
                "count": len(chunk),
                "json": str(json_path.as_posix()),
            }
        )

    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "locale": args.locale,
                "source_csv": str(args.input.as_posix()),
                "total_keys": len(keys),
                "batch_size": args.batch_size,
                "batches": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Split {len(keys)} keys into {batch_id} batches under {out_root}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
