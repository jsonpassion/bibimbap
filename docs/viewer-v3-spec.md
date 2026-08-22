# BIBIMBAP Trace Viewer v3 — FINAL SPEC ("원장 + 레이스")

Winner base: **ledger** (combined judge score 74 vs race 68 / waterfall 68; zero fatal flaws from 2 of 3 judges; only candidate that passes the 30-second read with no keypress).
Grafted in: race's Before/After single-clock mechanics + SPLIT delta chips + 17px per-event caption + hero sentence; waterfall's `← 로그 #k` source links, live checksum, rubric rail, "병렬 웨이브 → 실제 직렬" claim, robust `derive()`, `<input type=file>` fallback, F-zoom.
Output file: `viz/viewer-v3.html` — single file, vanilla JS + SVG, no CDN, Google Fonts only, traces inlined, `normalizeRaw` + drop ingestion kept from v2.

Verified data facts every number below is derived from (do not hard-code; these are the acceptance values):

| | 단독 (baseline) | run-001 v1 (Before) | run-002 v3.2 | run-003 v3.5 (After) |
|---|---|---|---|---|
| tokens (prompt+completion) | 617 (131+486) | 26,808 (24,446+2,362) | 1,564 (1,445+119) | 1,645 (1,501+144) |
| ratio vs 단독 | 1 | 43.45× → show "43.4×" | 2.53× → "2.5×" | 2.67× → "2.7×" |
| input share | 21% | 91.2% | 92.4% | 91.2% |
| seconds | 5.09 | 60.2 | 7.9 | 16.0 |
| plan-ready t | — | 20.20 | 4.88 | 12.47 |
| first call t / last call t | — | 21.47 / 59.41 | 5.93 / 7.10 | 14.26 / 15.18 |
| calls / tasks (dup) | 1 / — | 28 / 3 (2) | 2 / 1 (0) | 2 / 1 (0) |
| task subtotals (tok, calls, event-derived s) | — | #1 10,629·11·13.64s · #2 4,330·6·6.85s · #3 11,849·11·18.10s | 1,564·2·2.22s | 1,645·2·2.71s |
| tasks[].durationSec (from wave start 20.21) | — | 13.6 / 20.8 / 39.2 | 2.2 | 2.7 |
| agents defined / with calls | — | 8 / 1 (+planner) | 5 / 1 | 5 / 1 |
| planner model | — | gpt-oss-120b | gpt-oss-120b | Qwen3-32B-FP8 |
| rejectedPlansBefore | — | 6 | 10 | 17 |
| events | — | 49 | 13 | 13 |
| token-usage-update session cum (NOT run total) | — | 10,629 / 14,959 / 26,808 | 78,092 | 4,208 |

SPLIT deltas (After=run-003 vs Before=run-001): 계획 완료 −7.73s · 첫 호출 −7.21s · 완주 −44.2s · 토큰 −25,163 (−93.9% → "−94%", ÷16.3).

---

## 0. One-screen story (what the judge sees in 3 / 10 / 30 seconds)

- **3 s**: `43.4× → 2.7×` at 180 px, sentence `관측할 수 있으면 줄일 수 있다` under it.
- **10 s**: the sawtooth in 01 — 28 bars whose height climbs 487→1,277 three times, two of the three task bands hatched red; 617 dashed line that is almost invisible next to 26,808.
- **30 s** (presenter presses `C`, `Space`): three runs race on one 0–60.2 s clock; v3.5 plants a 🏁 at 16.0 s while v1 is still hatching duplicate task #2; SPLIT chips light up `완주 −44.2s · 토큰 −94%`.
- Everything else (ledger rows, judgments, footnote) is below the fold for the expo visitor who scrolls and clicks.

---

## 1. Information architecture (single scroll, sections 00–05, one sticky header)

```
┌ STICKY HEADER (≈150 px) ───────────────────────────────────────────────────┐
│ row1: BIBIMBAP · 원장   [v1 · 8 agents][v3.2 · gpt-oss][v3.5 · Qwen3][+드롭]  │
│       [ ] 비교·레이스 (C)   ⟲ ▶ [자동|1×|4×|10×]   00 01 02 03 04 05 (섹션)   │
│       counter: 16.0s / 16.0s · 호출 2 · 1,645 tok · 단독의 2.7×  ·  이벤트 13/13 │
│ row2: SCRUBBER svg 1100×64 — cumulative-token area IS the slider track       │
│ row3: CAPTION 17px rule-generated sentence · sub 12px "#7 모델 호출 — …"      │
│       [⏳ 플래너 생각 중 · 12.5s · 건너뛰기 →]  (only while playing in a gap)  │
│ row4 (cmp only): SPLIT chips  계획 −7.7s · 첫 호출 −7.2s · 완주 −44.2s · 토큰 −94% │
└────────────────────────────────────────────────────────────────────────────┘
00 HERO      43.4× → 2.7×  + sentence + exact-figure caption + 4 shared linear bars
01 시간      phase bands · task bands (hatch) · SAWTOOTH call bars · cum staircase · markers
             (cmp ON → 3 stacked lanes on one 0–60.2 s axis + per-lane status chip = RACE)
02 에이전트  one lane per defined agent (8 / 5), idle lanes dimmed "호출 0 · 유휴"
03 원장      one row per log event (49) grouped by task with subtotals → "= 합계" → 단독 → 배율
             row click → inline 해석 | 원본 panel (with ← 로그 #k links + checksum)
04 판단      rule-derived flag cards (⏳ ?? ? ?! ✓ + 병렬→직렬) · comparison table · 91% sentence
05 각주      있음/없음 two columns · calibration reliability chart · methods line from data
FOOTER RAIL  6 rubric chips (hover = spotlight) · key legend · drop hint + <input type=file>
```

