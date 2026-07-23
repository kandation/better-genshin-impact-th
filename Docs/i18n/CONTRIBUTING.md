# คู่มือผู้ร่วมพัฒนา i18n ภาษาไทย · BetterGI Thai Fork

**Contributing to Thai localization** — [kandation/better-genshin-impact-th](https://github.com/kandation/better-genshin-impact-th) · branch `i18n-th`

---

## ภาพรวม (Overview)

Fork นี้แปล BetterGI (เครื่องมือ automation Genshin Impact) เป็นภาษาไทย โดยใช้:

- **JSON dictionary** สำหรับ UI (`BetterGenshinImpact/User/I18n/th.json`)
- **`.resx`** สำหรับ string ใน game tasks / OCR
- **เครื่องมือ Python** ใน `tools/i18n/`

Upstream หลัก: [babalae/better-genshin-impact](https://github.com/babalae/better-genshin-impact)  
UI translations ช community: [babalae/bettergi-i18n](https://github.com/babalae/bettergi-i18n)

---

## เริ่มต้นอย่างไร

### 1. ตั้งค่า repo

```powershell
git clone https://github.com/kandation/better-genshin-impact-th.git
cd better-genshin-impact-th
git remote add upstream https://github.com/babalae/better-genshin-impact.git
git checkout i18n-th
```

### 2. อ่านเอกสาร agent (Cursor)

เปิด skill index: `.cursor/skills/bettergi-i18n-index/SKILL.md`

| หัวข้อ | Skill |
|--------|-------|
| Git / worktree | `bettergi-i18n-git` |
| โครงสร้าง i18n | `bettergi-i18n-architecture` |
| ขั้นตอนแปล | `bettergi-i18n-translate` |
| Agent แบบ batch | `bettergi-i18n-agents` |
| OCR | `bettergi-i18n-ocr` |
| Fork setup | `bettergi-i18n-repo` |

### 3. Scan งานที่ค้าง

```powershell
.\tools\i18n\run-scan.ps1 -TargetLocale th
```

---

## Workflow แปล UI (สรุป)

1. **Scan** — `python tools/i18n/scan_missing.py --target-locale th`
2. **Split** — `python tools/i18n/split_batches.py --batch-size 150`
3. **Translate** — ใช้ `tools/i18n/agent_prompt_th.md` + `batch-NNN-th.json`
4. **Merge** — `python tools/i18n/merge_fragments.py --fragments-dir tools/i18n/batches/th/done --drop-empty`
5. **Verify** — scan ซ้ำ + `dotnet build BetterGenshinImpact.sln -c Debug`
6. **Commit & push** — commit เล็กต่อ batch/feature

รายละเอียด: `tools/i18n/README.md` และ skills ด้านบน

---

## กฎแปลภาษาไทย (สรุป)

- ใช้ศัพท์ **official Genshin client ไทย** เมื่อมี
- ชื่อแผนที่: ทับศัพท์ได้ (蒙德 → มอนด์สตัด)
- อ้างอิง [Genshin Wiki TH](https://genshin-impact.fandom.com/th/) และ [glossary-th.md](./glossary-th.md)
- String ที่ OCR ใช้: **ต้องตรงข้อความบนจอเกม** — อ่าน skill OCR ก่อน
- อย่าแปล URL, regex, path, hotkey names

---

## Git

- **origin** = fork ของคุณ / kandation  
- **upstream** = babalae/better-genshin-impact  
- ทำงานบน **`i18n-th`**
- Commit หลัง feature ย่อยเสร็จ — ตัวอย่าง: `i18n(th): translate UI batch 003`
- Parallel batch: ใช้ `git worktree` (ดู skill git)

```powershell
git push origin i18n-th
```

---

## สิ่งที่ควร contribute กลับ upstream

| งาน | ปลายทาง |
|-----|---------|
| `th.json` ครบ/เกือบครบ | [bettergi-i18n](https://github.com/babalae/bettergi-i18n) |
| รองรับ OCR ไทย (model mapping) | better-genshin-impact upstream |

---

## ติดต่อ / คำถาม

- เปิด Issue บน fork ภาษาไทย
- อัปเดต glossary เมื่อตัดสินใจศัพท์ใหม่

---

## English (brief)

This fork adds **Thai UI** to BetterGI. Work on branch **`i18n-th`**. Run `tools/i18n/scan_missing.py --target-locale th`, split into batches, translate with `agent_prompt_th.md`, merge to `User/I18n/th.json`, build, commit incrementally, push to origin. Cursor agents should read `.cursor/skills/bettergi-i18n-index/SKILL.md` first.
