---
name: bettergi-i18n-agents
description: >-
  Parallel agent workflow for BetterGI Thai UI translation using tools/i18n/
  batch files and agent_prompt_th.md. Covers cheap model assignment, worktree
  isolation, done/ output, and merge_fragments.py. Use when running batch
  translation agents or splitting work across multiple Cursor/cloud agents.
---

# BetterGI i18n — Agent / Batch Workflow

## ไฟล์สำคัญ

| Path | บทบาท |
|------|--------|
| `tools/i18n/agent_prompt_th.md` | System prompt — copy ทั้งไฟล์ให้ agent |
| `tools/i18n/batches/th/batch-NNN-th.json` | Input (~150 keys, value ว่าง) |
| `tools/i18n/batches/th/manifest.json` | รายการ batch + จำนวน key |
| `tools/i18n/batches/th/done/` | **Output** หลัง agent แปล (สร้างเอง) |

## ขั้นตอนมาตรฐาน (agent หนึ่งตัว / หนึ่ง batch)

1. แนบ `batch-NNN-th.json` ให้ agent
2. ใส่ prompt จาก `agent_prompt_th.md`
3. รับ **JSON เท่านั้น** — key เดิม, value เป็นไทย
4. บันทึกเป็น `tools/i18n/batches/th/done/batch-NNN-th.json`
5. Validate: `python -c "import json; json.load(open('...','r',encoding='utf-8'))"`

## Parallel agents (หลาย batch พร้อมกัน)

### แบบ A — Cursor / cloud agents แยก chat

```
Agent 1 → batch-001-th.json → done/batch-001-th.json
Agent 2 → batch-002-th.json → done/batch-002-th.json
...
Agent 12 → batch-012-th.json → done/batch-012-th.json
```

- ใช้ **model ราคาถูก/เร็ว** — งานเป็น pattern ซ้ำ
- หนึ่ง agent หนึ่ง batch — อย่าให้สอง agent แก้ไฟล์เดียวกัน

### แบบ B — git worktree (แนะนำเมื่อ commit แยก branch)

ดู skill **bettergi-i18n-git** — branch `i18n-th/batch-NNN` ต่อ worktree

## Prompt template (สั้น)

```
Read tools/i18n/agent_prompt_th.md

Translate tools/i18n/batches/th/batch-003-th.json to Thai.
Return ONLY valid JSON with same keys.
Save output to tools/i18n/batches/th/done/batch-003-th.json
Do not translate URLs, regex, or log format strings.
```

## หลัง agent เสร็จทุก batch

```powershell
python tools/i18n/merge_fragments.py `
  --fragments-dir tools/i18n/batches/th/done `
  --drop-empty

python tools/i18n/scan_missing.py --target-locale th
dotnet build BetterGenshinImpact.sln -c Debug
```

## จัดการ error จาก agent

| ปัญหา | แก้ |
|-------|-----|
| Output มี markdown ``` | strip fences ก่อน save |
| Key หาย | reject — ต้องครบทุก key |
| `_note_*` keys | ลบก่อน merge หรือแก้ manual |
| ค่าว่าง | `--drop-empty` หรือ re-run agent เฉพาะ key |

## Batch tracking (manifest)

อัปเดตสถานะใน PR description หรือ issue:

```
- [x] batch-001 (150)
- [x] batch-002 (150)
- [ ] batch-003 (150)
...
```

## งานที่ **ไม่** ควรใส่ใน cheap batch agent

- `resx-gaps-th.csv` — ต้องรู้ game UI + OCR
- `ocr-related-th.csv` — ต้องทดสอบ recognition ก่อน
- `CultureInfoNameToKVPConverter.cs` — code change แยก commit

## Living doc

<!-- tips เรื่อง model, token limit, batch size ที่เหมาะ -->