Page height target at 1280 px: ≈2,600 px with run-001 ledger groups collapsed (see §4.3), ≈1,900 px for run-003.

### 1.1 Sticky header
- `#runs` segmented buttons from `ORDER` (run-001, run-002, run-003, then dropped runs). Label = `RUNS[k].meta.version` shortened: `v1 · 8 agents`, `v3.2 · gpt-oss`, `v3.5 · Qwen3`. **Never** derive labels with `replace('run-00','v')`.
- `#cmp` checkbox "비교 · 레이스" — **default OFF** (stage frame needs wide sawtooth bars).
- `#sections` nav chips `00 01 02 03 04 05` → `scrollIntoView({block:'start'})` under the sticky header (`scroll-margin-top: 160px` on every `section`).
- `#counter` (mono, tabular): `{f1(tNow)}s / {f1(dur)}s · 호출 {n} · {fmt(tok)} tok · 단독의 {ratio}× · 이벤트 {i}/{N}` — this is the ONLY place the live (playhead-dependent) ratio appears.
- `#scrub` SVG (see §3.1). `#caption` 17px (flag caption if the last flagged event ≤ tNow was within the last 1 event, else the per-event rule caption — see §5.2), `#sub` 12px `#{i+1} {e.summary}`.
- `#skip` button appears only while `playing && nextEvent.t − tNow > 3`.
- `#splits` row rendered only when `cmp` (see §6.3).

### 1.2 Default state on load
`cur = 'run-003'`, `cmp = false`, `tNow = D.dur` (End frame: everything lit, hero at totals), `sel = -1`, not playing. This is the expo landing frame and the PT opening frame.

---

## 2. Data layer (schema → derived model)

### 2.1 Inputs (unchanged schema)
`trace.json = {meta, agents[], tasks[], events[], tokens, insights, baseline, calibration[]}`; `events[i] = {t, ts, type, phase, agentId, agentName, summary, detail, taskId?, tokens?{prompt,completion,cumPrompt,cumCompletion}}`.
Raw drop: `events.jsonl` (AI:GO `squad:*` eventTypes, cumulative promptTokens/completionTokens) + `.squad.json` → `normalizeRaw(text, squad)` from v2 (keep verbatim, plus the 3 fixes in §2.4).

### 2.2 Inline the three runs
```html
<script type="application/json" id="run-001">…run-001.json…</script>  (×3, ~38 KB)
```
`RUNS[k] = JSON.parse(document.getElementById(k).textContent)`; keep `fetch('traces/'+k+'.json')` only as a dev fallback when the inline block is missing. The file must open by double-click under `file://`.

### 2.3 `derive(T)` → `D` (cache: `RUNS[k].D ||= derive(RUNS[k])`; never mutate another run's events while rendering `cur`)
Store derived per-event data in parallel arrays keyed by index (`D.flag[i]`, `D.task[i]`, `D.k[i]`), not on the event objects → `JSON.stringify(events[i])` stays clean for the 원본 tab and no cyclic refs.

