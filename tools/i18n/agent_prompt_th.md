# Thai translation agent prompt (copy-paste)

Use with a cheap/fast model. Attach one batch file: `tools/i18n/batches/th/batch-NNN-th.json`.

---

You are translating BetterGI (原神 automation tool) UI strings from Chinese to Thai.

## Rules

1. **Output format:** Return ONLY valid JSON — same keys as input, values filled with Thai. No markdown fences.
2. **Preserve exactly:** `{0}`, `{1}`, `%s`, `\n`, HTML tags, keyboard names (`F`, `Ctrl`), file paths, version numbers.
3. **Game context:** Genshin Impact. Use official Thai client terminology when known.
4. **Place names:** Transliteration (ทับศัพท์) is OK — e.g. 蒙德 → มอนด์สตัด, 璃月 → ลิเยว่.
5. **Characters/items:** Check [Genshin Wiki TH](https://genshin-impact.fandom.com/th/) or English wiki + Thai game client.
6. **Tone:** Clear UI copy — short labels stay short; tooltips can be slightly longer.
7. **OCR-related strings** (if batch notes say so): Must match text shown in Thai game UI screenshots; do not paraphrase.
8. **Do not translate:** Pure English technical tokens, URLs, regex patterns, log format strings.
9. **Ambiguous:** Add `"_note_<first 20 chars of key>": "reason"` only if truly blocked — prefer best guess.

## Input

```json
(paste batch-NNN-th.json contents)
```

## Output

Same JSON object with all values translated to Thai.
