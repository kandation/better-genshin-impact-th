#!/usr/bin/env python3
"""Scan C# Log* templates and status overlay strings; diff vs th.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "BetterGenshinImpact"
DIRS = ["GameTask", "ViewModel", "View", "Service", "Core", "Helpers"]
CJK = re.compile(r"[\u4e00-\u9fff]")

# Structured logging: LogXxx("template", args...) — exact template is the i18n key
LOG_TEMPLATE = re.compile(
    r'(?:_logger|logger|Logger)\.(?:Log(?:Information|Warning|Error|Debug|Trace|Critical)|Log)'
    r'\s*\(\s*(?:@)?"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

# Interpolated: LogXxx($"...") — cannot match JSON without code fix
LOG_INTERP = re.compile(
    r'(?:_logger|logger|Logger)\.(?:Log(?:Information|Warning|Error|Debug|Trace|Critical)|Log)'
    r'\s*\(\s*\$"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

# Concat: LogXxx("..." +  or LogXxx(xxx + "..."
LOG_CONCAT_HINT = re.compile(
    r'(?:_logger|logger|Logger)\.(?:Log(?:Information|Warning|Error|Debug|Trace|Critical)|Log)'
    r'\s*\([^;]{0,200}\+',
    re.MULTILINE,
)

# StatusItem("… name …")
STATUS_ITEM = re.compile(
    r'new\s+StatusItem\s*\(\s*"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

# Common Notify / LogInformation-style Chinese string literals near task start/end
NOTIFY_SUCCESS = re.compile(
    r'\.(?:Success|Warning|Error|Info)\s*\(\s*"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)


def unescape_csharp(s: str) -> str:
    return (
        s.replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\t", "\t")
        .replace(r"\"", '"')
        .replace(r"\\", "\\")
    )


def scan() -> None:
    templates: dict[str, list[str]] = {}
    interpolated: dict[str, list[str]] = {}
    status: dict[str, list[str]] = {}
    notify: dict[str, list[str]] = {}
    concat_files: list[str] = []

    for d in DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in base.rglob("*.cs"):
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue

            for m in LOG_TEMPLATE.finditer(text):
                s = unescape_csharp(m.group(1))
                if CJK.search(s):
                    templates.setdefault(s, []).append(rel)

            for m in LOG_INTERP.finditer(text):
                s = unescape_csharp(m.group(1))
                if CJK.search(s):
                    interpolated.setdefault(s, []).append(rel)

            for m in STATUS_ITEM.finditer(text):
                s = unescape_csharp(m.group(1))
                # strip icon prefixes like \uf256 space
                if CJK.search(s):
                    status.setdefault(s, []).append(rel)

            for m in NOTIFY_SUCCESS.finditer(text):
                s = unescape_csharp(m.group(1))
                if CJK.search(s):
                    notify.setdefault(s, []).append(rel)

            if LOG_CONCAT_HINT.search(text) and CJK.search(text):
                # crude: only if Log line with + and CJK nearby
                for line in text.splitlines():
                    if (
                        re.search(r"\.(?:Log(?:Information|Warning|Error|Debug|Trace|Critical)|Log)\s*\(", line)
                        and "+" in line
                        and CJK.search(line)
                        and '$"' not in line
                    ):
                        concat_files.append(f"{rel}: {line.strip()[:160]}")

    th_path = ROOT / "User" / "I18n" / "th.json"
    th = json.loads(th_path.read_text(encoding="utf-8"))

    def is_missing(k: str) -> bool:
        return k not in th or not str(th.get(k, "")).strip()

    # Also check status without icon prefix
    status_bare: dict[str, list[str]] = {}
    for k, locs in status.items():
        bare = re.sub(r"^[^\u4e00-\u9fff]+", "", k).strip()
        if bare and bare != k:
            status_bare.setdefault(bare, []).extend(locs)
        status_bare.setdefault(k, []).extend(locs)

    all_keys = set(templates) | set(status_bare) | set(notify)
    missing = sorted(k for k in all_keys if is_missing(k))
    present = sorted(k for k in all_keys if not is_missing(k))

    out_dir = Path(__file__).with_name("reports")
    out_dir.mkdir(exist_ok=True)

    missing_obj = {k: "" for k in missing}
    (out_dir / "missing-log-keys-th.json").write_text(
        json.dumps(missing_obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    meta = {
        "template_cjk_count": len(templates),
        "notify_cjk_count": len(notify),
        "status_cjk_count": len(status_bare),
        "all_unique_keys": len(all_keys),
        "already_translated": len(present),
        "missing": len(missing),
        "interpolated_count": len(interpolated),
        "concat_hint_lines": len(concat_files),
    }
    (out_dir / "missing-log-meta-th.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "log-interpolated-th.json").write_text(
        json.dumps({k: locs for k, locs in interpolated.items()}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "log-concat-hints-th.txt").write_text(
        "\n".join(concat_files) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print("--- user examples ---")
    examples = [
        "开始自动演奏整个专辑未完成的音乐",
        "自动音乐专辑任务异常:当前未处于主题专辑界面,请在专辑界面运行本任务。注意全部歌曲列表页面无法运行本任务!",
        "→任务结束",
        "→任务启动!",
        "千音雅集:回到游戏主界面时记得关闭自动音游任务!",
        "千音雅集:默认的样式“轻漾涟漪”是不可用的!需要手动完成几首曲目获得600千音币后兑换并使用胡桃样式《疏影引蝶映梅红”!",
        "拾取",
        "剧情",
        "邀约",
        "钓鱼",
        "传送",
    ]
    for e in examples:
        v = th.get(e)
        print(f"{'OK' if v and str(v).strip() else 'MISS'} | {e[:70]} | {v}")

    print(f"\nWrote {len(missing)} missing keys -> reports/missing-log-keys-th.json")
    print(f"Interpolated gaps: {len(interpolated)}")


if __name__ == "__main__":
    scan()
