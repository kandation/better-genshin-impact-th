#!/usr/bin/env python3
"""Merge high-priority log/status Thai keys into th.json without overwriting."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TH = REPO / "BetterGenshinImpact" / "User" / "I18n" / "th.json"
DONE = REPO / "tools" / "i18n" / "batches" / "th" / "done"

PRIORITY: dict[str, str] = {
    "拾取": "เก็บ",
    "剧情": "บท",
    "邀约": "นัด",
    "传送": "วาร์ป",
    "钓鱼": "ตกปลา",
    "\uf256 拾取": "\uf256 เก็บ",
    "\uf075 剧情": "\uf075 บท",
    "\ue5c8 邀约": "\ue5c8 นัด",
    "\uf578 钓鱼": "\uf578 ตกปลา",
    "\uf3c5 传送": "\uf3c5 วาร์ป",
    "→ 任务启动！": "→ เริ่มงาน!",
    "→ 任务结束": "→ จบงาน",
    "→任务启动!": "→เริ่มงาน!",
    "→任务结束": "→จบงาน",
    "开始自动演奏整个专辑未完成的音乐": "เริ่มเล่นเพลงที่ยังไม่จบทั้งอัลบั้มอัตโนมัติ",
    "自动音乐专辑任务异常:{Msg}": "งานอัลบั้มเพลงอัตโนมัติผิดปกติ:{Msg}",
    "自动音乐专辑任务异常详情": "รายละเอียดงานอัลบั้มเพลงอัตโนมัติผิดปกติ",
    "当前未处于主题专辑界面，请在专辑界面运行本任务。注意全部歌曲列表页面无法运行本任务！": (
        "ขณะนี้ไม่ได้อยู่หน้าอัลบั้มธีม กรุณารันงานนี้ในหน้าอัลบั้ม "
        "หน้า list เพลงทั้งหมดรันงานนี้ไม่ได้!"
    ),
    "开始自动演奏": "เริ่มเล่นอัตโนมัติ",
    "{Name}：回到游戏主界面时记得关闭自动音游任务！": (
        "{Name}: กลับหน้าหลักเกมแล้วอย่าลืมปิดงาน rhythm game อัตโนมัติ!"
    ),
    "{Name}：默认的样式“轻漾涟漪”是{No}的！需要手动完成几首曲目获得{Money}千音币后兑换并使用胡桃样式“{Hutao}”！": (
        '{Name}: สไตล์เริ่มต้น "Light Ripple" {No}! '
        "ต้องเล่นจบเพลงด้วยตนเองเพื่อได้ {Money} Repertoire Coin "
        'แล้วแลกใช้สไตล์ Hu Tao "{Hutao}"!'
    ),
    "千音雅集": "Repertoire of Harmonic Sounds",
    "不可用": "ใช้ไม่ได้",
    "疏影引蝶映梅红": "Plum Blossom in Shadow",
    "轻漾涟漪": "Light Ripple",
    "暂停自动拾取拾取:{Count}": "หยุดเก็บอัตโนมัติชั่วคราว:{Count}",
    "{Seconds}秒后恢复自动拾取:{Count}": "จะกลับมาเก็บอัตโนมัติใน {Seconds} วินาที:{Count}",
    "恢复自动拾取:{Count}": "กลับมาเก็บอัตโนมัติ:{Count}",
    "→ {Text}": "→ {Text}",
    "任务启动！": "เริ่มงาน!",
    "任务结束": "จบงาน",
}


def main() -> None:
    DONE.mkdir(parents=True, exist_ok=True)
    frag = DONE / "batch-000-log-priority-th.json"
    frag.write_text(json.dumps(PRIORITY, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    th: dict[str, str] = json.loads(TH.read_text(encoding="utf-8"))
    before = len(th)
    added = 0
    for k, v in PRIORITY.items():
        if k not in th or not str(th.get(k, "")).strip():
            th[k] = v
            added += 1

    TH.write_text(json.dumps(th, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"priority fragment: {len(PRIORITY)} keys -> {frag}")
    print(f"th.json {before} -> {len(th)} (added {added})")
    for k in [
        "拾取",
        "剧情",
        "→ 任务启动！",
        "开始自动演奏整个专辑未完成的音乐",
        "千音雅集",
        "\uf256 拾取",
    ]:
        print(f"  {k!r} => {th.get(k)!r}")


if __name__ == "__main__":
    main()
