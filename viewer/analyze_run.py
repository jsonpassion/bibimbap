#!/usr/bin/env python3
"""최신 스쿼드 실행 1건을 events.jsonl에서 즉시 요약: 태스크 수·호출 수·토큰·소요시간.
사용: python3 analyze_run.py [workspace_dir]"""
import json, sys, os, collections
from datetime import datetime
ws = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Documents/Developer/bibimbap-squad/workspace")
ts = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
raw = [json.loads(l) for l in open(os.path.join(ws, "logs", "events.jsonl"))]
starts = [i for i, e in enumerate(raw) if e["eventType"] == "squad:execution-started"]
if not starts: sys.exit("완주된 실행 없음")
ex = raw[starts[-1]:]; plan_i = max(i for i, e in enumerate(raw[:starts[-1]]) if e["eventType"] == "squad:planning-started")
plan = next((e for e in raw[plan_i:starts[-1]] if e["eventType"] == "squad:plan-ready"), {}).get("payload", {})
calls, prev, per_task = [], (0, 0), collections.Counter(); cur = None
for e in ex:
    p = e.get("payload") or {}; t = e["eventType"]
    if t == "squad:agent-state-changed" and p.get("state") == "running": cur = p.get("agentId")
    if t == "squad:execution-token-usage":
        cp, cc = p.get("promptTokens", 0), p.get("completionTokens", 0)
        calls.append((cp - prev[0] if cp >= prev[0] else cp, cc - prev[1] if cc >= prev[1] else cc)); prev = (cp, cc)
fin = next((e for e in ex if e["eventType"] == "squad:execution-completed"), None)
tu = (fin or {}).get("payload", {}).get("tokenUsage", {})
done = [e for e in ex if e["eventType"] == "squad:task-completed"]
dur = ts(ex[-1]["timestamp"]) - ts(raw[plan_i]["timestamp"])
print(f"계획 태스크 수      : {plan.get('taskCount')}  (중복 여부 확인)")
print(f"완료 태스크 수      : {len(done)}  성공 {sum(1 for e in done if e['payload'].get('success'))}")
print(f"모델 호출 수(실행)  : {len(calls)}  → 태스크당 {len(calls)/max(len(done),1):.1f}회")
print(f"토큰 (실행 단계)    : 입력 {tu.get('promptTokens', sum(c[0] for c in calls)):,} / 출력 {tu.get('completionTokens', sum(c[1] for c in calls)):,}")
print(f"소요 시간(계획 포함): {dur:.1f}s")
print("호출별 출력 토큰    :", [c[1] for c in calls])
print("최종 result         :", str((fin or {}).get('payload', {}).get('result', ''))[:160].replace("\n", " "))
