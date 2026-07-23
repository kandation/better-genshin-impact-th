---
name: bettergi-i18n-ocr
description: >-
  OCR notes for BetterGI Thai: PP-OCR v5 model mapping, EasyOCR fallback,
  GameCultureInfoName vs UiCultureInfoName, Thai game client strings in resx.
  Use before translating ocr-related-th.csv or resx automation strings.
---

# BetterGI i18n — OCR Notes

## สอง setting ที่สับสนบ่อย

| Config | Field | ผลต่อ |
|--------|-------|--------|
| UI ภาษา BetterGI | `OtherConfig.UiCultureInfoName` | JSON dictionary / WPF |
| ภาษา client เกม | `OtherConfig.GameCultureInfoName` | OCR model + string match ใน task |

แปล UI เป็นไทยได้ แต่ถ้า **เกมตั้งเป็นจีน/อังกฤษ** OCR จะยังจับข้อความนั้น — automation string ต้องตรงกับ **ภาษาที่เกมแสดงจริง**

## PaddleOCR ใน BetterGI

- Code: `BetterGenshinImpact/Core/Recognition/OCR/Paddle/PaddleOcrService.cs`
- Model mapping: `PaddleOcrModelType.FromCultureInfo(CultureInfo)`

### ภาษาไทย (`th`) — สถานะปัจจุบัน (อัปเดต 2026-07-23)

- `FromCultureInfo()` มี branch `th`/`thai` แล้ว แต่ยัง **`return null`** → fallback V5 (zh/en) — ดู `PaddleOcrService.cs` + [ocr-multilang-audit.md](../../../Docs/i18n/ocr-multilang-audit.md)
- **ไม่มี PP-OCR Thai model** ใน repo — ต้อง bundle หรือใช้ EasyOCR
- **11 ไฟล์ `*.th.resx`** สำหรับ task หลัก (AutoFishing, AutoDomain, …) — resx gaps เหลือ 1 (ชื่อภาษา 简体中文)
- **~80+ hardcoded 中文** ใน `GameTask/` ยังไม่ผ่าน `IStringLocalizer` — ดู Pattern B ใน audit doc

### ก่อนแปล OCR-dependent strings

```
- [ ] ตั้ง game client เป็นภาษาไทย (ถ้าทดสอบไทย)
- [ ] จับ screenshot UI จริง — บันทึกข้อความที่ OCR ต้อง match
- [ ] ทดสอบ recognition (overlay log ใน BetterGI)
- [ ] พิจารณา PP-OCR Thai model หรือ EasyOCR ถ้า Latin ไม่พอ
```

## ไฟล์รายงาน OCR

```powershell
python tools/i18n/scan_missing.py --target-locale th
# → tools/i18n/reports/ocr-related-th.csv
```

String ในรายการนี้มักมาจาก:

- `GameTask/**` paths
- ข้อความที่ task ใช้ `IStringLocalizer` + OCR จับจากภาพ

## กฎแปล string ที่ OCR ใช้

1. **ตรงตัวกับเกม** — ไม่ใช่คำแปลสวยๆ ที่ OCR จับไม่ได้
2. **เว้นวรรค/สระ** ตาม client ไทย (ทดสอบจริง)
3. ถ้า client ไทยใช้ English term (เช่นชื่อบาง event) → **อย่าแปล**
4. บันทึก screenshot + OCR result ใน PR เมื่อเป็นไปได้

## `.resx` + OCR

`resx-gaps-th.csv` รวม key ที่ task ใช้ match UI เกม — workflow:

1. เปิดเกม ภาษาไทย → หน้าจอที่ task ใช้
2. จดข้อความบนจอ
3. ใส่ใน `<value>` ของ `*.th.resx`
4. รัน task สั้นๆ ดู overlay recognition

## EasyOCR (ทางเลือก / อนาคต)

ถ้า Paddle ไม่รองรับไทยเพียงพอ — ตรวจว่า repo มี integration EasyOCR หรือไม่ก่อนแนะนำ upstream

## Upstream contribution

การเพิ่ม `th` ใน `FromCultureInfo()` + model ไทย = **code change แยก** จากงานแปล JSON — เปิด issue/PR ไป upstream หรือ fork ตามนโยบายทีม

## Living doc

<!-- ผลทดสอบ OCR ไทย, model ที่ใช้ได้, screenshot references -->

- **Audit ฉบับเต็ม:** [Docs/i18n/ocr-multilang-audit.md](../../../Docs/i18n/ocr-multilang-audit.md)
- **ตกปลา:** `钓鱼`→`ตกปลา`, `上钩`→`ปลาติดเบ็ด` ใน `AutoFishingTask.th.resx` — ยืนยันกับ client ไทย
- **Blocker หลัก:** PP-OCR Thai model, hardcoded Chinese ใน QuickSereniteaPot / UseRedemptionCode / AutoStygianOnslaught
