#!/usr/bin/env python3
"""Comprehensive Thai i18n scanner — finds ALL Chinese UI-facing strings.

Unlike the older scan_missing.py (attribute-focused + strict filters) and
find_missing_th.py (raw dump), this scanner:

  * XAML attributes (Text/Content/Header/ToolTip/Title/…)
  * XAML element text content (standalone lines AND inline >text<)
  * C# string literals in View / ViewModel / Model / Service / Helpers / Core/Config
  * ThemedMessageBox / WithCultureGet anywhere under BetterGenshinImpact
  * Keys present in en.json but missing from th.json
  * Does NOT skip just because a string was never in batch-001..014

Outputs (tools/i18n/reports/):
  scan-all-th.json              full report
  missing-all-th.csv            translate candidates (CJK, missing/empty in th.json)
  missing-all-th-batch.json     empty-value batch ready for Gemini / agents
  non-ui-chinese-th.csv         CJK found but classified as log/incomplete/code
  empty-th.csv                  keys in th.json with blank values
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APP = REPO / "BetterGenshinImpact"
TH_PATH = APP / "User" / "I18n" / "th.json"
EN_PATH = APP / "User" / "I18n" / "en.json"
REPORTS = Path(__file__).resolve().parent / "reports"

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
BINDING_RE = re.compile(r"\{Binding|\{StaticResource|\{DynamicResource|\{x:", re.I)
XAML_ENTITY_RE = re.compile(r"&#x?[0-9a-fA-F]+;")

# Mirrors AutoTranslateInterceptor.ShouldTranslatePropertyName (Contains-style)
XAML_ATTR_RE = re.compile(
    r'(?P<attr>(?:\w+:)?\w*(?:Text|Content|Header|ToolTip|Title|Subtitle|'
    r'Description|PlaceholderText|Placeholder|Label|Caption)\w*)\s*=\s*"(?P<value>[^"]*)"',
    re.IGNORECASE,
)
XAML_INLINE_CONTENT_RE = re.compile(r">([^<>{}\n]+)<")
CS_STRING_RE = re.compile(r'(?P<prefix>@)?"(?P<value>(?:\\.|[^"\\])*)"')
WITH_CULTURE_GET_RE = re.compile(
    r'WithCultureGet\s*\([^,]+,\s*"((?:\\.|[^"\\])*)"',
)
THEMED_MSG_RE = re.compile(
    r'ThemedMessageBox\.\w+\s*\(\s*"((?:\\.|[^"\\])*)"',
)

CS_UI_PREFIXES = (
    "BetterGenshinImpact/View/",
    "BetterGenshinImpact/ViewModel/",
    "BetterGenshinImpact/Model/",
    "BetterGenshinImpact/Service/",
    "BetterGenshinImpact/Helpers/",
    "BetterGenshinImpact/Helper/",
    "BetterGenshinImpact/Core/Config/",
)

SKIP_DIR_NAMES = {"bin", "obj", ".git", "packages", "node_modules"}

# Lines that look like logging / serialization, not user-facing UI
LOG_HINT_RE = re.compile(
    r"(Log(?:Information|Error|Warning|Debug|Trace)|Debug\.Write|"
    r"Console\.(?:Write|WriteLine)|Serilog|"
    r"throw new |ArgumentException|InvalidOperation)",
)
INCOMPLETE_INTERP_RE = re.compile(
    r"\{[A-Za-z_][\w.]*\.(?:ToString|Message|Code|StatusCode)\s*\([^}]*$"
    r"|\{[^}]*\?\?\s*$"
    r"|\{[^}]*$"  # unclosed brace at end — often split string
)
API_PATH_NOISE_RE = re.compile(
    r"^(?:icon_doc|item_doc|marker_doc|oauth)/|"
    r"无法反序列化|返回内容为空|返回错误|"
    r"PDH GPU|状态码 0x"
)


@dataclass
class Hit:
    text: str
    file: str
    line: int
    kind: str  # xaml-attr | xaml-content | cs | themed | culture | en.json
    property: str = ""
    category: str = "ui"  # ui | log | incomplete | noise
    notes: str = ""


@dataclass
class Report:
    generated_at: str
    th_keys_total: int
    th_empty: int
    unique_source_cjk: int
    missing_ui: int
    missing_non_ui: int
    already_translated: int
    empty_keys: list[str] = field(default_factory=list)
    missing_ui_keys: list[dict] = field(default_factory=list)
    missing_non_ui_keys: list[dict] = field(default_factory=list)
    by_kind: dict = field(default_factory=dict)
    by_category: dict = field(default_factory=dict)


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def decode_xaml_entities(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        entity = match.group(0)
        if entity.startswith("&#x"):
            return chr(int(entity[3:-1], 16))
        if entity.startswith("&#"):
            return chr(int(entity[2:-1], 10))
        return entity

    return XAML_ENTITY_RE.sub(repl, text)


def normalize_text(text: str) -> str:
    return (
        decode_xaml_entities(text)
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
    )


def classify(text: str, *, kind: str, line_ctx: str = "") -> str:
    """Classify a CJK string as ui / log / incomplete / noise."""
    t = text.strip()
    if not t or not contains_cjk(t):
        return "noise"
    if INCOMPLETE_INTERP_RE.search(t) and t.count("{") > t.count("}"):
        return "incomplete"
    if API_PATH_NOISE_RE.search(t):
        return "noise"
    if LOG_HINT_RE.search(line_ctx):
        # Still UI if ThemedMessageBox / explicit dialog patterns
        if kind in {"themed", "xaml-attr", "xaml-content", "culture"}:
            return "ui"
        # Short labels next to log calls can still be UI titles — keep cautious
        if len(t) < 40 and not any(x in t for x in ("失败", "异常", "错误信息", "返回")):
            return "ui"
        return "log"
    # Pure log-style prefixes
    if t.startswith("[00:") or re.match(r"^\[\d{2}:\d{2}", t):
        return "log"
    if kind == "cs" and any(
        x in t
        for x in (
            "反序列化",
            "LogInformation",
            "跳过此任务",
            "→ 开始执行",
            "→ 脚本执行结束",
        )
    ):
        # Runtime log / status — still shown in UI log box sometimes → keep as ui
        if t.startswith("→") or "跳过" in t:
            return "ui"
        return "log"
    return "ui"


def should_skip_path(path: Path) -> bool:
    return bool(SKIP_DIR_NAMES & set(path.parts))


def scan_xaml(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    rel = str(path.relative_to(REPO)).replace("\\", "/")
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for line_no, line in enumerate(text.splitlines(), 1):
        if BINDING_RE.search(line):
            # Still allow attrs on same line if value is literal — but usually binding.
            # Skip entire line when binding present (safer; fewer false positives).
            continue
        for m in XAML_ATTR_RE.finditer(line):
            value = normalize_text(m.group("value")).strip()
            if not contains_cjk(value):
                continue
            cat = classify(value, kind="xaml-attr", line_ctx=line)
            hits.append(
                Hit(value, rel, line_no, "xaml-attr", m.group("attr"), cat)
            )
        for m in XAML_INLINE_CONTENT_RE.finditer(line):
            value = normalize_text(m.group(1)).strip()
            if not value or not contains_cjk(value) or value.startswith("<!--"):
                continue
            cat = classify(value, kind="xaml-content", line_ctx=line)
            hits.append(Hit(value, rel, line_no, "xaml-content", "inline", cat))
        # Standalone element content line (TextBlock body on its own line)
        stripped = line.strip()
        if (
            stripped
            and "<" not in stripped
            and ">" not in stripped
            and "=" not in stripped
            and not stripped.startswith("<!--")
            and contains_cjk(stripped)
        ):
            value = normalize_text(stripped)
            cat = classify(value, kind="xaml-content", line_ctx=line)
            hits.append(Hit(value, rel, line_no, "xaml-content", "Element.Content", cat))
    return hits


def scan_cs(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    rel = str(path.relative_to(REPO)).replace("\\", "/")
    is_ui_path = rel.startswith(CS_UI_PREFIXES)
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    # strip block comments lightly
    content = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)

    for line_no, line in enumerate(content.splitlines(), 1):
        if line.strip().startswith("//"):
            continue
        for m in WITH_CULTURE_GET_RE.finditer(line):
            value = normalize_text(m.group(1))
            if contains_cjk(value):
                hits.append(
                    Hit(
                        value,
                        rel,
                        line_no,
                        "culture",
                        "WithCultureGet",
                        classify(value, kind="culture", line_ctx=line),
                    )
                )
        for m in THEMED_MSG_RE.finditer(line):
            value = normalize_text(m.group(1))
            if contains_cjk(value):
                hits.append(
                    Hit(
                        value,
                        rel,
                        line_no,
                        "themed",
                        "ThemedMessageBox",
                        classify(value, kind="themed", line_ctx=line),
                    )
                )
        if not is_ui_path:
            continue
        if "LocalizedString" in line or "ResourceManager" in line:
            continue
        for m in CS_STRING_RE.finditer(line):
            value = normalize_text(m.group("value"))
            if not contains_cjk(value):
                continue
            if len(value) > 800:
                continue
            cat = classify(value, kind="cs", line_ctx=line)
            hits.append(Hit(value, rel, line_no, "cs", "string-literal", cat))
    return hits


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def build_report(*, emit_batch: bool, batch_out: Path | None) -> Report:
    th: dict[str, str] = {}
    if TH_PATH.exists():
        th = {str(k): "" if v is None else str(v) for k, v in json.loads(TH_PATH.read_text(encoding="utf-8")).items()}
    en: dict[str, str] = {}
    if EN_PATH.exists():
        en = {str(k): "" if v is None else str(v) for k, v in json.loads(EN_PATH.read_text(encoding="utf-8")).items()}

    all_hits: list[Hit] = []
    for xaml in APP.rglob("*.xaml"):
        if should_skip_path(xaml):
            continue
        all_hits.extend(scan_xaml(xaml))
    for cs in APP.rglob("*.cs"):
        if should_skip_path(cs):
            continue
        all_hits.extend(scan_cs(cs))

    # en.json keys with CJK that are missing from th
    for k in en:
        if contains_cjk(k) and k not in th:
            all_hits.append(Hit(k, "BetterGenshinImpact/User/I18n/en.json", 0, "en.json", "key", "ui"))

    # Dedupe by text — keep first hit, aggregate sources
    by_text: dict[str, list[Hit]] = defaultdict(list)
    for h in all_hits:
        by_text[h.text].append(h)

    empty_keys = sorted(k for k, v in th.items() if not v.strip())
    missing_ui: list[dict] = []
    missing_non_ui: list[dict] = []
    already = 0
    kind_counts: dict[str, int] = defaultdict(int)
    cat_counts: dict[str, int] = defaultdict(int)

    for text, hits in sorted(by_text.items(), key=lambda x: x[0]):
        primary = hits[0]
        # Prefer ui category if any hit says ui
        cats = {h.category for h in hits}
        category = "ui" if "ui" in cats else primary.category
        kind_counts[primary.kind] += 1
        cat_counts[category] += 1

        sources = "; ".join(f"{h.file}:{h.line}:{h.kind}" for h in hits[:5])
        row = {
            "key": text,
            "category": category,
            "kind": primary.kind,
            "property": primary.property,
            "sources": sources,
            "hit_count": len(hits),
            "in_th": text in th,
            "th_value": th.get(text, ""),
        }

        if text in th and th[text].strip():
            already += 1
            continue
        if text in th and not th[text].strip():
            # empty — treat as missing ui if category ui
            if category == "ui":
                missing_ui.append(row)
            else:
                missing_non_ui.append(row)
            continue
        # not in th at all
        if category == "ui":
            missing_ui.append(row)
        else:
            missing_non_ui.append(row)

    report = Report(
        generated_at=datetime.now(timezone.utc).isoformat(),
        th_keys_total=len(th),
        th_empty=len(empty_keys),
        unique_source_cjk=len(by_text),
        missing_ui=len(missing_ui),
        missing_non_ui=len(missing_non_ui),
        already_translated=already,
        empty_keys=empty_keys,
        missing_ui_keys=missing_ui,
        missing_non_ui_keys=missing_non_ui,
        by_kind=dict(kind_counts),
        by_category=dict(cat_counts),
    )

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "scan-all-th.json").write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(
        REPORTS / "missing-all-th.csv",
        missing_ui,
        ["key", "category", "kind", "property", "sources", "hit_count", "in_th", "th_value"],
    )
    write_csv(
        REPORTS / "non-ui-chinese-th.csv",
        missing_non_ui,
        ["key", "category", "kind", "property", "sources", "hit_count", "in_th", "th_value"],
    )
    write_csv(
        REPORTS / "empty-th.csv",
        [{"key": k} for k in empty_keys],
        ["key"],
    )

    batch = {row["key"]: "" for row in missing_ui}
    batch_path = batch_out or (REPORTS / "missing-all-th-batch.json")
    if emit_batch:
        batch_path.parent.mkdir(parents=True, exist_ok=True)
        batch_path.write_text(
            json.dumps(batch, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"th.json keys:           {report.th_keys_total}")
    print(f"th.json empty values:   {report.th_empty}")
    print(f"Unique CJK in source:   {report.unique_source_cjk}")
    print(f"Already translated:     {report.already_translated}")
    print(f"Missing UI (translate): {report.missing_ui}")
    print(f"Missing non-UI (skip):  {report.missing_non_ui}")
    print(f"By kind:                {dict(kind_counts)}")
    print(f"By category:            {dict(cat_counts)}")
    print(f"Reports:                {REPORTS}")
    if emit_batch:
        print(f"Batch JSON:             {batch_path} ({len(batch)} keys)")
    if missing_ui:
        print("\nSample missing UI keys:")
        for row in missing_ui[:20]:
            preview = row["key"].replace("\n", "\\n")[:80]
            print(f"  - {preview}")
    return report


def split_into_batches(
    batch_json: Path,
    *,
    out_dir: Path,
    chunk_size: int,
    start_index: int,
) -> list[Path]:
    data = json.loads(batch_json.read_text(encoding="utf-8"))
    keys = sorted(data.keys())
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(0, len(keys), chunk_size):
        chunk = {k: "" for k in keys[i : i + chunk_size]}
        idx = start_index + (i // chunk_size)
        path = out_dir / f"batch-{idx:03d}-th.json"
        path.write_text(json.dumps(chunk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    print(f"Wrote {len(paths)} batches ({len(keys)} keys, size={chunk_size}) → {out_dir}")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-batch", action="store_true", help="Do not write missing-all-th-batch.json")
    parser.add_argument(
        "--batch-out",
        type=Path,
        default=None,
        help="Path for combined empty-value batch JSON",
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help="Also split missing UI keys into tools/i18n/batches/th/batch-NNN-th.json",
    )
    parser.add_argument("--chunk-size", type=int, default=60, help="Keys per split batch (default 60)")
    parser.add_argument("--start-index", type=int, default=100, help="First batch number for --split (default 100)")
    args = parser.parse_args(argv)

    report = build_report(emit_batch=not args.no_batch, batch_out=args.batch_out)
    if args.split and report.missing_ui:
        batch_path = args.batch_out or (REPORTS / "missing-all-th-batch.json")
        split_into_batches(
            batch_path,
            out_dir=REPO / "tools" / "i18n" / "batches" / "th",
            chunk_size=args.chunk_size,
            start_index=args.start_index,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
