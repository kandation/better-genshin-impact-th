---
name: bettergi-i18n-architecture
description: >-
  BetterGI localization architecture: JSON UI dictionary (User/I18n), WPF
  AutoTranslateInterceptor, .resx game-task strings, JsonTranslationService.
  Use when adding Thai locale, locating untranslated strings, or wiring th
  into settings.
---

# BetterGI i18n — Architecture

BetterGI มี **สองระบบแปล** แยกกัน — อย่าสลับ workflow

## 1. UI strings (WPF) — JSON dictionary

| ส่วน | Path |
|------|------|
| Loader | `BetterGenshinImpact/Service/JsonTranslationService.cs` |
| Auto-translate WPF tree | `BetterGenshinImpact/View/Behavior/AutoTranslateInterceptor.cs` |
| Binding `{Tr ...}` | `BetterGenshinImpact/View/Converters/TrConverter.cs` |
| ไฟล์ locale | `BetterGenshinImpact/User/I18n/{locale}.json` |
| Upstream i18n repo | [babalae/bettergi-i18n](https://github.com/babalae/bettergi-i18n) |

### รูปแบบ JSON

Flat object — **key = ข้อความจีนต้นฉบับ**, **value = คำแปล**

```json
{
  "设置": "การตั้งค่า",
  "启动": "เริ่ม"
}
```

- Source language: **`zh-Hans`** (implicit — ไม่มีไฟล์ JSON)
- Locale ที่มีแล้ว: `zh-Hant`, `en`, `ja`
- **เป้าหมาย fork:** เพิ่ม `th.json`

### Runtime flow

1. User เลือก UI language ใน Settings → `OtherConfig.UiCultureInfoName`
2. `JsonTranslationService` โหลด `User/I18n/{locale}.json` (bundled + optional download)
3. `AutoTranslateInterceptor` walk WPF tree แปล property ที่ชื่อมี `Text`, `Content`, `Header`, `ToolTip`, `Title`, `Placeholder`, …
4. Key ที่ไม่มีใน JSON → แสดงจีนต้นฉบับ + รายงาน missing (ถ้าเปิด collection)

### Download จาก upstream i18n

```
https://raw.githubusercontent.com/babalae/bettergi-i18n/main/i18n/{locale}.json
```

Production updates มักมาจาก repo แยก — fork นี้ bundle snapshot ใน `User/I18n/`

## 2. Game automation / OCR strings — `.resx`

Task code ใช้ `IStringLocalizer<T>` + ไฟล์ co-located:

```
GameTask/AutoFishing/AutoFishingTask.{zh-Hans,en,fr,zh-Hant}.resx
GameTask/AutoArtifactSalvage/AutoArtifactSalvageTask.*.resx
```

- Base: `*.zh-Hans.resx` — key มักเป็นข้อความ UI ในเกม (จีน)
- แปล: copy จาก `*.en.resx` → `*.th.resx` แล้วแก้ `<value>`

## 3. Game client language (แยกจาก UI language)

| Setting | ความหมาย |
|---------|----------|
| `OtherConfig.UiCultureInfoName` | ภาษา UI ของ BetterGI |
| `OtherConfig.GameCultureInfoName` | ภาษา client เกมสำหรับ OCR / string matching |

OCR model เลือกจาก `Core/Recognition/OCR/Paddle/PaddleOcrService.cs` → `FromCultureInfo()`

## เพิ่ม locale `th` ในแอป (code changes)

Checklist เมื่อ UI พร้อม:

```
- [ ] สร้าง `BetterGenshinImpact/User/I18n/th.json`
- [ ] `CultureInfoNameToKVPConverter.cs` → `"th" => "ไทย"`
- [ ] Settings UI list รองรับ `th` (ตาม pattern locale อื่น)
- [ ] `.resx` ที่ขาดตาม `resx-gaps-th.csv`
- [ ] `dotnet build BetterGenshinImpact.sln -c Debug`
```

## ไฟล์ที่ scan ไม่ครอบคลุม (อย่าใส่ใน th.json)

- `Assets/**/*.json` — pathing/recognition data
- `User/Script`, `User/Js`, `User/log`

## Living doc

<!-- บันทึก architecture changes จาก upstream merge -->
