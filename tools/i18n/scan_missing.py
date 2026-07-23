#!/usr/bin/env python3
"""Scan BetterGI for untranslated / missing i18n strings.

Finds hardcoded UI strings in source and compares them against JSON UI
translations (BetterGenshinImpact/User/I18n/{locale}.json) and .resx
game-task resources.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Mirrors AutoTranslateInterceptor.ShouldTranslatePropertyName (View/Behavior)
XAML_ATTR_PATTERN = re.compile(
    r'(?P<attr>(?:\w+:)?(?:Text|Content|Header|ToolTip|Title|Subtitle|'
    r'Description|PlaceholderText|Label|Caption))\s*=\s*"(?P<value>[^"]*)"',
    re.IGNORECASE,
)

XAML_RUN_PATTERN = re.compile(
    r'<(?:\w+:)?Run\s+[^>]*Text="(?P<value>[^"]*)"',
    re.IGNORECASE,
)

CS_STRING_PATTERN = re.compile(
    r'(?P<prefix>@)?"(?P<value>(?:\\.|[^"\\])*)"',
    re.MULTILINE,
)

RESX_DATA_PATTERN = re.compile(
    r'<data\s+name="(?P<name>[^"]+)"[^>]*>\s*<value>(?P<value>.*?)</value>',
    re.DOTALL,
)

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".github",
    "bin",
    "obj",
    "node_modules",
    "packages",
    "Fischless.WindowsInput",
    "BetterGenshinImpact.Test",
    "BetterGenshinImpact.UnitTest",
}

DEFAULT_EXCLUDE_GLOBS = {
    "**/Assets/**/*.json",  # pathing / recognition game data, not UI copy
    "**/User/Script/**",
    "**/User/Js/**",
    "**/User/log/**",
    "**/User/I18n/missing.*.json",
}

OCR_PATH_HINTS = (
    "ocr",
    "paddle",
    "recognition",
    "recognize",
    "recognise",
    "artifact",
    "resx",
    "gametask",
    "bvision",
    "bvresx",
)

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")
WHITESPACE_ONLY_RE = re.compile(r"^\s*$")
URL_RE = re.compile(r"^https?://", re.I)
BINDING_RE = re.compile(r"\{Binding|\{StaticResource|\{DynamicResource|\{x:", re.I)
XAML_ENTITY_RE = re.compile(r"&#x?[0-9a-fA-F]+;")
# Likely code/log/regex — not UI copy
NON_UI_TEXT_RE = re.compile(
    r"(?="
    r".*(?:\\n|\\r|\\t|\{0\}|\{1\}|<td|<div|<pre|</|\(\?|===|\+\+|"
    r"string\.Join|ConcatenateStrings|onclick=|colspan|"
    r"[\[\]\\]|\.cs:|Exception|LogError|Debug\.|"
    r"^\s*$)"
    r")",
    re.DOTALL,
)

CS_UI_PATH_PREFIXES = (
    "BetterGenshinImpact/View/",
    "BetterGenshinImpact/ViewModel/",
)

WITH_CULTURE_GET_RE = re.compile(
    r'WithCultureGet\s*\([^,]+,\s*"((?:\\.|[^"\\])*)"',
)
THEMED_MSG_RE = re.compile(
    r'ThemedMessageBox\.\w+\s*\(\s*"((?:\\.|[^"\\])*)"',
)


@dataclass
class StringHit:
    text: str
    file: str
    line: int
    kind: str  # xaml | cs | resx-base
    property: str = ""
    ocr_related: bool = False
    notes: str = ""


@dataclass
class ResxGap:
    resx_base: str
    key: str
    base_value: str
    target_file: str
    target_value: str
    reason: str  # missing-file | missing-key | empty-value | untranslated


@dataclass
class Report:
    generated_at: str
    repo_root: str
    target_locale: str
    summary: dict
    missing_json_keys: list[dict]
    empty_json_values: list[dict]
    stale_json_keys: list[dict]
    resx_gaps: list[dict]
    hardcoded_not_in_json: list[dict]
    ocr_related: list[dict]
    samples: dict = field(default_factory=dict)


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def looks_like_ui_english(text: str) -> bool:
    if not ASCII_LETTER_RE.search(text):
        return False
    if URL_RE.match(text):
        return False
    if BINDING_RE.search(text):
        return False
    if re.fullmatch(r"[A-Za-z0-9_.\-/\\]+", text):
        return False
    if len(text.strip()) < 2:
        return False
    return True


def looks_like_translatable_ui(text: str) -> bool:
    if WHITESPACE_ONLY_RE.match(text):
        return False
    if len(text) > 300:
        return False
    if not contains_cjk(text):
        return looks_like_ui_english(text)
    if NON_UI_TEXT_RE.search(text):
        return False
    if text.count("\n") > 2:
        return False
    return True


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
    return decode_xaml_entities(text).replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")


def is_ocr_related(path: str, text: str, kind: str) -> bool:
    lower = path.replace("\\", "/").lower()
    if any(h in lower for h in OCR_PATH_HINTS):
        return True
    if kind == "resx-base":
        return True
    ocr_terms = ("ocr", "paddle", "识别", "文字识别", "截图")
    return any(t in text.lower() or t in text for t in ocr_terms)


def should_skip_path(path: Path, exclude_dirs: set[str], exclude_globs: list[str]) -> bool:
    parts = set(path.parts)
    if parts & exclude_dirs:
        return True
    path_posix = path.as_posix()
    for pattern in exclude_globs:
        if path.match(pattern):
            return True
    return False


def iter_source_files(root: Path, extensions: Iterable[str], exclude_dirs: set[str], exclude_globs: list[str]) -> Iterable[Path]:
    for ext in extensions:
        for path in root.rglob(f"*{ext}"):
            if should_skip_path(path.relative_to(root), exclude_dirs, exclude_globs):
                continue
            yield path


def strip_csharp_comments(content: str) -> str:
    # Remove // line comments and /* */ block comments (best-effort for string scanning)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
    return content


def scan_xaml(path: Path, repo_root: Path) -> list[StringHit]:
    hits: list[StringHit] = []
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/")

    for line_no, line in enumerate(text.splitlines(), start=1):
        if BINDING_RE.search(line):
            continue
        for match in XAML_ATTR_PATTERN.finditer(line):
            value = normalize_text(match.group("value"))
            if not looks_like_translatable_ui(value):
                continue
            hits.append(
                StringHit(
                    text=value,
                    file=rel,
                    line=line_no,
                    kind="xaml",
                    property=match.group("attr"),
                    ocr_related=is_ocr_related(rel, value, "xaml"),
                )
            )
        for match in XAML_RUN_PATTERN.finditer(line):
            value = normalize_text(match.group("value"))
            if not looks_like_translatable_ui(value):
                continue
            hits.append(
                StringHit(
                    text=value,
                    file=rel,
                    line=line_no,
                    kind="xaml",
                    property="Run.Text",
                    ocr_related=is_ocr_related(rel, value, "xaml"),
                )
            )
    return hits


def scan_cs(path: Path, repo_root: Path, include_english: bool) -> list[StringHit]:
    hits: list[StringHit] = []
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    content = strip_csharp_comments(raw)
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    is_ui_path = rel.startswith(CS_UI_PATH_PREFIXES)

    def add_hit(value: str, line_no: int, prop: str, notes: str = "") -> None:
        value = normalize_text(value)
        if not looks_like_translatable_ui(value):
            return
        if not include_english and not contains_cjk(value):
            return
        hits.append(
            StringHit(
                text=value,
                file=rel,
                line=line_no,
                kind="cs",
                property=prop,
                ocr_related=is_ocr_related(rel, value, "cs"),
                notes=notes,
            )
        )

    for line_no, line in enumerate(content.splitlines(), start=1):
        for match in WITH_CULTURE_GET_RE.finditer(line):
            add_hit(match.group(1), line_no, "WithCultureGet")
        for match in THEMED_MSG_RE.finditer(line):
            add_hit(match.group(1), line_no, "ThemedMessageBox")

        if not is_ui_path:
            continue

        if "LocalizedString" in line or "ResourceManager" in line:
            continue
        for match in CS_STRING_PATTERN.finditer(line):
            add_hit(match.group("value"), line_no, "string-literal", "english-ui" if not contains_cjk(match.group("value")) else "")

    return hits


def parse_resx(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    entries: dict[str, str] = {}
    for match in RESX_DATA_PATTERN.finditer(text):
        name = match.group("name")
        if name in {"Name1", "Color1", "Bitmap1", "Icon1"}:
            continue
        value = match.group("value").strip()
        entries[name] = value
    return entries


def scan_resx_gaps(repo_root: Path, target_locale: str) -> tuple[list[StringHit], list[ResxGap]]:
    base_hits: list[StringHit] = []
    gaps: list[ResxGap] = []

    for base_file in sorted(repo_root.rglob("*.zh-Hans.resx")):
        rel_base = str(base_file.relative_to(repo_root)).replace("\\", "/")
        stem = base_file.name[: -len(".zh-Hans.resx")]
        target_file = base_file.with_name(f"{stem}.{target_locale}.resx")
        base_entries = parse_resx(base_file)

        for key, base_value in sorted(base_entries.items()):
            base_hits.append(
                StringHit(
                    text=key,
                    file=rel_base,
                    line=0,
                    kind="resx-base",
                    property=key,
                    ocr_related=True,
                    notes=base_value,
                )
            )

        if not target_file.exists():
            for key, base_value in base_entries.items():
                gaps.append(
                    ResxGap(
                        resx_base=rel_base,
                        key=key,
                        base_value=base_value,
                        target_file=str(target_file.relative_to(repo_root)).replace("\\", "/"),
                        target_value="",
                        reason="missing-file",
                    )
                )
            continue

        target_entries = parse_resx(target_file)
        rel_target = str(target_file.relative_to(repo_root)).replace("\\", "/")
        for key, base_value in base_entries.items():
            if key not in target_entries:
                gaps.append(
                    ResxGap(
                        resx_base=rel_base,
                        key=key,
                        base_value=base_value,
                        target_file=rel_target,
                        target_value="",
                        reason="missing-key",
                    )
                )
                continue
            target_value = target_entries[key]
            if not target_value.strip():
                reason = "empty-value"
            elif target_value == base_value and contains_cjk(base_value):
                reason = "untranslated"
            else:
                continue
            gaps.append(
                ResxGap(
                    resx_base=rel_base,
                    key=key,
                    base_value=base_value,
                    target_file=rel_target,
                    target_value=target_value,
                    reason=reason,
                )
            )

    return base_hits, gaps


def load_json_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def dedupe_hits(hits: Iterable[StringHit]) -> list[StringHit]:
    seen: set[tuple[str, str, int, str]] = set()
    out: list[StringHit] = []
    for hit in hits:
        key = (hit.text, hit.file, hit.line, hit.kind)
        if key in seen:
            continue
        seen.add(key)
        out.append(hit)
    return out


def build_report(
    repo_root: Path,
    target_locale: str,
    include_english: bool,
    exclude_dirs: set[str],
    exclude_globs: list[str],
) -> Report:
    app_root = repo_root / "BetterGenshinImpact"
    i18n_path = app_root / "User" / "I18n" / f"{target_locale}.json"

    xaml_hits: list[StringHit] = []
    cs_hits: list[StringHit] = []

    for path in iter_source_files(app_root, [".xaml"], exclude_dirs, exclude_globs):
        xaml_hits.extend(scan_xaml(path, repo_root))

    for path in iter_source_files(app_root, [".cs"], exclude_dirs, exclude_globs):
        cs_hits.extend(scan_cs(path, repo_root, include_english))

    resx_hits, resx_gaps = scan_resx_gaps(repo_root, target_locale)

    all_hits = dedupe_hits([*xaml_hits, *cs_hits, *resx_hits])
    ui_hits = [h for h in all_hits if looks_like_translatable_ui(h.text)]

    translation_map = load_json_map(i18n_path)
    translation_keys = set(translation_map.keys())

    source_strings = {h.text for h in ui_hits if h.kind != "resx-base"}
    resx_keys = {h.text for h in resx_hits}

    missing_json = sorted(k for k in (source_strings - translation_keys) if looks_like_translatable_ui(k))
    empty_json = sorted(k for k, v in translation_map.items() if not v.strip())
    stale_json = sorted(translation_keys - source_strings - resx_keys)

    hardcoded_rows = []
    for hit in ui_hits:
        if hit.kind == "resx-base":
            continue
        if hit.text in translation_keys:
            continue
        hardcoded_rows.append(asdict(hit))

    missing_json_rows = [{"key": k} for k in missing_json]
    empty_json_rows = [{"key": k, "value": translation_map[k]} for k in empty_json]
    stale_json_rows = [{"key": k, "value": translation_map[k]} for k in stale_json[:200]]
    resx_gap_rows = [asdict(g) for g in resx_gaps]
    ocr_rows = [asdict(h) for h in ui_hits if h.ocr_related and h.kind != "resx-base" and h.text not in translation_keys]

    summary = {
        "target_locale": target_locale,
        "translation_file": str(i18n_path.relative_to(repo_root)).replace("\\", "/"),
        "translation_file_exists": i18n_path.exists(),
        "translation_keys_total": len(translation_keys),
        "xaml_cjk_hits": len([h for h in xaml_hits if looks_like_translatable_ui(h.text)]),
        "cs_ui_hits": len([h for h in cs_hits if looks_like_translatable_ui(h.text)]),
        "unique_ui_source_strings": len(source_strings),
        "missing_json_keys": len(missing_json),
        "empty_json_values": len(empty_json),
        "stale_json_keys": len(stale_json),
        "resx_base_keys": len(resx_keys),
        "resx_gaps": len(resx_gaps),
        "ocr_related_untranslated": len(ocr_rows),
        "hardcoded_not_in_json": len(hardcoded_rows),
    }

    return Report(
        generated_at=datetime.now(timezone.utc).isoformat(),
        repo_root=str(repo_root),
        target_locale=target_locale,
        summary=summary,
        missing_json_keys=missing_json_rows,
        empty_json_values=empty_json_rows,
        stale_json_keys=stale_json_rows,
        resx_gaps=resx_gap_rows,
        hardcoded_not_in_json=hardcoded_rows,
        ocr_related=ocr_rows,
        samples={
            "missing_json_keys": missing_json[:15],
            "resx_gaps": [asdict(g) for g in resx_gaps[:10]],
            "hardcoded_not_in_json": hardcoded_rows[:10],
        },
    )


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_outputs(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    locale = report.target_locale

    json_path = output_dir / f"missing-{locale}.json"
    json_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")

    write_csv(
        output_dir / f"missing-json-keys-{locale}.csv",
        report.missing_json_keys,
        ["key"],
    )
    write_csv(
        output_dir / f"hardcoded-not-in-json-{locale}.csv",
        report.hardcoded_not_in_json,
        ["text", "file", "line", "kind", "property", "ocr_related", "notes"],
    )
    write_csv(
        output_dir / f"resx-gaps-{locale}.csv",
        report.resx_gaps,
        ["resx_base", "key", "base_value", "target_file", "target_value", "reason"],
    )
    write_csv(
        output_dir / f"ocr-related-{locale}.csv",
        report.ocr_related,
        ["text", "file", "line", "kind", "property", "ocr_related", "notes"],
    )


def print_summary(report: Report) -> None:
    s = report.summary
    print(f"Target locale: {s['target_locale']}")
    print(f"Translation file: {s['translation_file']} (exists={s['translation_file_exists']})")
    print(f"Translation keys in file: {s['translation_keys_total']}")
    print(f"Unique UI source strings scanned: {s.get('unique_ui_source_strings', s.get('unique_cjk_source_strings'))}")
    print(f"Missing JSON keys: {s['missing_json_keys']}")
    print(f"Empty JSON values: {s['empty_json_values']}")
    print(f"Stale JSON keys (in file, not found in scan): {s['stale_json_keys']}")
    print(f"Resx gaps for .{s['target_locale']}.resx: {s['resx_gaps']}")
    print(f"OCR-related untranslated hits: {s['ocr_related_untranslated']}")
    if report.samples.get("missing_json_keys"):
        print("\nSample missing JSON keys:")
        for key in report.samples["missing_json_keys"]:
            print(f"  - {key}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan BetterGI for missing i18n strings.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--target-locale",
        default="en",
        help="Target locale code matching User/I18n/{locale}.json and *.resx files (e.g. en, ja, th)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: tools/i18n/reports)",
    )
    parser.add_argument(
        "--include-english",
        action="store_true",
        help="Also collect likely UI English string literals from .cs files",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Extra directory name to exclude (repeatable)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir or (Path(__file__).resolve().parent / "reports")

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir or [])
    exclude_globs = list(DEFAULT_EXCLUDE_GLOBS)

    report = build_report(
        repo_root=repo_root,
        target_locale=args.target_locale,
        include_english=args.include_english,
        exclude_dirs=exclude_dirs,
        exclude_globs=exclude_globs,
    )
    write_outputs(report, output_dir)
    print_summary(report)
    print(f"\nReports written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
