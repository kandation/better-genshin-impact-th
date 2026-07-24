# BetterGI i18n scan tools

Utilities for finding untranslated UI strings when adding a new locale (e.g. Thai `th`).

## How BetterGI localization works

### UI strings (WPF) — JSON dictionary

| Item | Location |
|------|----------|
| Runtime loader | `BetterGenshinImpact/Service/JsonTranslationService.cs` |
| WPF auto-translate | `BetterGenshinImpact/View/Behavior/AutoTranslateInterceptor.cs` |
| Binding converter | `BetterGenshinImpact/View/Converters/TrConverter.cs` |
| Bundled translations | `BetterGenshinImpact/User/I18n/{locale}.json` |
| Canonical upstream repo | [babalae/bettergi-i18n](https://github.com/babalae/bettergi-i18n) |

**Format:** flat JSON object — **key = Chinese source text**, **value = translation**.

```json
{
  "设置": "Settings",
  "启动": "Start"
}
```

`zh-Hans` is the implicit source language (no JSON file). Other UI locales in settings today: `zh-Hant`, `en`, `ja`.

At runtime, `AutoTranslateInterceptor` walks WPF trees and translates static literals on properties whose names contain `Text`, `Content`, `Header`, `ToolTip`, `Title`, `Placeholder`, etc.

### Game automation / OCR strings — `.resx`

Task code uses `IStringLocalizer<T>` with co-located `.resx` files, e.g.:

- `GameTask/AutoFishing/AutoFishingTask.{zh-Hans,en,fr,zh-Hant}.resx`
- `GameTask/AutoArtifactSalvage/AutoArtifactSalvageTask.*.resx`

Keys are usually Chinese game UI text (`合成`, `每日`, …). Existing locales: **zh-Hans** (base), **zh-Hant**, **en**, **fr**.

### OCR / game language (separate from UI language)

- Setting: `OtherConfig.GameCultureInfoName` (game client language for recognition)
- PaddleOCR model selection: `Core/Recognition/OCR/Paddle/PaddleOcrService.cs`
- V5 Latin model covers many scripts; **Thai (`th`) is not explicitly mapped** — may fall back to Latin model or need PP-OCR Thai / EasyOCR verification before translating OCR-dependent task strings.

---

## Tool: `scan_missing.py`

Scans the repo and compares source strings against translation files.

### What it finds

1. **Hardcoded CJK in `.xaml`** — `Text`, `Content`, `Header`, `ToolTip`, `Title`, `PlaceholderText`, `Run.Text`, …
2. **Hardcoded CJK in `.cs`** — string literals (comments stripped)
3. **Missing JSON keys** — source strings not present in `User/I18n/{target}.json`
4. **Empty JSON values** — keys with blank translations
5. **Stale JSON keys** — keys in JSON not seen in scan (dynamic/runtime-only strings)
6. **`.resx` gaps** — keys in `*.zh-Hans.resx` missing or untranslated in `*.{target}.resx`

OCR-related hits are flagged when the path or text suggests recognition/game-task usage.

### Requirements

- Python 3.10+ (stdlib only)
- Windows PowerShell or any shell

### Run

```powershell
# Default: compare against bundled en.json
.\tools\i18n\run-scan.ps1

# Thai (file does not exist yet — expect all keys missing)
.\tools\i18n\run-scan.ps1 -TargetLocale th

# Direct Python
python tools/i18n/scan_missing.py --target-locale en
python tools/i18n/scan_missing.py --target-locale th --include-english
```

### Output (`tools/i18n/reports/`)

| File | Contents |
|------|----------|
| `missing-{locale}.json` | Full report |
| `missing-json-keys-{locale}.csv` | Keys to add to JSON |
| `hardcoded-not-in-json-{locale}.csv` | Per-occurrence details |
| `resx-gaps-{locale}.csv` | Missing `.resx` translations |
| `ocr-related-{locale}.csv` | OCR-sensitive strings |

### Default exclusions

- `bin/`, `obj/`, `Test/`, `.github/`
- `**/Assets/**/*.json` (pathing/recognition data, not UI copy)
- `User/Script`, `User/Js`, `User/log`

Override with `--exclude-dir dirname`.

---

## Thai translation guidelines

Context for translators and parallel agents:

| Topic | Guidance |
|-------|----------|
| Game | Genshin Impact (原神) |
| Terminology | Prefer **official Thai in-game terms** where they exist |
| Map / location names | **English proper names** — Fontaine, Liyue, Mondstadt (do not transliterate to Thai) |
| Artifacts / characters | Cross-check [Genshin Impact Wiki (Thai)](https://genshin-impact.fandom.com/th/) or English wiki + official Thai client |
| OCR / automation strings | Strings matched against game screenshots — verify Thai OCR support (PP-OCR v5 / EasyOCR) before translating; flag in `ocr-related-*.csv` |
| UI JSON workflow | Add `"中文原文": "คำแปลไทย"` entries to `th.json`, then PR to [bettergi-i18n](https://github.com/babalae/bettergi-i18n) |
| Resx workflow | Copy nearest locale file (e.g. `AutoFishingTask.en.resx` → `AutoFishingTask.th.resx`) and translate `<value>` nodes |

### Cheap parallel translation workflow

1. Run `python tools/i18n/scan_missing.py --target-locale th`
2. Split UI keys into agent batches (~150 keys each):
   ```powershell
   python tools/i18n/split_batches.py --batch-size 150
   ```
   Output: `tools/i18n/batches/th/batch-001-th.json` … + `manifest.json`
3. Assign one batch per cheap agent using `agent_prompt_th.md` as the system prompt
4. Merge agent outputs:
   ```powershell
   python tools/i18n/merge_fragments.py --fragments-dir tools/i18n/batches/th/done --drop-empty
   ```
5. Handle smaller files separately:
   - `resx-gaps-th.csv` → game-task OCR strings (46 keys, needs game knowledge)
   - `ocr-related-th.csv` → review before translating (108 keys)
6. Add `"th" => "ไทย"` to `CultureInfoNameToKVPConverter.cs` and settings UI list
7. Test in app: Settings → UI language → Thai; exercise OCR-heavy tasks

### Gemini API translation (bulk)

For large batches, use `translate_gemini.py` with Google Gemini instead of manual agents.

```powershell
pip install -r tools/i18n/requirements-gemini.txt

# Set key once (do not commit)
$env:GEMINI_API_KEY = "your_key"
# or copy tools/i18n/.env.example → tools/i18n/.env

# Translate pending batches (empty values only)
.\tools\i18n\run-translate-gemini.ps1

# One file, dry run
python tools/i18n/translate_gemini.py tools/i18n/batches/th/batch-008-th.json --dry-run

# Merge when done
python tools/i18n/merge_fragments.py --fragments-dir tools/i18n/batches/th/done --drop-empty
```

Defaults: model `models/gemini-3.6-flash`, 40 keys per API call, rules from `agent_prompt_th.md`.

---

## Updating upstream i18n

Bundled files are snapshots. Production updates are downloaded from:

```
https://raw.githubusercontent.com/babalae/bettergi-i18n/main/i18n/{locale}.json
```

After translating, contribute `th.json` to **bettergi-i18n**, not only this fork.
