---
name: bettergi-i18n-repo
description: >-
  Setup BetterGI Thai i18n fork: gh fork, clone, origin/upstream remotes,
  i18n-th branch, contributing to kandation/better-genshin-impact-th. Use when
  onboarding new contributors or configuring git remotes for the first time.
---

# BetterGI i18n — Repo / Fork Setup

## Repos

| Repo | บทบาท |
|------|--------|
| [babalae/better-genshin-impact](https://github.com/babalae/better-genshin-impact) | Upstream หลัก |
| [babalae/bettergi-i18n](https://github.com/babalae/bettergi-i18n) | UI JSON แยก (PR `th.json` ที่นี่ด้วยเมื่อพร้อม) |
| [kandation/better-genshin-impact-th](https://github.com/kandation/better-genshin-impact-th) | **Fork ภาษาไทย** (origin) |

## Clone ครั้งแรก

```powershell
gh repo fork babalae/better-genshin-impact --clone --remote=false
cd better-genshin-impact

# ถ้า fork แล้ว — clone fork โดยตรง
git clone https://github.com/kandation/better-genshin-impact-th.git
cd better-genshin-impact-th

git remote add upstream https://github.com/babalae/better-genshin-impact.git
git fetch upstream
git checkout i18n-th
```

## ตรวจ remotes

```powershell
git remote -v
# origin    → kandation/better-genshin-impact-th
# upstream  → babalae/better-genshin-impact
```

## Branch strategy

| Branch | ใช้เมื่อ |
|--------|----------|
| `i18n-th` | **default** — งานแปลไทย, docs, tools/i18n |
| `main` | sync upstream baseline |
| `i18n-th/batch-NNN` | worktree ชั่วคราว (optional) |

```powershell
git fetch origin
git checkout i18n-th
git pull origin i18n-th
```

## Sync จาก upstream

```powershell
git fetch upstream
git checkout i18n-th
git merge upstream/main
# แก้ conflict (มักที่ non-i18n code) → commit
git push origin i18n-th
```

## Contributing checklist

```
- [ ] Fork / clone ตามด้านบน
- [ ] อ่าน Docs/i18n/CONTRIBUTING.md
- [ ] อ่าน skill bettergi-i18n-index
- [ ] ทำงานบน branch i18n-th
- [ ] Commit เล็ก + message ชัด (skill git)
- [ ] Push origin → เปิด PR บน fork
```

## PR ไปที่ไหน

| เนื้อหา | Target |
|---------|--------|
| แปลไทย + fork-specific | `kandation/better-genshin-impact-th` → `i18n-th` |
| UI JSON สำหรับช community กว้าง | [babalae/bettergi-i18n](https://github.com/babalae/bettergi-i18n) `th.json` |
| OCR model / core code | upstream `babalae/better-genshin-impact` (แยก discussion) |

## Dependencies สำหรับเครื่องมือ i18n

- Python 3.10+ (stdlib only สำหรับ scripts ใน `tools/i18n/`)
- .NET SDK — build ตรวจ compile
- `gh` CLI — fork/PR (optional แต่แนะนำ)

## Living doc

<!-- onboarding issues, Windows path notes, CI -->