| derived | rule (exact) |
|---|---|
| `dur` | `Math.max(T.meta?.durationSec || 0, events.at(-1).t)` |
| `plan, exec0, agg, fin` | first `plan-ready`, `execution-started`, `aggregation-started`, `execution-completed` |
| phases | planning `[0, plan.t]`, execution `[plan.t, agg.t ?? dur]`, aggregation `[agg.t, fin.t ?? dur]` |
| `calls[]` | events with `type==='execution-token-usage'` and `tokens` |
| per-call Δ | already `tokens.prompt/completion` (v2 normalizeRaw restores Δ from cumulative: `dp = cp − prevCp`) |
| cumulative at i | `cum[i] = Σ_{calls j ≤ i} prompt+completion` (own running sum; cross-check vs `tokens.cumPrompt+cumCompletion` → checksum claim) |
| `total, prompt, completion` | sums over `calls` (do **not** read `T.tokens.*` for charts; show `T.tokens.total` in methods as "trace 합계 = N ✓ 일치" when present) |
| `spans[]` (tasks) | open on `task-status-changed` whose summary/detail contains `in_progress` (`{n, i0, t0, taskId, agentId, calls:[], title}`); every subsequent `execution-token-usage` joins the open span (`D.task[i]=n`, `D.k[i]=position`); close on `task-completed` with same `taskId` (fallback: next `task-completed`) → `{t1, i1, dur=t1−t0, first=prompt of call 1, last=prompt of last call, peak=max prompt}`. Title: `T.tasks.find(x=>x.id===taskId)?.title` → else the `'…'` in summary → else `'task'`. |
| `wallDur` per span | `T.tasks.find(id).durationSec` (may be null for dropped logs) |
| `serialClaim` | if a `task-wave-started` lists ≥2 taskIds and spans do not overlap in `[t0,t1]` → `"웨이브 1: 태스크 N개 '병렬' → 실제 직렬 (겹침 0)"`; if `wallDur` exists and `wallDur − span.dur > 1 s` → `"tasks[].durationSec {wallDur}s는 웨이브 시작 기준, 이벤트 기준 {dur}s — 앞 태스크를 기다렸다"` |
| `dup` per span | key `title + '|' + agentId`; the 2nd+ occurrence of a key is `dup=true` (so run-001 spans #2, #3) — matches `insights.duplicateTasks` (assert equal when present) |
| `runs` (agent lanes) | pairs of `agent-state-changed` running→idle per agentId → `[t0,t1,'execution']`; planner lane gets `[0,plan.t,'planning']` and `[agg.t,fin.t,'aggregation']` |
| `byAgent` | calls per agentId `{calls, prompt, completion}`; `active = Object.keys(byAgent).length`; label `플래너 1 + 호출 {active} / {agents.length}` |
| `gaps[]` | consecutive events with `Δt > 3 s` → `{t0,t1}` (run-001: 0→20.20, 51.43→56.50; run-003: 0→12.47) |
| `base` | `T.baseline ? {tok: prompt+completion, s: seconds, correct, item, model} : null` — when null every ratio renders `—` and the 617 line is omitted |
| `flags` | see §5.1 |
| `checkpoints` | `{plan: plan.t, firstCall: calls[0].t, finish: fin.t, tokens: total}` — used by SPLIT |

### 2.4 `normalizeRaw` fixes (keep v2 logic, add)
1. `task-status-changed`: when `cur` (last running agent) is null, take the agentId from the **next** `agent-state-changed(running)` in the raw stream; also store `ev.detail = {oldStatus, newStatus, taskId}` and `ev.taskId`.
2. Titles: after the loop, patch every `task-status-changed` summary with `tasks[taskId].title` (from `task-completed.taskTitle`) so spans read `SOLVE` not `task`.
3. `meta.rejectedPlansBefore` already counted — keep; set `insights.duplicateTasks` from the dup rule above; `baseline`/`calibration` borrowed from current `T` **and** `meta.borrowedBaseline = true` → hero caption shows `⚠ 기준 617은 {base.item}의 단독 값 — 이 로그의 문항과 다를 수 있음`.
4. `ingest(file)`: wrap in `try/catch` → `toast('적재 실패: ' + err.message)`; detect squad by content (`j.config || j.agents`) not just filename; support `<input type=file multiple>` in the footer label.
5. `dragover` → `body.drag` class → full-page dashed amber overlay `여기에 events.jsonl + .squad.json 또는 trace.json`.

---

## 3. Visual mappings (exact)

Global SVG width `W=1100` (viewBox units; `width:100%`), left gutter `L=150`, right gutter `R=110`.
`xMax = cmp ? max(ORDER.map(dur)) : D.dur`; `X(t) = L + t/xMax·(W−L−R)`.
`tokMax = cmp ? max(all totals, base.tok) : max(D.total, base.tok)`.
Per-call scale (fixed across runs): `callMax = cmp ? max over all runs of (prompt+completion) : max over D.calls` (run-001: 1,490 = 1,175+315).

### 3.1 Scrubber (`#scrub`, 1100×64)
- Area path: staircase of `cum` over `X(t)` from `X(0)` to `X(dur)`, fill `--ex` .25, stroke 1.5.
- cmp ON: other runs' staircases as dashed `--dim` ghosts.
- Baseline: dashed `--ag` horizontal line at `y(base.tok)` with left label `단독 617`.
- Bottom 5 px phase strip (planning amber / execution blue / aggregation green).
- Playhead `<line class="ph">` full height, `--acc` 1.5 px. Right-top label `{fmt(total)} tok`.
- Pointer: `pointerdown/move` on the svg → `t = (x−L)/(W−L−R)·xMax` → `setT(t)`; snap to markers (plan, task ends, agg, fin) when within 6 px. A visually-hidden `<input type=range step=0.01>` mirrors `tNow` for keyboard/a11y.

### 3.2 00 Hero
```
 [v1 · Before]                      [v3.5 · After]
   43.4×          →                    2.7×
 (180px, 800)   (48px dim)        (180px, 800, --ag)
 관측할 수 있으면 줄일 수 있다   (28px, weight 600)
 26,808 / 617 = 43.45 · 1,645 / 617 = 2.67 · 같은 문항 math-visible-0001 · 정답 여부: 외부 채점(baseline.correct=true) · 스쿼드 답 텍스트는 로그 미기록  (14px dim)
 herobar (1100×110): 4 rows — 단독 617 (--ag) / v1 26,808 / v3.2 1,564 / v3.5 1,645; linear, 0-based, shared max=26,808; 617 as dashed vertical rule; current run row bright, others .4 (cmp OFF: 단독 + Before + current only)
```
- Before slot = `ORDER[0]` (run-001) **fixed**; After slot = `cur`. If `cur === ORDER[0]` the After slot shows `—` with sub-label `After 런 선택: 2 / 3`.
- Hero numbers are **frozen at run totals** (never follow the playhead). Run switch morphs the After number over 1.2 s easeOutCubic (`setRatio`). This is the stage move: key `3`.
- Right slot sub-label: `{label} · 플래너 {planner.model}` (shows `Qwen3-32B-FP8`).
- Optional single muted line (toggle in 05): `26,808 tok ≈ RNGD 1장 기준 ~{26808/3000}s · ~{…}J (공개 수치 3,000 tok/s · 180 W 가정 — 측정 아님)`.

### 3.3 01 시간 (`#tl`, single run: 1100×230)
| element | mapping |
|---|---|
| phase band (y 6–24) | rect `X(a)→X(b)`, fill phase color .18 + 3 px top rule; label `계획 20.2s` if width > 70 px, `계획` if > 22 px, else none |
| markers | vertical 1 px lines at plan.t, each span.t1, agg.t, fin.t; labels staggered on 3 rows (y 36/48/60), `text-anchor` flips to `end` when `X(t) > W−R` (fixes the 41.0/59.4 collision) |
| task band (y 66–84) | rect per span; fill `--ex` .25; `dup` → `url(#hatch)` red + `??` badge; label `SOLVE #1 · 13.6s · 11회` |
| **sawtooth call bars** (base y0=200, max height 120) | x = `X(call.t) − bw/2`, `bw = max(6, min(14, (W−L−R)/xMax·0.6))`; prompt segment height `prompt/callMax·120` fill `--prompt`, completion stacked on top fill `--comp`; dup-task bars get a hatch overlay at .6; `data-t`, `data-i`; bar ≥ 3rd call of a span has a 2 px `--warn` top cap |
| cumulative staircase | polyline of `cum` on right axis (0 → tokMax, label `26,808` at top right, `617` dashed `--ag` line) |
| gap glyph | for each `gaps[]` entry a thin `⏳ 20.2s 침묵` label centered in the gap |
| legend (y 224) | `■ 입력(컨텍스트 재전송)  ■ 출력  ▨ 중복 태스크 = 단독에 없던 비용  ┄ 단독 617` |

cmp ON → see §6 (RACE lanes replace this svg).

### 3.4 02 에이전트 (`#ln`, height = 34·agents + 40)
One row per `T.agents` entry in file order (planner first). Left: name 13 px + model chip 11 px (`Qwen3-32B-FP8 · 플래너`). Bars from `runs[agentId]`: planning amber / execution blue / aggregation green; dup spans hatched; call ticks 1.5 px white at `X(call.t)`. Right gutter badge mono `37.7s · 28회 · 26,808 tok` (execution sum). Rows with no `runs` and no calls: opacity .35, badge `호출 0 · 유휴`. Header line above: `정의 8 · 계획 1 · 호출 1 · 유휴 6`.

### 3.5 03 원장 (`#rows`, mono 13 px, 7-column grid `# · t · 에이전트 · 항목 · 입력 · 출력 · 누적`)
- Every event is one row (`data-i`, `data-t`). Call rows: numbers in tabular mono, `+Δ` vs previous call in the same task shown after 입력 (`487`, `503 (+16)`, `686 (+183)` …). Status rows: dim text, 항목 = summary.
- Rows are grouped: `계획` (events before exec0) / one `<details>` per span / `취합`. Group header row (always visible) = subtotal: `소계 SOLVE #2 중복 · 6회 · 6.9s · 입력 487→758 · 4,330 tok` + flag badges of events inside. **Default**: details open when `events.length ≤ 20`, else closed (run-001 opens with three subtotal lines; selecting/seeking any event inside opens its group).
- After the last group: `입력 소계 24,446 (91.2%)` · `출력 소계 2,362 (8.8%)` · dashed rule · `= 합계 26,808 tok` (bold, 1 px top+bottom rule) · `단독 gpt-oss-120b 617 tok · 5.09s · baseline 필드` · `배율 43.4× · 시간 11.8×` · `trace.tokens.total 26,808 ✓ 일치`.
- Badges: `⏳` gap, `??` dup start, `?` over-call, `?!` ctx growth, `✓` done — class `b-{flag}`.
- Row click → `select(i)`: playhead seeks to `e.t`, row highlighted, inline panel opens directly under the row (§4.1). Click same row again closes.

### 3.6 04 판단
- Flag cards (from `D.flags`, order by t): badge + caption (§5.2) + `t=20.2s · 이벤트 #2 · plan-ready` + `← 로그 #2` ; click → `select(i, scroll=true)`.
- Comparison table (`#cmpt`): header `기준: 단독 gpt-oss-120b · 같은 문항 math-visible-0001 (Weave: 최좌측 = 기준)`; columns 단독 · v1 · v3.2 · v3.5 (+drops); rows: 토큰 / 시간 (s, **f1**) / 모델 호출 / 태스크 (중복) / 입력 비중 / 에이전트 (계획+호출 / 정의) / 플래너 모델 / 계획 전 거절 횟수 / 계획 시간 (plan.t) / 답 텍스트 (`로그 미기록` in every column). Numeric cells carry a delta chip vs 단독; click anywhere on the table cycles `×배 → 절대차 → %` (`dmode`). Worse-than-baseline → chip red tint; better → green tint.
- Under the table, one 15 px sentence computed from data: `입력 비중은 v1 91.2% · v3.5 91.2% — 줄어든 것은 비중이 아니라 컨텍스트를 다시 보낸 횟수 28 → 2. v3.5 플래너(Qwen3-32B-FP8)는 v3.2보다 7.6s 느리지만(12.5s vs 4.9s) 태스크 수가 1로 고정됐다 (거절 17회 뒤).` Template with slots; sentence omitted when fewer than 2 runs loaded.

### 3.7 05 각주 (two columns + chart + methods)
있음: `토큰 누적치 (execution-token-usage → 호출별 Δ 복원)` · `상태 전이 (agent-state-changed · task-status-changed)` · `타임스탬프 · 계획 태스크 수 · 거절된 계획 수` · `단독 베이스라인 (baseline 필드, 외부 채점 러너)`.
없음 (dashed border, `--bad` bullet): `솔버의 답 텍스트 — AI:GO가 저장하지 않음 (로그 형식 고정, 운영진 확인)` · `추론 내용 · 프롬프트 본문` · `스쿼드 답의 정답 여부 — 로그에 없음. 이 뷰어는 맞았는지 말하지 않는다; 정답은 채점 러너(baseline.correct)로만 표시` · `token-usage-update 의 세션 누적치(78,092 / 4,208)는 이 실행의 합계가 아님 → 차트에 쓰지 않음`.
Calibration: reuse v2 renderer at 520×220, drop the `n/n` label when `n < 5`, bubble r = `3+√n·1.6`, caption `확신도 10 → 36/36 정답 (140문항, 채점 러너) · 확신도가 낮은 문항만 재검토하면 된다 = 원칙 0의 근거`.
Methods line (12 px mono, generated): `methods · 26,808 = Σ execution-token-usage.prompt+completion (호출 28회, run-001, trace.json) · 입력 24,446 / 출력 2,362 · 617 = baseline.prompt+completion (furiosa-ai/gpt-oss-120b, 5.09s, correct=true) · 배율 26,808/617 = 43.45 · 중복 = 같은 제목+같은 에이전트 태스크 −1 · 호출별 Δ = cumPrompt[i]−cumPrompt[i−1] · 태스크 구간 = task-status-changed(in_progress) → task-completed · 2026-08-22`.

### 3.8 Footer rubric rail
Six chips; `hover`/focus adds `body[data-spot=observability]` etc. CSS: `body[data-spot] [data-rubric]:not([data-rubric~=X]) {opacity:.15}`. Chip text is the element name only; the definition sits in a `title` tooltip and in `#railDef` (one line, no citations on screen).

---

## 4. Interactions

### 4.1 Click-to-explain (inline panel under a ledger row; also opened by any SVG bar/band/tick/flag card click via `data-i`)
Header: `#7 execution-token-usage · Math-Solver · t=21.47s · 2026-08-22T04:53:16Z`.
Metric strip (4 big numbers, type-dependent): call → `입력 487 · 출력 56 · 누적 543 · Δ입력 vs 직전 —`; task-status → `태스크 #2 · 중복 · 이전 #1 완료 33.85s`; plan-ready → `계획 20.2s · 태스크 3 · 지시문 1 · 거절 6`.
Tabs `해석 | 원본`:
- 해석 = fixed 6 fields (`시각 · 에이전트(모델) · 타입 · 토큰 · 상태 전이 · 출력 텍스트`) — missing ones rendered with dashed border and `로그 미제공 (AI:GO 미저장)`; then **claim cards**, each with a `← 로그 #i, #j` link that seeks/selects:
  - `입력 Δ = 686 − 503 = +183 → 히스토리 누적 (컨텍스트 재전송)` ← #8, #7
  - `누적 검산 Σ(prompt+completion) #6..#8 = 1,822 · 로그 cumPrompt+cumCompletion = 1,822 ✓ 일치`
  - `누적 1,822 = 단독 617의 3.0×`
  - `같은 태스크 3번째 호출 — 단독 모델은 1회` (k ≥ 3)
  - task-status dup: `중복 판정: title 'SOLVE' + agentId 동일 → #1(완료 33.85s)의 반복` ← #4, #19
  - plan-ready: `태스크 3개 · 웨이브 1 · 지시문 "task count must be exactly 1" → 중복 2 · 이 계획 전 거절 6회` ← #1
  - task-completed: `tasks[].durationSec 39.2s vs 이벤트 기준 18.1s — 웨이브 시작(20.21s)부터 측정: "병렬" 웨이브였지만 직렬 처리` ← #3, #31, #46
  - token-usage-update: `세션 누적 78,092 ≠ 이 실행 합계 1,564 → 차트에 쓰지 않음` 
- 원본 = `JSON.stringify(T.events[i], null, 2)` (event as loaded; no derived keys because derived data lives in `D.*[i]`).

### 4.2 Playhead / replay
- `setT(t)`: clamp, move every `.ph` line (scrub, 01, 02, race lanes), toggle `.future` (opacity .22) on all `[data-t] > tNow`, recompute counter, caption, skip chip, SPLIT chips, lane status chips. Hero untouched.
- `play()`: rAF loop, `dt ≤ 0.1 s`; speed `auto` = 15× inside `gaps[]`, else 2.5× (run-001 ≈ 16 s wall; run-003 ≈ 2 s) / 1× / 4× / 10×. Ends at `dur`, stays on final frame. `⟲`/`R` → `setT(0)` and stop.
- Skip chip → `setT(nextEvent.t − 0.05)`.
- Idle reset: any input resets a 45 s timer; on fire → `stop(); cmp=false; show('run-003'); setT(dur); window.scrollTo(0,0)`.
- `document.hidden` → pause (note in keys legend: 창이 가려지면 재생이 멈춤).

### 4.3 Keyboard (one `keydown` switch; ignored when focus is in an input)
| key | action |
|---|---|
| `Space` | play / pause |
| `←` / `→` | select previous / next event (opens its group, seeks) |
| `N` / `Shift+N` | next / previous flagged event (the 5–7-stop tour) |
| `Home` / `End` | t=0 / t=dur |
| `R` | reset to 0 (stop) |
| `1`…`9` | switch run by `ORDER` index (hero After slot morphs) |
| `C` | toggle 비교·레이스 |
| `F` | zoom 01 to the selected task span (`xWin=[t0−0.5, t1+0.5]`), `Esc` unzoom; breadcrumb chip `전체 › SOLVE #1` in the section title |
| `Shift+1`…`Shift+6` (by `e.code`), `Tab`/`Shift+Tab` | jump to section 00–05 |
| `Esc` | close inline panel / unzoom |
| `?` | toggle key legend |

### 4.4 Mouse
Scrubber drag; click on any bar/band/tick/row/card (`data-i`) → select; hover `<title>` tooltips on call bars (`태스크 #1 · 3번째 호출 · 입력 686 / 출력 44 · 누적 1,822`); comparison table click cycles delta mode; rubric chips hover spotlight; `#sections` chips scroll; drop anywhere; `<input type=file multiple>` in footer.

---

## 5. Rules (no hand-written per-run text)

### 5.1 Flags (`D.flags[i]`)
| flag | badge | rule |
|---|---|---|
| gap | ⏳ | `plan-ready` with `plan.t > 5` (one per run) — plus any other gap > 5 s gets a timeline glyph only (no card) |
| dup | ?? | `task-status-changed(in_progress)` opening a span with `dup=true` |
| over | ? | the 3rd call of the **first** span that has ≥3 calls (one card; later spans' 3rd calls get the bar cap only) |
| ctx | ?! | last call of every span with ≥2 calls where `last > first` |
| serial | ⇉ | first `task-completed` when `serialClaim` is non-null (run-001 only) |
| done | ✓ | `execution-completed` |
run-001 → 9 stops in t order: ⏳(plan 20.2s) · ?!(#1 last call, 487→1,277) · ⇉(#1 completed, serial claim) · ??(#2 start) · ?!(#2, 487→758) · ??(#3 start) · ?(3rd call — flagged on span #1 only, so it actually sits at event #8 inside task #1) · ?!(#3, 522→1,196) · ✓. ctx is restricted to spans with ≥3 calls to avoid badge inflation. run-003 → ⏳ ✓ only (`692 > 809` is false, so no ?!).

### 5.2 Captions (17 px line, per event, template slots from data)
- planning-started → `플래너 {model}가 생각 중 — 이벤트 0개 구간`
- plan-ready(gap) → `플래너({model})가 {t}s 침묵 후 태스크 {n}개 — 지시문은 1개{dup? (중복 d)}`
- task-status dup → `{title} #{n} 시작 — 이미 끝난 태스크의 반복, 컨텍스트 재전송이 처음부터 다시`
- call k=1 → `태스크 #{n} 첫 호출 — 입력 {p}`; k=2 → `2번째 호출 — 입력 {p} (+Δ)`; k≥3 → `같은 태스크 {k}번째 호출 — 입력 {prev}→{p} (+Δ): 컨텍스트가 다시 전송됐다 · 누적 {cum}`
- ctx → `태스크 #{n}: 호출 {k}회, 입력 {first}→{last} — 같은 대화를 매번 다시 보냈다`
- task-completed → `{title} #{n} 완료 · {calls}회 · {tok} tok · {dur}s` (+ serial claim once)
- token-usage-update → `세션 누적 {v} (이 실행 합계 아님)`
- aggregation-started → `취합 시작 — 플래너가 {n}개 결과 합성`
- done → `합계 {total} tok = 단독 {base}의 {r}× · {dur}s vs {base.s}s`
- no baseline → drop the `단독 …` clause.

---

## 6. Before/After RACE mechanics (cmp ON)

1. **One clock**: `tNow` is shared; `xMax = 60.2` (max dur across `ORDER`), `tokMax = 26,808`, `callMax = 1,490`. No normalization.
2. **Section 01 becomes lanes** (`#tl` height = 120·runs + 40): one lane per run in `ORDER` (Before first), each lane = compact phase band (8 px) + task bands (hatch dup) + sawtooth bars on the shared call scale (`bw ≥ 6`) + cumulative staircase on the shared token axis (right gutter shared across lanes so 26,808 towers over 1,645). Left shell: `v1 · Before · 플래너 gpt-oss-120b · 에이전트 8 / 호출 1`. Current run lane has the bright fill; others .6.
3. **Lane status chip** (right gutter, updated in `setT`): before finish `실행 중 · {tok} tok · 호출 {k}`; when `tNow ≥ fin.t` → `🏁 완주 16.0s · 1,645 tok · 2.7×` (chip turns `--ag`). Past `fin.t` the lane freezes (no future bars anyway).
4. **Baseline lane** (thin, top): a single marker at 5.09 s with `🏁 단독 617 tok · 정답(외부 채점)`.
5. **SPLIT chips** under the scrubber, After = `cur` vs Before = `ORDER[0]` (if `cur === ORDER[0]`, After = `ORDER.at(-1)`): `계획 완료 {Δplan}s`, `첫 호출 {Δfirst}s`, `완주 {Δfinish}s`, `토큰 {−25,163} (−94%)`; each lights up only when `tNow ≥ max(tBefore, tAfter)` of that checkpoint (token chip at both finishes); green if improvement, red if worse (e.g. v3.5 vs v3.2 계획 +7.6s is red — shown honestly). Token chip click cycles `÷16.3 → −25,163 → −94%`.
6. **Scrubber** shows the current run's area + ghosts of the others; **hero** adds all 4 bars.
7. **Stage script**: `3` (hero morph) → `C` → `Space` (auto ≈ 16 s): v3.5 plants 🏁 at 16.0 s while v1 is in hatched task #2; `완주 −44.2s` lights at 60.2 s; end frame stays. `N` tours the 7 flagged moments if time is short.
8. Dropped runs join the race automatically (ORDER push); lanes > 4 → lane height 90.

---

## 7. Rubric pointer table (presenter: hover the rail chip; the rest of the page dims)

| axis | on-screen element (`data-rubric`) | one-sentence defense |
|---|---|---|
| Observability | scrubber area + 01 sawtooth + 02 idle lanes | 로그의 외부 출력(누적 토큰 카운터·상태 전이)만으로 루프 반복 수·컨텍스트 성장·8명 중 1명 가동이라는 내부 상태를 복원한다 — 원본 events.jsonl을 드롭해도 같은 그림. |
| Interpretability | 17 px caption line + 03 subtotal rows | 플레이헤드가 지나는 매 이벤트를 사람 문장 한 줄로 바꾸고, 태스크마다 '6회 · 입력 487→758' 소계로 읽게 한다. |
| Traceability | 03 ledger (49 rows) + 원본 tab + `← 로그 #k` links + methods line | 모든 숫자는 이벤트 인덱스에 묶여 클릭 한 번에 원본 JSON으로 가고, 합계는 화면에서 검산된다 (10,629+4,330+11,849=26,808). |
| Explainability | 04 flag cards + inline claim cards + hatched dup bands | 왜 43×인가: 컨텍스트를 28번 보냈고(Δ입력 +183…) 그중 두 태스크는 통째로 중복 — 규칙으로만 생성되어 낯선 로그에도 같은 설명. |
| Clarity | 00 hero (한 숫자 + 한 문장) + 0-based shared linear bars | 3초 안에 43.4× → 2.7×, 잘린 축·로그 축·그래프·버블 없음, 색은 페이즈·입출력·낭비에만. |
| Insightfulness | RACE lanes + SPLIT chips + comparison table sentence + calibration | v3.5가 16초에 완주할 때 v1은 중복 태스크를 돌고 있고, 입력 비중은 91%로 같으며 바뀐 건 재전송 횟수 28→2; Qwen3 플래너는 느리지만 태스크 수를 고정했다. |

---

## 8. Color / typography (dark, projector)

```css
:root{
  --bg:#0c0d10; --panel:#111318; --line:#22262e; --fg:#e6e9ef; --dim:#98a0ae; --mute:#5c6472;
  --pl:#e8b44a;   /* planning */      --ex:#5b9cf5;  /* execution / completion bars */
  --prompt:#3a4f80; /* input segment */ --comp:#8fe3ff; /* output segment */
  --ag:#3ddc97;   /* aggregation + 단독 baseline + improvement */
  --bad:#ff6b6b;  /* hatch / dup / worse */  --warn:#ffa94d; /* over-call cap, ?! */
  --acc:#ffffff;  /* playhead, selection */
}
```
- Contrast: `--dim` on `--bg` ≥ 5.5:1; idle lanes use `--dim` at .35 opacity but badge text stays `--dim` (not `--mute`).
- Hatch: `<pattern id=hatch width=6 height=6 patternTransform=rotate(45)><rect width=2 height=6 fill=var(--bad)/></pattern>`.
- Fonts: body `14px/1.5 -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif`; numbers/ledger `"JetBrains Mono", "SF Mono", Menlo, monospace` via `<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap">` (system fallback works offline); `font-variant-numeric: tabular-nums` everywhere numbers appear.
- Sizes: hero 180 px / 800 (After slot same; `clamp(96px, 14vw, 180px)`), sentence 28 px / 600, caption 17 px, section h2 15 px + `em` 12 px dim, ledger 13 px, **all SVG text ≥ 12 px** (lane model chips 11 px minimum), table 13 px, methods 12 px.
- Flat surfaces, 1 px separators, no gradients/glow/shadows/emoji in headers (🏁 ⏳ are data badges, allowed). Motion only: playhead, hero morph (1.2 s), `.future` opacity transition 120 ms, ledger print stagger 40 ms on first render of a run (optional).

---

## 9. Copy (Korean UI, English sub where useful)

- Title: `BIBIMBAP · 원장` / sub `Squad Trace Ledger · run replay`
- Runs: `v1 · 8 agents` / `v3.2 · gpt-oss` / `v3.5 · Qwen3` / dropped: `드롭 {n}`
- Controls: `비교 · 레이스 (C)` · `⟲` · `▶`/`⏸` · `자동 (≈16s)` `1×` `4×` `10×`
- Skip chip: `⏳ 플래너 생각 중 · {n}s · 건너뛰기 →`
- Hero sentence: `관측할 수 있으면 줄일 수 있다` / `If you can observe it, you can cut it.`
- Section titles: `00 결과` / `01 시간 — 호출 1개 = 막대 1개, 높이 = 입력 토큰(컨텍스트 재전송)` / `02 에이전트 — 정의된 에이전트 전부, 유휴도 보인다` / `03 원장 — 로그 한 줄 = 원장 한 줄, 누르면 해석과 원본` / `04 판단 — 규칙으로만 도출, 손으로 쓴 문장 없음` / `05 각주 — 이 로그에 있는 것과 없는 것`
- Legend: `빗금 = 단독 모델에 없던 비용 (중복 태스크)` · `┄ 단독 617 = 기준선`
- Status chips: `실행 중 · {tok} tok · 호출 {k}` / `🏁 완주 {s}s · {tok} tok · {r}×`
- SPLIT: `계획 완료 −7.7s` · `첫 호출 −7.2s` · `완주 −44.2s` · `토큰 −25,163 (−94%)`
- Panel tabs: `해석` / `원본 (events[{i}])`; missing field: `로그 미제공 (AI:GO 미저장)`
- Toasts: `{k}: 이벤트 {N} → 호출 {M} · 태스크 {K} · 사전 가공 없이 파생` / `스쿼드 설정 적재됨 — 이제 events.jsonl을 드롭하세요` / `적재 실패: {msg}` / `⚠ 기준 617은 math-visible-0001 단독 값 — 문항 불일치 가능`
- Keys legend: `Space 재생 · ←/→ 이벤트 · N 다음 표시 · 1/2/3 런 · C 레이스 · F 태스크 확대 · R 처음 · Shift+1…6 섹션 · 드롭: events.jsonl + .squad.json / trace.json`
- Rail chips: `Observability → 스크러버·톱니·유휴 레인` … (table §7)

### 9.1 Honesty footnote (verbatim, section 05 and panel strip)
> **이 로그에 없는 것.** 솔버의 답 텍스트는 AI:GO가 저장하지 않는다(로그 형식 고정, 운영진 확인). 추론 내용과 프롬프트 본문도 없다. 따라서 이 뷰어는 스쿼드가 맞았는지 말하지 않는다 — 정답 여부는 외부 채점 러너(`baseline.correct`)로만 표시하고, 화면의 모든 수치는 토큰 누적치·상태 전이·타임스탬프에서만 파생된다. `token-usage-update`의 세션 누적치(78,092 / 4,208)는 이 실행의 합계가 아니므로 어떤 차트에도 쓰지 않는다.
> *Not in the log: the solver's answer text (AI:GO does not record it), reasoning, prompt bodies. Correctness shown only from the external grader.*

---

## 10. Build plan — 3 hours, starting from `viewer-v2.html`

Work in `viz/viewer-v3.html`; serve `viz/` with `python3 -m http.server 8765` for checks, but the deliverable must also open via `file://`.

| step | min | do | check |
|---|---|---|---|
| 0 | 10 | `cp viewer-v2.html viewer-v3.html`. Keep: `<script>` lines for `normalizeRaw`, `ingest`, `#file` change handler, drop listeners, the calibration block of `renderReceipt`. Delete Bowl/Lens/Receipt markup + `renderState/stateAt/renderFeed/renderDecisions/bar`. Replace CSS vars with §8. Inline the 3 run JSONs as `<script type=application/json>`; `RUNS`, `ORDER=['run-001','run-002','run-003']`. | file opens by double-click, console clean |
| 1 | 20 | Port `derive()` from ledger with §2.3 changes (parallel arrays `D.flag/task/k`, dur fallback, null baseline, title lookup via `T.tasks`, `serialClaim`, `gaps`, `checkpoints`, dup by key). Cache `RUNS[k].D`. | assert in console: totals 26,808/1,564/1,645; spans 3/1/1; dup 2/0/0; serialClaim non-null only for run-001 |
| 2 | 20 | Sticky header: runs seg, cmp toggle (off), controls, section chips, counter, scrubber svg (§3.1) with pointer seek + hidden range, caption row, skip chip. `setT/play/stop/loop` with auto speed, idle timer, `visibilitychange` pause. | drag scrubber → counter updates; auto play run-001 ≈ 16 s |
| 3 | 15 | 00 Hero (§3.2): two slots, sentence, exact caption, herobar; `setRatio` morph on `show(k)`; frozen at totals. | load → `43.4× → 2.7×`; key `1` → After slot `—`; key `3` → morph back |
| 4 | 25 | 01 timeline single-run (§3.3): phase bands, staggered markers with end-anchoring, task bands + hatch, sawtooth bars (bw ≥ 6, prompt/comp stack, dup overlay, ≥3rd cap), cum staircase + 617 line, gap glyphs, legend; `data-t/data-i` on everything; F-zoom with `xWin`. | run-001 shows 3 sawteeth; F on SOLVE #1 enlarges 11 bars |
| 5 | 15 | 02 lanes (§3.4) with idle rows, badges, header counts `정의 8 · 계획 1 · 호출 1 · 유휴 6`. | 8 rows, 6 dimmed |
| 6 | 30 | 03 ledger (§3.5): grouped rows with `<details>`, subtotals, totals block, badges; `select(i)` + inline panel (§4.1) with 6 fields, claim cards with `← 로그 #k` links, checksum, 원본 tab. Clicking any `[data-i]` anywhere routes to `select`. | click row #8 → `Δ = 686 − 503 = +183`, checksum ✓; `←/→` walk rows; 원본 shows no derived keys |
| 7 | 20 | 04 flags cards + comparison table (f1 seconds, delta modes, 답 텍스트 row) + data sentence; 05 footnote, calibration (v2 renderer tweaked), methods line. | table 시간 row reads 5.09/60.2/7.9/16.0; sentence prints 91.2%/91.2%/28→2 |
| 8 | 25 | RACE (§6): cmp ON → lanes renderer, shared scales, lane status chips, baseline lane, SPLIT chips with light-up rule and token chip cycling; scrubber ghosts; hero 4 bars. | C+Space: v3.5 chip `🏁 완주 16.0s` at 16 s; `완주 −44.2s` lights at 60.2 s; v3.2-vs-v3.5 계획 chip red |
| 9 | 10 | Rubric rail (§3.8) with `data-rubric` attributes on: scrubber, #tl, #ln, #caption, #rows, panels, #flags, #cmpt, #hero, calibration. Key legend, `?` toggle. | hover each chip → only its elements stay lit |
| 10 | 10 | Ingestion hardening (§2.4): try/catch, content-detect squad, title patch, agentId fallback, borrowed-baseline warning, dragover overlay, footer `<input type=file multiple>`. | drop a rebuilt events.jsonl (+squad) → toast `이벤트 49 → 호출 28 · 태스크 3`, dup 2 flagged, titles `SOLVE` |
| 11 | 10 | QA at 1280×800 (light/dark irrelevant — committed dark): no horizontal scroll, every SVG text ≥ 12 px, no label collisions at 41.0/59.4 s, hero never shows a mid-scrub number, idle reset after 45 s, `file://` open, console clean on all three runs + compare. Screenshot the 4 stage frames (hero / 01 / race end / 05). | done |

Total ≈ 180 min. If behind schedule, cut in this order: RNGD line → F-zoom → ledger print stagger → 02 lanes (keep header counts) — never cut hero, sawtooth, ledger rows, race chips, footnote.

### 10.1 Acceptance asserts (run in console after load; all must hold)
```js
['run-001','run-002','run-003'].map(k=>{const D=RUNS[k].D;return [k,D.total,D.calls.length,D.spans.length,D.spans.filter(s=>s.dup).length,+D.dur.toFixed(1)]})
// → [["run-001",26808,28,3,2,60.2],["run-002",1564,2,1,0,7.9],["run-003",1645,2,1,0,16]]
RUNS['run-001'].D.spans.map(s=>s.prompt+s.completion) // → [10629,4330,11849]
RUNS['run-001'].D.spans.map(s=>[s.first,s.last])      // → [[487,1277],[487,758],[522,1196]]
RUNS['run-001'].D.serialClaim !== null && RUNS['run-003'].D.serialClaim === null
document.querySelector('#ratio-after').textContent     // → "2.7" on load (cur=run-003)
splits()  // → {plan:-7.73, first:-7.21, finish:-44.23, tokens:-25163, pct:-93.9}
```
