# OCR / Template Matching Multi-Language Audit

Audit date: 2026-07-23 · Branch: `i18n-th` · Fork: kandation/better-genshin-impact-th

BetterGI uses **Chinese (`zh-Hans`) as the primary language** for many automation strings, OCR match targets, and recognition assets. This document maps the architecture, risks for Thai (`th`) game clients, and remediation status.

---

## 1. Where OCR runs

### PaddleOcrService

| Item | Location |
|------|----------|
| Service | `BetterGenshinImpact/Core/Recognition/OCR/Paddle/PaddleOcrService.cs` |
| Factory | `BetterGenshinImpact/Core/Recognition/OCR/OcrFactory.cs` |
| Culture source | `OtherConfig.GameCultureInfoName` (not UI language) |

**Model selection** — `PaddleOcrModelType.FromCultureInfo(CultureInfo)`:

| Culture bucket | PP-OCR model | Examples |
|----------------|--------------|----------|
| `ocrV5Langs` | V5 (zh/en/ja) | `zh-Hans`, `en`, `ja` |
| `latinLangs` | V5Latin | `de`, `fr`, `vi`, … |
| `eslavLangs` | V5Eslav | `ru`, `uk`, … |
| `ko` | V5Korean | Korean |
| **`th`** | **`null` → OcrFactory fallback V5** | No Thai script model |

Default OCR config: `PaddleOcrModelConfig.V4Auto` or `V5Auto`. When `FromCultureInfo()` returns `null`, factory falls back to **V4 or V5** (Chinese/English-centric).

**Thai status (2026-07-23):** Explicit `th`/`thai` branch added with TODO comment. Still returns `null` — **no PP-OCR Thai recognition model** is bundled. V5Latin does **not** cover Thai script.

### UI vs game language

| Setting | Field | Drives |
|---------|-------|--------|
| BetterGI UI | `OtherConfig.UiCultureInfoName` | `User/I18n/{locale}.json`, WPF auto-translate |
| Game client | `OtherConfig.GameCultureInfoName` | OCR model selection, `.resx` task strings via `WithCultureGet` |

Both are selectable in **Settings → Common → 原神游戏语言 / UI language** (`CommonSettingsPage.xaml`). `LanguageDict` includes `th` for both pickers.

---

## 2. Chinese-centric hardcoded strings

### Pattern A — Culture-aware (good, needs `.th.resx`)

Tasks use `IStringLocalizer<T>` + `CultureHelper.WithCultureGet(cultureInfo, "中文key")`:

```csharp
CultureInfo cultureInfo = new CultureInfo(TaskContext.Instance().Config.OtherConfig.GameCultureInfoName);
this.fishingLocalizedString = stringLocalizer.WithCultureGet(cultureInfo, "钓鱼");
```

**Files using this pattern:**

| Task / helper | Keys (zh-Hans) | `.th.resx` |
|---------------|----------------|------------|
| `AutoFishingTask` | 钓鱼, 上钩 | ✅ Added |
| `AutoDomainTask` | 挑战达成, 跳过, … (+4 keys missing from base resx) | ✅ Partial |
| `AutoArtifactSalvageTask` | 快速选择, affix names, star tiers | ✅ Added (EN stats) |
| `TpTask` | Region names (蒙德, 璃月, …) | ✅ Added |
| `GoToAdventurersGuildTask` | 凯瑟琳, 每日, 探索 | ✅ Added |
| `GoToCraftingBenchTask` | 合成 | ✅ Added |
| `GoToSereniteaPotTask` | 阿圆, 壶灵, … | ❌ **No `.resx` at all** |
| `ClaimBattlePassRewardsTask` | 一键, 领取 | ✅ Added |
| `ClaimEncounterPointsRewardsTask` | 委托 | ✅ Added |
| `CheckRewardsTask` | 今日奖励已领取 | ✅ Added |
| `BvResxHelper` / `BvStatus` | 复苏 | ✅ Added |

### Pattern B — Hardcoded Chinese in code (high risk for non-zh clients)

These **ignore** `GameCultureInfoName`:

