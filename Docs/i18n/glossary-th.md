# Glossary ภาษาไทย · Genshin / BetterGI

> **กฎชื่อเฉพาะ (Proper names):** แผนที่ / region, ตัวละคร, ชนิดปลา — ใช้ **ชื่อภาษาอังกฤษ official** (Fontaine, Liyue, Jean, Medaka ฯลฯ) **ห้าม** แปลเป็นภาษาไทยหรือทับศัพท์ (เช่น ฟอนเตน, ลิเยว่, มอนด์สตัด) และ **ห้าม** ปล่อยชื่อจีนใน value (璃月, 蒙德)

เอกสารนี้เป็น **template ที่เติมได้** — เมื่อตัดสินใจศัพท์ใหม่ ให้เพิ่มแถวและอ้างอิงใน PR

แหล่งอ้างอิงหลัก:

- [Genshin Impact Wiki (Thai)](https://genshin-impact.fandom.com/th/)
- Client เกมภาษาไทย (in-game UI)
- [bettergi-i18n en.json](https://github.com/babalae/bettergi-i18n) — บริบทความหมาย (ไม่ copy มาทั้งก้อน)

---

## วิธีใช้

1. ก่อนแปล batch — ค้น glossary ว่ามีศัพท์นั้นหรือยัง
2. ถ้า Wiki TH กับ client ไม่ตรง — **เลือก client** สำหรับ OCR string; **เลือก Wiki/client ที่ผู้เล่นรู้จัก** สำหรับ UI ทั่วไป
3. เพิ่มแถวใหม่พร้อม `หมายเหตุ` ว่าอ้างอิงจากไหน

---

## Regions / แผนที่ (English display names)

| 中文 | English display name | หมายเหตุ |
|------|----------------------|----------|
| 蒙德 | Mondstadt | ห้ามทับศัพท์ไทย |
| 璃月 | Liyue | |
| 稻妻 | Inazuma | |
| 须弥 | Sumeru | |
| 枫丹 | Fontaine | |
| 纳塔 | Natlan | |
| 至冬 | Snezhnaya | |
| 挪德卡莱 | Nod-Krai | |

> **หมายเหตุ:** value ใน `th.json` และ `*.th.resx` ต้องเป็นชื่อ EN ด้านบน — ไม่ใช่ภาษาไทย ไม่ใช่จีน

---

## ระบบเกม (UI ทั่วไป)

| 中文 / EN | ไทย (แนะนำ) | หมายเหตุ |
|-----------|-------------|----------|
| 原石 | อัญมณีพราย | Primogem — ตรวจ client |
| 纠缠之缘 | อัญมณีพราย (Intertwined Fate) | ตรวจ client |
| 相遇之缘 | อัญมณีแห่งการพบ (Acquaint Fate) | ตรวจ client |
| 圣遗物 | อาร์ติแฟกต์ | Artifact |
| 秘境 | ดันเจี้ยน | Domain |
| 委托 | เควสว่าจ้าง | Commissions |
| 每日 | รายวัน | Daily |
| 合成 | สังเคราะห์ | Crafting — batch 003 |
| 委托 | เควสว่าจ้าง | Commissions — batch 005 |
| 元素战技 | สกิลธาตุ | Elemental Skill — batch 003 |
| 元素爆发 | ท่าไม้ตาย | Elemental Burst — batch 003 |
| 凯瑟琳 | Katherine | Adventurers' Guild — batch 003 |
| 地脉花 | Ley Line Outcrop | Ley line farming — batch 004 |
| 启示之花 | Blossom of Wealth | Ley line type — batch 004 |
| 壶灵 | Teapot Spirit | Serenitea Pot NPC — batch 005 |
| 尘歌壶 | กระถางแห่งควันและหยาดน้ำ | Serenitea Pot |
| 七天神像 | รูปปั้นเจ็ดบูรพา | Statue of The Seven — ตรวจ client |
| 浓缩树脂 | Condensed Resin | ใช้ชื่อ EN ใน UI |
| 原粹树脂 | Original Resin | ใช้ชื่อ EN ใน UI |
| 脆弱树脂 | Fragile Resin | ใช้ชื่อ EN ใน UI |
| 须臾树脂 | Transient Resin | ใช้ชื่อ EN ใน UI |

---

## ตกปลา / Fishing

| 中文 / EN | ไทย (แนะนำ) | หมายเหตุ |
|-----------|-------------|----------|
| 钓鱼 | ตกปลา | UI ทั่วไป — OCR ใน `.resx` ต้องตรง client ไทย |
| 上钩 | ปลากัดเหยื่อ | UI label — OCR resx อาจเป็น "ปลาติดเบ็ดแล้วล่ะ" ต้องตรวจ in-game |
| 上钩等待超时时间 | หมดเวลารอปลากัดเหยื่อ | การตั้งค่า BetterGI |
| 抛竿 / 收杆 | เหวี่ยงเบ็ด / ดึงเบ็ด | UI ทั่วไป |
| Medaka, Crystalfish 等 | _(keep English)_ | ชื่อปลา — ไม่แปลเป็นภาษาไทย |

---

## BetterGI-specific (เครื่องมือ)

| 中文 | ไทย (แนะนำ) | หมายเหตุ |
|------|-------------|----------|
| 一条龙 | งานรายวันครบชุด | One-Click Daily — batch 001–002 |
| 自动 | อัตโนมัติ | auto- prefix |
| 设置 | การตั้งค่า | Settings |
| 启动 | เริ่ม / เปิดใช้งาน | context-dependent |
| 识别 | จดจำ / การจดจำ | OCR context → อาจใช้ "จดจำภาพ" |

---

## ตัวละคร (ตัวอย่าง — เติมต่อ)

| EN | 中文 | Display in Thai UI | หมายเหตุ |
|----|------|--------------------|----------|
| Nahida | 纳西妲 | Nahida | ใช้ชื่อ EN community |
| Neuvillette | 那维莱特 | Neuvillette | |
| Jean | 琴 | Jean | |
| Kazuha | 万叶 | Kazuha | |
| Katherine | 凯瑟琳 | Katherine | Adventurers' Guild |

---

## OCR — ห้าม paraphrase

String ใน `tools/i18n/reports/ocr-related-th.csv` ต้อง **ตรงกับข้อความบนหน้าจอ** ไม่ใช่คำใน glossary ด้านบนเสมอไป

บันทึกคู่ `(key จีน, ข้อความบนจอไทย, screenshot path)` ใน PR เมื่อเป็นไปได้

---

## Changelog glossary

<!-- เพิ่มแถวใหม่ด้านล่าง พร้อมวันที่และ PR -->

| วันที่ | ศัพท์ | การตัดสินใจ | PR/Issue |
|--------|-------|-------------|----------|
| 2026-07-23 | 七天神像, 钓鱼 UI, 上钩 | batch 001–002; OCR resx ยังรอตรวจ client | i18n-th |
| 2026-07-23 | 元素战技, 元素爆发, 委托, 凯瑟琳 | batch 003–005; สกิลธาตุ/ท่าไม้ตาย/เควสว่าจ้าง/Katherine | i18n-th |
| 2026-07-23 | 地脉花, 启示之花, 壶灵 | Ley Line Outcrop, Blossom of Wealth, Teapot Spirit (EN names) | i18n-th |
| 2026-07-23 | Regions, characters, fish | Proper names = English only; no Thai transliteration | i18n-th |
| 2026-07-23 | batch 006–012 | UI batch complete; 1676/1676 JSON keys; whitespace variants in batch-013 | i18n-th |
| 2026-07-23 | 史莱姆凝液, 精致的宝箱, 洞天百宝 | Slime Condensate, Exquisite Chest, Realm Depot (EN item names) | batch 008–009 |
| 2026-07-23 | 阿圆, 空荧酒馆, 千星奇域 | Tubby, Seelie Map, Simulanka (EN display names) | batch 009–011 |
| 2026-07-23 | 蓝花/黄花/藏金之花 | Blossom of Revelation/Wealth (EXP/Mora ley lines) | batch 009/012 |
| 2026-07-23 | 自动千音雅集, 自动幽境危战 | Repertoire of Harmonic Sounds, Spiral Abyss: Domain of Conflict | batch 009 |
