---
name: bettergi-i18n-git
description: >-
  Git workflow for BetterGI Thai i18n fork: incremental commits per feature,
  git worktree for parallel batch translation, origin/upstream remotes, i18n-th
  branch strategy. Use when committing i18n work, syncing upstream, or running
  parallel translation branches.
---

# BetterGI i18n — Git Workflow

## Remotes & branches

| Remote | URL | ใช้เมื่อ |
|--------|-----|----------|
| `origin` | `https://github.com/kandation/better-genshin-impact-th.git` | push PR/commit ของ fork |
| `upstream` | `https://github.com/babalae/better-genshin-impact.git` | ดึงโค้ดหลัก BetterGI |

- **Branch หลักของ fork:** `i18n-th` (default สำหรับงานแปลไทย)
- **`main`:** ตาม upstream / release baseline — ไม่แปลบน main โดยตรง

```powershell
git fetch upstream
git checkout i18n-th
git merge upstream/main   # หรือ rebase ตามนโยบายทีม
```

## หลักการ commit

1. **Commit หลัง feature ย่อยเสร็จ** — อย่ารวม scan + แปล 12 batch + แก้ OCR ใน commit เดียว
2. **Commit เล็ก incremental** — หนึ่ง batch, หนึ่งไฟล์ resx, หรือหนึ่งการ enable locale
3. **อย่า commit ไฟล์ชั่วคราว** — ยกเว้น `tools/i18n/batches/` ถ้าทีมใช้ track progress

### Commit message convention

รูปแบบที่ fork นี้ใช้:

```
<type>(<scope>): <สรุปสั้นเป็นภาษาอังกฤษหรือไทย>

[optional body]
```

| type | ตัวอย่าง |
|------|----------|
| `feat(i18n-th)` | ฟีเจอร์ locale / เครื่องมือ i18n |
| `i18n(th)` | แปล batch หรืออัปเดต `th.json` |
| `fix(i18n-th)` | แก้คำแปล / OCR string |
| `docs(i18n)` | เอกสาร contributor |

**ตัวอย่างจริงจาก repo:**

```
feat(i18n-th): Thai-first README, CN archive, and i18n scan tools
i18n(th): translate UI batch 001 (150 keys)
i18n(th): add AutoFishingTask.th.resx
feat(i18n-th): register th in CultureInfoNameToKVPConverter
```

## git worktree — แปล parallel หลาย batch

ใช้เมื่อรัน agent หลายตัวพร้อมกัน โดยไม่ชน working tree เดียวกัน

```powershell
# จาก repo หลัก (i18n-th)
cd D:\games\better_gh_th

# สร้าง worktree ต่อ batch (ตัวอย่าง batch 001 และ 002)
git worktree add ..\better_gh_th-batch-001 -b i18n-th/batch-001 i18n-th
git worktree add ..\better_gh_th-batch-002 -b i18n-th/batch-002 i18n-th

# ในแต่ละ worktree: แปล → บันทึก tools/i18n/batches/th/done/batch-NNN-th.json
cd ..\better_gh_th-batch-001
# ... agent work ...
git add tools/i18n/batches/th/done/batch-001-th.json
git commit -m "i18n(th): translate UI batch 001"

# กลับ repo หลัก merge branch ย่อย
cd D:\games\better_gh_th
git merge i18n-th/batch-001
git merge i18n-th/batch-002

# ล้าง worktree เมื่อเสร็จ
git worktree remove ..\better_gh_th-batch-001
git branch -d i18n-th/batch-001
```

### Worktree checklist

```
- [ ] branch ชื่อ `i18n-th/batch-NNN` ชัดเจน
- [ ] แต่ละ worktree แก้ไฟล์ batch คนละไฟล์
- [ ] merge กลับ `i18n-th` แล้วรัน merge_fragments.py ที่ repo หลัก
- [ ] ลบ worktree + branch ชั่วคราว
```

## Push

```powershell
git push origin i18n-th
```

## Living doc — บันทึก learnings

<!-- เพิ่ม git tips, conflict patterns, upstream sync notes ด้านล่าง -->
