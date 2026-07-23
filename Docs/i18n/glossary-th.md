# Glossary ภาษาไทย · Genshin / BetterGI

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

## Regions / แผนที่ (ทับศัพท์)

| 中文 | ไทย (แนะนำ) | หมายเหตุ |
|------|-------------|----------|
| 蒙德 | มอนด์สตัด | Mondstadt |
| 璃月 | ลิเยว่ | Liyue |
| 稻妻 | _(เติมจาก Wiki TH)_ | Inazuma |
| 须弥 | สุเมรุ | Sumeru |
| 枫丹 | ฟอนเตน | Fontaine |
| 纳塔 | _(เติมจาก Wiki TH)_ | Natlan |
| 至冬 | _(เติมจาก Wiki TH)_ | Snezhnaya |

> **หมายเหตุ:** แถวที่มี _(เติมจาก Wiki TH)_ ยังไม่ยืนยัน — **ตรวจ Wiki/client ก่อน merge**

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
| 合成 | สังเคราะห์ | Crafting |
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

| EN | 中文 | ไทย | หมายเหตุ |
|----|------|-----|----------|
| Nahida | 纳西妲 | _(เติมจาก Wiki TH)_ | ใช้ชื่อ official TH |
| Neuvillette | 那维莱特 | _(เติมจาก Wiki TH)_ | |
| Katherine | 凯瑟琳 | Katherine / แคทเธอรีน | ตรวจ client ไทย |

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
