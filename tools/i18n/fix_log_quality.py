#!/usr/bin/env python3
"""Fix a few known bad/truncated log translations and add new templates from code fixes."""

from __future__ import annotations

import json
from pathlib import Path

TH = Path("BetterGenshinImpact/User/I18n/th.json")
th = json.loads(TH.read_text(encoding="utf-8"))

fixes = {
    "{Name}：默认的样式“轻漾涟漪”是{No}的！需要手动完成几首曲目获得{Money}千音币后兑换并使用胡桃样式“{Hutao}”！": (
        '{Name}: สไตล์เริ่มต้น "Light Ripple" {No}! '
        "ต้องเล่นจบเพลงด้วยตนเองเพื่อได้ {Money} Repertoire Coin "
        'แล้วแลกใช้สไตล์ Hu Tao "{Hutao}"!'
    ),
    "{Name}：回到游戏主界面时记得关闭自动音游任务！": (
        "{Name}: กลับหน้าหลักเกมแล้วอย่าลืมปิดงาน rhythm game อัตโนมัติ!"
    ),
    "轻漾涟漪": "Light Ripple",
    # templates from AutoFight $ → structured fixes
    "战斗人次（{CountFight}）低于配置人次（{Threshold}），跳过此次拾取！": (
        "จำนวนครั้งต่อสู้ ({CountFight}) ต่ำกว่าเกณฑ์ ({Threshold}) ข้ามการเก็บครั้งนี้!"
    ),
    "切换为拾取队伍：{PartyName}": "สลับเป็นทีมเก็บของ: {PartyName}",
    "成功切换队伍为{PartyName}": "สลับทีมเป็น {PartyName} สำเร็จ",
    "切换为原队伍：{PartyName}": "สลับกลับทีมเดิม: {PartyName}",
    "切换为原队伍{PartyName}": "สลับกลับทีมเดิม{PartyName}",
    "未识别到战斗结束: yellow{Y0},{Y1},{Y2};white{W0},{W1},{W2}": (
        "จดจำจบการต่อสู้ไม่พบ: yellow{Y0},{Y1},{Y2};white{W0},{W1},{W2}"
    ),
}

for k, v in fixes.items():
    th[k] = v

TH.write_text(json.dumps(th, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("fixed", len(fixes), "keys; total", len(th))