| File | Examples | Risk |
|------|----------|------|
| `QuickSereniteaPotTask.cs` | `Bv.FindF(capture, "进入", "尘歌壶")` | Thai UI won't match |
| `UseRedemptionCodeTask.cs` | `GetByText("账户")`, `"前往兑换"`, … | Full task broken on Thai |
| `CraftMaterialTask.cs` | `"合成"`, `"确认"`, `"筛选"` | Crafting automation |
| `AutoStygianOnslaughtTask.cs` | `"幽境危战"`, `"前往挑战"`, … | Event task |
| `AutoLeyLineOutcropTask.cs` | `Bv.FindF(capture, "接触")`, `"地脉"` | Ley line farming |
| `QuickSereniteaPotTask.cs` | `"进入"`, `"离开"` | Serenitea pot macro |
| `OneKeyClaimRewardTask.cs` | `"领取"`, `"礼物领取"` | Reward macro |
| `GridScreenName.cs` | Inventory tab names (武器, 圣遗物, …) | Grid OCR |
| `GameSettingsChecker.cs` | Warns if game lang ≠ zh-Hans | User expectation |

**Count:** 80+ `GameTask/` files contain Chinese string literals used for matching (grep `[\u4e00-\u9fff]`).

### Pattern C — Image / template assets

- `RecognitionAssets.Get("AutoFishing", "LiftRodButton", …)` — pixel templates, language-agnostic
- `Assets/**/*.json` pathing data — not in i18n scan scope
- `AutoFishingImageRecognition.MatchFishBiteWords` — white-bar contour detection (language-agnostic primary path)

### Pattern D — `Bv.FindF` OCR pipeline

`BvSimpleOperation.FindF` → crops F-key prompt area → `RecognitionObject.OcrThis` → **regex match** against passed strings. Strings must match **on-screen game text** for the configured culture.

---

## 3. IStringLocalizer + `.resx` locales

### How it works

1. `App.xaml.cs` registers `services.AddLocalization()`
2. Co-located satellite files: `{TaskName}.{culture}.resx` (e.g. `AutoFishingTask.th.resx`)
3. **Keys are Chinese UI strings** from `*.zh-Hans.resx`; **values** are the text shown in the game for that locale
4. `WithCultureGet` temporarily sets `CurrentUICulture` to `GameCultureInfo`, then indexes `stringLocalizer[zhKey]`
5. Fallback chain: `{culture}` → parent → default; if missing, **returns the key (Chinese)** → OCR searches for Chinese on a Thai screen → **fail**

### Game language ≠ UI language

| Scenario | UI (th.json) | Game (th) | Result |
|----------|--------------|-----------|--------|
| Thai UI + Thai game | Thai labels | Thai OCR strings from `.th.resx` | ✅ Intended |
| Thai UI + zh-Hans game | Thai labels | Chinese from `.zh-Hans.resx` | ✅ If user sets game lang correctly |
| Thai UI + Thai game, missing `.th.resx` | Thai labels | Falls back to **Chinese keys** | ❌ OCR mismatch |
| zh-Hans UI + Thai game | Chinese UI | Needs `.th.resx` + game lang = th | Mixed |

**Critical:** Users must set **原神游戏语言** to match the actual Genshin client language.

---

## 4. Thai game client + Chinese search strings

When `GameCultureInfoName = th` but `.th.resx` is missing (before this fix):

1. `WithCultureGet` returns Chinese key (e.g. `"钓鱼"`)
2. Paddle OCR uses V5 fallback — **cannot reliably read Thai script**
3. `Bv.FindF` / OCR match compares against Chinese → **no match**
4. `GameSettingsChecker` logs warning if registry game lang ≠ zh-Hans (informational)

**After `.th.resx` addition:** String side is addressed for 11 task resource files (46 keys). OCR model limitation for Thai **script** remains.

---

## 5. Fishing OCR strings (community priority)

### resx-backed (culture-aware)

| Key | zh-Hans | `th.resx` value | Notes |
|-----|---------|-----------------|-------|
| 钓鱼 | 钓鱼 | `ตกปลา` | F-key enter fishing mode (`EnterFishingMode`, `QuitFishingMode`) |
| 上钩 | 上钩 | `ปลาติดเบ็ด` | Partial match for on-screen `ปลาติดเบ็ดแล้วล่ะ` (Thai guide citation) |

