# Extra rules for Serilog / status log string batches

Apply in addition to agent_prompt_th.md:

1. These are **runtime log / status overlay** strings, not settings UI.
2. Preserve exactly: Serilog placeholders `{Name}`, `{Msg}`, `{0}`, `{Text}`, `{Enabled}`, etc.; symbols `◎` `○` `*` `→` `>>>` `==========`; numbers; quotes `“”` `《》`.
3. Keep Genshin proper names in **English** (Hu Tao, Fontaine, Liyue, fish species, character names).
4. Match Thai game UI for generic terms (钓鱼→ตกปลา, 剧情→เนื้อเรื่อง/บทสนทนา by context, 邀约→นัดหมาย/Hangout, 传送→teleport/วาร์ป).
5. Short status labels stay short (拾取→เก็บ, 剧情→บท, 邀约→นัด, 钓鱼→ตกปลา, 传送→วาร์ป).
6. Tone: clear operational log messages — concise Thai.
7. Do not invent placeholders; keep every `{...}` token unchanged.
8. FontAwesome / icon prefixes like literal `\uf256` or Unicode private-use chars: keep the prefix, translate only the Chinese word after it.
