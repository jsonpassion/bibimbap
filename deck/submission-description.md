**[54-1] BIBIMBAP — if you can observe it, you can reduce it.**

Team CouchPotato (Jason Lee, Hoyeon Park). Track: Build the Best Agent Squad — beat one large model with multiple small models. Everything below ran on FuriosaAI RNGD through Lablup AI:GO.

## What we built
1. **An AI:GO agent squad** that answers benchmark problems (MMLU-Pro/GPQA, AIME/HMMT, LiveCodeBench/SWE-bench) with the smallest structure that survives the grader: two agents, both `gpt-oss-120b`. **Conductor**, the planner, does not decompose — it solves the problem in its own planning message (0 tasks, 0 tools, two solution routes reconciled before answering). **Solver** is its twin: when the planner creates no task the runtime fans the request out, and Solver answers once more as insurance. 2.2 model calls per problem.
2. **A Trace Viewer** (single HTML file, offline) that replays the squad's own `events.jsonl` and `.squad.json`: a simple-mode scoreboard and a ledger mode that maps the six rubric words — observability, interpretability, traceability, explainability, clarity, insightfulness — to six screen elements, 1:1.
3. **"BIBIMBAP Friends"**, a storybook version of the same traces for non-engineers: the agents as characters, retired designs shown in grey, and a live replay of real runs that loops on stage.

## How the trace decided the design
- **First squad**: 8 agents, 26,808 tokens for one math item (43× a single model) — the planner wrote three identical tasks, loops idled up to 11 rounds, and 91% of the cost was re-sent input. Reverse-engineering the loop protocol and finding the planner's hidden thinking in router stats (1,229 → 54 tokens with `/no_think`) brought the same item to 1,611 tokens (÷17).
- **Five squad designs, all measured**: specialist routing (5 agents, 2.5× tokens) · confidence-gated second opinion (fixed 4 items, broke 20) · subject specialists (no gain) · 3 solvers + judge ensemble (correct locally, **0.045** on the board) · planner answers directly (**0.373**).
- **The key lesson**: the grader reads only the planner's final message of the planning phase. The ensemble's judge was right, but its answer never reached the grader — so the planner became the solver.
- **Three models, three roles** (public practice sets, same items): gpt-oss-120b is the solver (generic 81.9%, math 82.6%, LCB 88.9%); Qwen3-32B is a superb router when its thinking can be controlled (one task in 61 tokens) but the runner ignores `/no_think`; K-EXAONE-236B is strong but 130–170 s per call with 35–50% timeouts on the shared endpoint. Keep what works where it works — that is the bibimbap.

## Results
- Leaderboard: **0.373** (math 53.8%, tied #1; generic 58.6%; coding 18.4%; 2.2 calls/item) across nine submissions: 0.186 → 0.254 → 0.045 → 0.285 → 0.373 → 0.363 → final (Conductor v6.6) pending at submission time.
- Two late findings shaped the final set: (1) coding 21.1% = 8/38 for every top team — all SWE-bench items score zero, and in our outputs the cause was **patch format** (bare `@@` hunk headers rejected by `git apply`/`patch`), not the fix; a patch contract in the prompt took numeric headers from 0/5 to 8/8 with no LiveCodeBench regression (20/20). (2) "Ungraded" math items are reasoning cut by the runner's per-call token cap; prompt wording cannot shorten gpt-oss reasoning (measured twice), so we kept the one-shot that graded 11/13.

## Technology
Lablup AI:GO (Backend.AI GO) squads on FuriosaAI RNGD · `furiosa-ai/gpt-oss-120b` (final), Qwen3-32B-FP8 and K-EXAONE-236B (measured) · our own harness `jxc-selfeval` that replays runner conditions (planner template + one-shot) on the full public practice sets with bootstrap CIs · viewer and storybook in vanilla HTML/SVG/JS, jsdom tests, no build step.

## Links
- Repo: https://github.com/jsonpassion/junction2026-54-1-CouchPotato (squad files, one-shot prompts, viewer, storybook, keynote)
- Demo: https://jsonpassion.github.io/junction2026-54-1-CouchPotato/viewer/kids.html · Trace Viewer: https://jsonpassion.github.io/junction2026-54-1-CouchPotato/viewer/viewer.html
- Working history: https://github.com/jsonpassion/bibimbap
