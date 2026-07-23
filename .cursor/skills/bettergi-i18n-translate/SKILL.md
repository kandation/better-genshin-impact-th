---
name: bettergi-i18n-translate
description: >-
  BetterGI Thai translation workflow: scan_missing.py, split_batches.py,
  agent translate, merge_fragments.py, verify. Includes Genshin Thai terminology,
  transliteration, wiki references, OCR-sensitive string rules. Use when
  translating UI JSON, resx, or reviewing translation quality.
---

# BetterGI i18n — Translation Workflow

## Pipeline overview

```
scan → split batches → agent/human translate → merge → verify → commit
```

## Step 1: Scan

```powershell
# PowerShell wrapper
.\tools\i18n\run-scan.ps1 -TargetLocale th

# หรือ Python โดยตรง
python tools/i18n/scan_missing.py --target-locale th
python tools/i18n/scan_missing.py --target-locale th --include-english
```

### Reports (`tools/i18n/reports/`)

| File | ใช้ทำอะไร |
|------|-----------|
| `missing-th.json` | รายงานรวม |
| `missing-json-keys-th.csv` | **input หลัก** สำหรับ split_batches |
| `hardcoded-not-in-json-th.csv` | string ใน xaml/cs ที่ยังไม่มี key |
| `resx-gaps-th.csv` | `.resx` ที่ยังไม่มี locale th |
| `ocr-related-th.csv` | string ที่เกี่ยวกับ OCR — อ่าน skill OCR ก่อนแปล |

## Step 2: Split batches (UI JSON)

```powershell
python tools/i18n/split_batches.py --batch-size 150
# Output: tools/i18n/batches/th/batch-001-th.json … manifest.json
```

ปัจจุบัน: **1676 keys → 12 batches** (batch สุดท้าย 26 keys)

## Step 3: Translate

- UI batch: ใช้ skill **bettergi-i18n-agents** + `tools/i18n/agent_prompt_th.md`
- `.resx`: แปลทีละไฟล์จาก `resx-gaps-th.csv` — ต้องรู้ UI เกม
- OCR strings: skill **bettergi-i18n-ocr** ก่อน

## Step 4: Merge

```powershell
# วางผล agent ใน tools/i18n/batches/th/done/
python tools/i18n/merge_fragments.py --fragments-dir tools/i18n/batches/th/done --drop-empty
# → BetterGenshinImpact/User/I18n/th.json
```

## Step 5: Verify

```
- [ ] re-scan: missing-json-keys-th.csv ลดลง
- [ ] JSON valid UTF-8, ไม่มี key ซ้ำ conflict
- [ ] รักษา {0}, \n, HTML, hotkeys
- [ ] dotnet build BetterGenshinImpact.sln -c Debug
- [ ] (manual) Settings → UI ภาษาไทย — สุ่มหน้าหลักๆ
```

## กฎแปลภาษาไทย (Genshin / BetterGI)

### ศัพท์และแหล่งอ้างอิง

| หัวข้อ | แนวทาง |
|--------|--------|
| เกม | Genshin Impact (原神) |
| ศัพท์ในเกม | ใช้ **คำไทย official client** เมื่อมี — ดู [Genshin Wiki TH](https://genshin-impact.fandom.com/th/) |
| ชื่อเฉพาะ (region / ตัวละคร / ปลา) | **ชื่อภาษาอังกฤษ** — Fontaine, Liyue, Jean, Medaka ฯลฯ — **ห้าม** ทับศัพท์ไทย (ฟอนเตน, ลิเยว่) หรือปล่อยจีนใน value |
| ตัวละคร / อาวุธ / artifact | cross-check Wiki TH + client ไทย (เฉพาะศัพท์ทั่วไป ไม่ใช่ proper name) |
| Glossary ทีม | อัปเดต [Docs/i18n/glossary-th.md](../../../Docs/i18n/glossary-th.md) เมื่อตัดสินใจศัพท์ใหม่ |

### โทนและรูปแบบ UI

- ป้ายสั้น → แปลสั้น ไม่ขยายความ
- Tooltip → อธิบายชัดขึ้นได้เล็กน้อย
- อย่าแปล: URL, regex, path, version, ชื่อไฟล์, log format
- รักษา: `{0}`, `{1}`, `%s`, `\n`, `<b>`, ชื่อปุ่ม (`F`, `Ctrl`)

### OCR-sensitive strings

- ต้อง **ตรงกับข้อความบนหน้าจอเกม client ไทย** — ห้าม paraphrase
- ถ้า OCR ยังไม่รองรับไทย → อย่า merge จนกว่าจะทดสอบ (skill OCR)
- flag ใน `ocr-related-th.csv`

### `.resx` workflow

1. เปิด `*.{task}.en.resx` (หรือ zh-Hans เป็น reference key)
2. Copy เป็น `*.th.resx`
3. แปลเฉพาะ `<value>` — **อย่าเปลี่ยน `<name>` (key จีน)**
4. Commit แยกต่อ task file

## Output quality checklist

```
- [ ] ทุก value เป็นภาษาไทย (ยกเว้น token ที่ห้ามแปล)
- [ ] ไม่มี markdown fence ใน JSON output จาก agent
- [ ] ศัพท์สำคัญตรง glossary
- [ ] OCR strings ตรง client ไทย
```

## Living doc

<!-- บันทึก edge cases, คำที่ตกลงใหม่, ปัญหา merge -->

- **Proper names (2026-07-23):** regions / characters / fish → English display names only; no Thai transliteration in values.
- **Whitespace keys (2026-07-23):** scan finds exact source strings (trailing spaces, `\n` suffix). batch-013 fix added 23 variant keys; 21 stale keys without variants remain harmless.
