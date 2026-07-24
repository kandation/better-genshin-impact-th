# Serilog / status log i18n gaps (Thai fork)

Generated after full GameTask log template sweep (2026-07-23).

## Matching model

`TranslatingSerilogLoggerProvider` translates the **exact** `{OriginalFormat}` template via `ITranslationService` (key = Chinese template). String **args** that contain CJK are also translated (fork change).

## Covered

- All structured `Log*` templates under GameTask/ViewModel/View/Service/Core/Helpers with CJK: **0 missing** after merge
- MaskWindow status labels: translated in `MaskWindowViewModel.InitializeStatusList` + Unicode icon keys in `th.json`
- TaskRunner start/end: `"→ 任务启动！"` / `"→ 任务结束"` (no longer concat via empty `_name`)

## Remaining code-only gaps (`$"..."` / concatenation)

These cannot match `th.json` as whole strings until converted to template + args.

| Area | Count (approx) | Notes |
|------|----------------|-------|
| `$"..."` interpolated Log* | ~120 active (see `tools/i18n/reports/log-interpolated-th.json`) | Prefer `LogInformation("…{X}…", x)` |
| Concat `+` Log lines | ~55 hints | Same fix |

### Fixed in this pass (examples)

- `TaskRunner`: concat → `"→ 任务启动！"` / `"→ 任务结束"`
- `RunnerContext`: concat → `{Count}` / `{Seconds}` templates
- `AutoFightTask` / `AutoFightJsonTask`: several `$"切换为拾取队伍…"` → structured templates
- Arg translation in `TranslatingSerilogLoggerProvider` for CJK string args (e.g. `{Name}` = `千音雅集`)

### Still interpolated (high traffic examples)

See `log-interpolated-th.json` — fishing timeouts, pathing distances, Genius Invokation, etc. Not blocking status overlay / album / task start-end UX.

## User example → runtime mapping

| User saw (formatted) | Actual key(s) |
|----------------------|---------------|
| `→任务启动!` | `→ 任务启动！` (space + fullwidth `！`) |
| `千音雅集:回到…` | template `{Name}：回到…` + arg `千音雅集` |
| `自动音乐专辑任务异常:当前未处于…` | template `自动音乐专辑任务异常:{Msg}` + exception message key |
| `◎拾取 ○剧情…` | status `Name` via Translate(`\uf256 拾取`) etc. |
