---
name: bettergi-i18n-index
description: >-
  Index for BetterGI Thai i18n fork (kandation/better-genshin-impact-th).
  Routes agents to git, architecture, translation, batch agents, OCR, and repo
  setup skills. Use when starting i18n work, onboarding contributors, or unsure
  which i18n skill to read.
---

# BetterGI Thai i18n — Skill Index

Fork: **kandation/better-genshin-impact-th** · Branch หลัก: **`i18n-th`** · Upstream: **babalae/better-genshin-impact**

## เริ่มต้นอย่างไร (Quick start)

1. อ่าน [Docs/i18n/CONTRIBUTING.md](../../../Docs/i18n/CONTRIBUTING.md) (คู่มือมนุษย์)
2. ตั้งค่า repo → skill **bettergi-i18n-repo**
3. Scan คีย์ที่ขาด → skill **bettergi-i18n-translate** + **bettergi-i18n-agents**
4. Commit แยกตาม feature → skill **bettergi-i18n-git**

## Child skills

| Skill | คำอธิบายสั้น | เมื่อไหร่ควรใช้ |
|-------|--------------|----------------|
| [bettergi-i18n-repo](../bettergi-i18n-repo/SKILL.md) | Fork, remote, branch, gh CLI | Clone ครั้งแรก, ตั้ง `origin`/`upstream`, sync จาก upstream |
| [bettergi-i18n-git](../bettergi-i18n-git/SKILL.md) | Commit ย่อย, worktree, message convention | ก่อน/หลัง commit, ทำงาน parallel หลาย batch |
| [bettergi-i18n-architecture](../bettergi-i18n-architecture/SKILL.md) | JSON UI dict, `.resx`, loader | แก้โครงสร้าง i18n, เพิ่ม locale `th`, เข้าใจว่า string อยู่ที่ไหน |
| [bettergi-i18n-translate](../bettergi-i18n-translate/SKILL.md) | scan → split → merge → verify, กฎแปลไทย | แปล UI/resx, ตรวจคุณภาพ, อัปเดต glossary |
| [bettergi-i18n-agents](../bettergi-i18n-agents/SKILL.md) | batch files, `agent_prompt_th.md`, parallel agents | มอบ batch ให้ agent ราคาถูก, merge ผลลัพธ์ |
| [bettergi-i18n-ocr](../bettergi-i18n-ocr/SKILL.md) | PP-OCR v5, EasyOCR, game client language | แปล string ที่ OCR จับจากภาพ, ทดสอบ recognition |

## เครื่องมือใน repo

| Path | หน้าที่ |
|------|---------|
| `tools/i18n/scan_missing.py` | หา key ที่ยังไม่แปล |
| `tools/i18n/split_batches.py` | แบ่ง CSV เป็น batch ~150 keys |
| `tools/i18n/merge_fragments.py` | รวม batch เป็น `th.json` |
| `tools/i18n/agent_prompt_th.md` | system prompt สำหรับ agent แปล |
| `tools/i18n/batches/th/manifest.json` | สถานะ batch (ปัจจุบัน 1676 keys / 12 batches) |
| `Docs/i18n/glossary-th.md` | glossary ศัพท์ Genshin ภาษาไทย |
| `Docs/i18n/ocr-multilang-audit.md` | audit OCR / template จีน + สถานะ `.th.resx` |

## สถานะงานแปล (อ้างอิง)

- UI JSON: **1676 / 1676** keys scanned — **0 missing**, **0 empty** (2026-07-23 scan)
- `th.json` on disk: **1697** keys (includes 21 stale whitespace variants kept for compatibility)
- `.resx`: **0 gaps** (ครบ 11 ไฟล์)
- OCR-sensitive: 0 untranslated hits in latest scan (`ocr-related-th.csv` for manual review)

## Living doc

เพิ่มลิงก์ skill ใหม่หรืออัปเดตสถานะงานใน section นี้เมื่อ workflow เปลี่ยน:

<!-- append new skills or status notes below -->

- **Proper names:** regions, characters, fish species → **English only** in `th.json` / `*.th.resx` values (see glossary-th.md)

### Batch progress (2026-07-23)

| Batch | Keys | Status |
|-------|------|--------|
| 001–005 | 749 | done (merged) |
| 006 | 150 | done |
| 007 | 151 | done |
| 008 | 151 | done |
| 009 | 151 | done |
| 010 | 151 | done |
| 011 | 151 | done |
| 012 | 26 | done |
| 013 | 23 | whitespace-variant fix |

- Latest scan: **missing JSON keys 0**, **empty values 0**, **1676** unique UI strings covered
- `.resx`: **0 gaps**
- `th.json` wired in `BetterGenshinImpact.csproj` (`CopyToOutputDirectory`)