**Detection order in `FishBite` behaviour:**

1. `MatchFishBiteWords` — white text bar contour (language-agnostic)
2. `LiftRodButton` template image
3. OCR contains `getABiteLocalizedString` from resx

### Fish species — English by design

| Component | Language | OCR impact |
|-----------|----------|------------|
| `BigFishType` / `FishType` | `Name` = English (`medaka`, `pufferfish`) | YOLO class labels — **not OCR** |
| `ChineseName` field | Chinese | Overlay/debug logging only |
| Bait selection | Icon/template matching | Language-agnostic |

**Thai community note:** Fish and bait names in Thai client remain **English** (e.g. Medaka, Fruit Paste Bait) — do **not** translate in code. Only UI prompts (钓鱼/上钩) need `.th.resx`.

### Still hardcoded for fishing context

- Behaviour tree node names (Chinese log strings) — logging only
- `FishType.cs` / `BigFishType.cs` — `ChineseName` for draw overlay when Thai game is used (cosmetic)

---

## 6. Fixes applied (this branch)

| Change | File(s) |
|--------|---------|
| Audit document | `Docs/i18n/ocr-multilang-audit.md` |
| Documented `th` OCR gap | `PaddleOcrService.cs` |
| Starter `.th.resx` (11 files, 46 keys) | `GameTask/**`, `View/Converters/` |

### `.th.resx` files added

- `AutoFishingTask.th.resx`
- `AutoDomainTask.th.resx`
- `AutoArtifactSalvageTask.th.resx`
- `TpTask.th.resx`
- `BvResxHelper.th.resx`
- `CheckRewardsTask.th.resx`
- `ClaimBattlePassRewardsTask.th.resx`
- `ClaimEncounterPointsRewardsTask.th.resx`
- `GoToAdventurersGuildTask.th.resx`
- `GoToCraftingBenchTask.th.resx`
- `CultureInfoNameToKVPConverter.th.resx`

---

## 7. What still blocks full Thai OCR

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| No PP-OCR Thai recognition model | **High** for Thai script UI | Use English game client; or upstream Thai model / EasyOCR |
| 80+ hardcoded Chinese literals in `GameTask/` | **High** for affected tasks | Migrate to resx + `WithCultureGet` incrementally |
| `GoToSereniteaPotTask` — no base `.resx` | Medium | Add `*.zh-Hans.resx` + locales |
| `AutoDomainTask` — 4 keys used in code but absent from resx (匹配挑战, 快速编队, 限时全部开放, 限时开放) | Medium | Add keys to all locale resx |
| `.th.resx` values need in-game screenshot verification | Medium | Test overlay + adjust strings |
| `GameSettingsChecker` zh-Hans warning | Low | Update message for multi-lang |
| Inventory/grid Chinese tab names | Medium | `GridScreenName` enum |

---

## 8. Verification

```powershell
python tools/i18n/scan_missing.py --target-locale th
# Expect: Resx gaps for .th.resx: 0 (after fix)
# OCR-related hits remain for hardcoded Chinese in non-resx code paths

dotnet build BetterGenshinImpact.sln -c Debug
```

### Testing checklist (manual)

- [ ] Set game language = ไทย / `th` in BetterGI settings
- [ ] Auto fishing: F-key prompt, bite notification
- [ ] Map teleport: region name switch (蒙德 → Mondstadt, 璃月 → Liyue, …)
- [ ] Adventurers Guild daily: Katheryne prompt
- [ ] Capture OCR overlay log for Thai script accuracy

---

## References

- `.cursor/skills/bettergi-i18n-ocr/SKILL.md`
- `.cursor/skills/bettergi-i18n-architecture/SKILL.md`
- `Docs/i18n/glossary-th.md` — fishing: 钓鱼→ตกปลา, 上钩→ปลาติดเบ็ด (verify in-game)
- Thai fishing bite UI: community guides cite **「ปลาติดเบ็ดแล้วล่ะ」**
