#!/usr/bin/env python3
"""Build batch-014-th.json with UI strings missing from th.json."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "i18n"))
from scan_missing import (  # noqa: E402
    XAML_ATTR_PATTERN,
    contains_cjk,
    looks_like_translatable_ui,
    normalize_text,
)

TH_PATH = REPO / "BetterGenshinImpact/User/I18n/th.json"
EN_PATH = REPO / "BetterGenshinImpact/User/I18n/en.json"
OUT_PATH = REPO / "tools/i18n/batches/th/batch-014-th.json"

CS_UI_PREFIXES = (
    "BetterGenshinImpact/View/",
    "BetterGenshinImpact/ViewModel/",
    "BetterGenshinImpact/Model/",
    "BetterGenshinImpact/Service/Notifier/",
    "BetterGenshinImpact/Service/Notification/",
)
CS_RE = re.compile(r'"((?:\\.|[^"\\])*)"')


def main() -> int:
    th = json.loads(TH_PATH.read_text(encoding="utf-8"))
    en = json.loads(EN_PATH.read_text(encoding="utf-8"))
    batch: dict[str, str] = {}

    def add(key: str) -> None:
        key = normalize_text(key).strip()
        if not key or key in th:
            return
        if not contains_cjk(key):
            return
        if re.search(r"\{[^0-9]", key):
            return
        if not looks_like_translatable_ui(key):
            return
        batch[key] = ""

    for k in en:
        add(k)

    for xaml in (REPO / "BetterGenshinImpact").rglob("*.xaml"):
        if "bin" in xaml.parts or "obj" in xaml.parts:
            continue
        rel = str(xaml.relative_to(REPO)).replace("\\", "/")
        if not rel.startswith("BetterGenshinImpact/View/"):
            continue
        text = xaml.read_text(encoding="utf-8-sig", errors="replace")
        for line in text.splitlines():
            if "{Binding" in line or "{StaticResource" in line or "{DynamicResource" in line:
                continue
            stripped = line.strip()
            # Plain TextBlock / Hyperlink element content (not attributes)
            if (
                stripped
                and "<" not in stripped
                and ">" not in stripped
                and "=" not in stripped
                and not stripped.startswith("<!--")
            ):
                add(stripped)

    for cs in (REPO / "BetterGenshinImpact").rglob("*.cs"):
        if "bin" in cs.parts or "obj" in cs.parts:
            continue
        rel = str(cs.relative_to(REPO)).replace("\\", "/")
        if not rel.startswith(CS_UI_PREFIXES):
            continue
        content = cs.read_text(encoding="utf-8-sig", errors="replace")
        for line in content.splitlines():
            if line.strip().startswith("//"):
                continue
            if "LocalizedString" in line or "ResourceManager" in line or "LogInformation" in line or "LogError" in line or "LogWarning" in line:
                continue
            for m in CS_RE.finditer(line):
                add(m.group(1))

    for k in list(batch):
        if k.endswith(" -"):
            add(k + " ")
        if k.endswith(" - "):
            add(k.rstrip())

    batch = dict(sorted(batch.items()))
    OUT_PATH.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(batch)} keys to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
