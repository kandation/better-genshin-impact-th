#!/usr/bin/env python3
"""Find UI strings in source that are missing from th.json (includes XAML element content)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TH_PATH = REPO / "BetterGenshinImpact/User/I18n/th.json"
EN_PATH = REPO / "BetterGenshinImpact/User/I18n/en.json"

XAML_CONTENT_RE = re.compile(r">([^<>{}\n]+)<")
ATTR_RE = re.compile(
    r"(?:Text|Content|Header|ToolTip|Title|Subtitle|Description|PlaceholderText|Label|Caption)\s*=\s*\"([^\"]*)\"",
    re.I,
)
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CS_RE = re.compile(r"\"((?:\\.|[^\"\\])*)\"")
CS_UI_PREFIXES = (
    "BetterGenshinImpact/View/",
    "BetterGenshinImpact/ViewModel/",
    "BetterGenshinImpact/Model/",
    "BetterGenshinImpact/Service/",
    "BetterGenshinImpact/Core/Config/",
)


def main() -> int:
    th: dict[str, str] = json.loads(TH_PATH.read_text(encoding="utf-8"))
    missing: dict[str, str] = {}

    for xaml in (REPO / "BetterGenshinImpact").rglob("*.xaml"):
        if "bin" in xaml.parts or "obj" in xaml.parts:
            continue
        rel = str(xaml.relative_to(REPO)).replace("\\", "/")
        text = xaml.read_text(encoding="utf-8-sig", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if "{Binding" in line or "{StaticResource" in line or "{DynamicResource" in line:
                continue
            for m in ATTR_RE.finditer(line):
                v = m.group(1).strip()
                if CJK_RE.search(v) and v not in th:
                    missing[v] = f"{rel}:{i}:attr"
            for m in XAML_CONTENT_RE.finditer(line):
                v = m.group(1).strip()
                if not v or not CJK_RE.search(v):
                    continue
                if v.startswith("<!--"):
                    continue
                if v not in th:
                    missing[v] = f"{rel}:{i}:content"

    for cs in (REPO / "BetterGenshinImpact").rglob("*.cs"):
        if "bin" in cs.parts or "obj" in cs.parts:
            continue
        rel = str(cs.relative_to(REPO)).replace("\\", "/")
        if not rel.startswith(CS_UI_PREFIXES):
            continue
        for i, line in enumerate(cs.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
            if "LocalizedString" in line or "ResourceManager" in line or line.strip().startswith("//"):
                continue
            for m in CS_RE.finditer(line):
                v = m.group(1).replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
                if not CJK_RE.search(v) or len(v) > 300:
                    continue
                if v not in th:
                    missing[v] = f"{rel}:{i}:cs"

    if EN_PATH.exists():
        en = json.loads(EN_PATH.read_text(encoding="utf-8"))
        for k in en:
            if k not in th and k not in missing:
                missing[k] = "en.json only"

    out = REPO / "tools/i18n/reports/missing-from-th-comprehensive.json"
    out.write_text(
        json.dumps({"count": len(missing), "keys": sorted(missing.keys()), "sources": missing}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Missing from th.json: {len(missing)}")
    print(f"Report: {out}")
    for k in sorted(missing.keys()):
        print(k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
