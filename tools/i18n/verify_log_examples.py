#!/usr/bin/env python3
import json
from pathlib import Path

th = json.loads(Path("BetterGenshinImpact/User/I18n/th.json").read_text(encoding="utf-8"))
checks = [
    "自动音乐专辑任务异常:{Msg}",
    "当前未处于主题专辑界面，请在专辑界面运行本任务。注意全部歌曲列表页面无法运行本任务！",
    "{Name}：回到游戏主界面时记得关闭自动音游任务！",
    "{Name}：默认的样式“轻漾涟漪”是{No}的！需要手动完成几首曲目获得{Money}千音币后兑换并使用胡桃样式“{Hutao}”！",
    "千音雅集",
    "不可用",
    "疏影引蝶映梅红",
    "→ 任务启动！",
    "→ 任务结束",
    "\uf256 拾取",
    "\uf075 剧情",
    "\ue5c8 邀约",
    "\uf578 钓鱼",
    "\uf3c5 传送",
]
for k in checks:
    v = th.get(k, "")
    print(("OK" if str(v).strip() else "MISS"), repr(k)[:70], "=>", repr(v)[:100])
print("total keys", len(th))
