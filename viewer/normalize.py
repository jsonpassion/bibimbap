#!/usr/bin/env python3
"""AI:GO Squad 워크스페이스 로그 → 뷰어용 trace.json 정규화.

사용:
  python3 normalize.py <workspace_dir> -o traces/run-001.json \
      [--baseline <selfeval results.jsonl> --item <item_id>] \
      [--calibration <confgate results.jsonl>]

입력: <workspace>/.squad.json, logs/events.jsonl, tasks/index.json
출력: 뷰어(viewer.html)가 읽는 단일 JSON (meta/agents/tasks/events/tokens/insights)
"""
import argparse, json, os, collections
from datetime import datetime

def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--baseline", help="selfeval results.jsonl (단독 모델 비교용)")
    ap.add_argument("--item", help="baseline에서 비교할 item_id")
    ap.add_argument("--calibration", help="confgate results.jsonl (확신도 캘리브레이션)")
    ap.add_argument("--execution", help="특정 executionId(접두사)로 실행 구간 선택 (기본: 마지막 실행)")
    a = ap.parse_args()
    ws = a.workspace

    squad = json.load(open(os.path.join(ws, ".squad.json")))["config"]
    agents = {ag["id"]: {"id": ag["id"], "name": ag["name"],
                         "role": (ag.get("role") or {}).get("value") or (ag.get("role") or {}).get("type"),
                         "model": ((ag.get("modelPreferences") or {}).get("preferredModelId") or "").split("/")[-1],
                         "planner": ag["id"] == squad.get("plannerAgentId")}
              for ag in squad["agents"]}

    raw = [json.loads(l) for l in open(os.path.join(ws, "logs", "events.jsonl"))]
    # 마지막 승인된 실행 구간만: execution-started 직전의 마지막 planning-started 부터 끝까지
    exec_starts = [i for i, e in enumerate(raw) if e["eventType"] == "squad:execution-started"]
    exec_idx = max(exec_starts)
    if a.execution:
        cands = [i for i in exec_starts if str((raw[i].get("payload") or {}).get("executionId", "")).startswith(a.execution)]
        if not cands:
            raise SystemExit(f"executionId {a.execution}* 를 가진 execution-started 이벤트 없음")
        exec_idx = cands[0]
        # 다음 실행 시작 전까지로 자르기
        later = [i for i in exec_starts if i > exec_idx]
        raw = raw[:later[0]] if later else raw
    plan_idx = max(i for i, e in enumerate(raw[:exec_idx]) if e["eventType"] == "squad:planning-started")
    evs = raw[plan_idx:]
    t0 = ts(evs[0]["timestamp"])
    rejected_plans = sum(1 for e in raw[:plan_idx] if e["eventType"] == "squad:plan-ready")

    tasks_idx = {t["id"]: t for t in json.load(open(os.path.join(ws, "tasks", "index.json")))}
    # 이 실행에 속한 태스크만 (wave/task-completed 이벤트에 등장한 id)
    run_ids = set()
    for e in evs:
        p = e.get("payload") or {}
        run_ids.update(p.get("taskIds") or []); 
        if p.get("taskId"): run_ids.add(p["taskId"])
    tasks = []
    for tid, t in tasks_idx.items():
        if run_ids and tid not in run_ids: continue
        ag = agents.get(t.get("assignedTo"), {})
        tasks.append({"id": tid, "title": t["title"], "agentId": t.get("assignedTo"),
                      "agentName": ag.get("name", "?"), "status": t["status"],
                      "createdAt": t.get("createdAt"), "completedAt": t.get("completedAt"),
                      "durationSec": round(ts(t["completedAt"]) - ts(t["createdAt"]), 1)
                      if t.get("completedAt") and t.get("createdAt") else None})

    events, calls, cur_agent = [], [], None
    prev_cum = (0, 0)
    phase = "planning"
    for e in evs:
        p = e.get("payload") or {}
        et = e["eventType"].split(":")[1]
        t = round(ts(e["timestamp"]) - t0, 2)
        ev = {"t": t, "ts": e["timestamp"], "type": et, "phase": phase}
        if et == "planning-started":
            ev["summary"] = "플래너가 요청을 분석해 계획을 수립합니다"
            ev["agentId"] = squad.get("plannerAgentId")
            ev["detail"] = {"request": p.get("request", "")[:600]}
        elif et == "plan-ready":
            ev["summary"] = f"계획 완성 — 태스크 {p.get('taskCount')}개, 웨이브 {len(p.get('waves', []))}개"
            ev["agentId"] = squad.get("plannerAgentId")
            ev["detail"] = {"taskCount": p.get("taskCount"), "waves": p.get("waves"), "autoApprove": p.get("autoApprove")}
        elif et == "execution-started":
            phase = "execution"; ev["phase"] = phase
            ev["summary"] = f"실행 시작 — 태스크 {p.get('totalTasks')}개 / 웨이브 {p.get('totalWaves')}개"
        elif et == "task-wave-started":
            ev["summary"] = f"웨이브 {p.get('waveIndex', 0) + 1} 시작 (태스크 {len(p.get('taskIds', []))}개 병렬)"
            ev["detail"] = {"taskIds": p.get("taskIds")}
        elif et == "task-status-changed":
            tk = tasks_idx.get(p.get("taskId"), {})
            ev["taskId"] = p.get("taskId"); ev["agentId"] = tk.get("assignedTo")
            ev["summary"] = f"태스크 '{tk.get('title', '?')}' {p.get('oldStatus')} → {p.get('newStatus')}"
        elif et == "agent-state-changed":
            ev["agentId"] = p.get("agentId"); cur_agent = p.get("agentId") if p.get("state") == "running" else cur_agent
            ev["summary"] = f"{agents.get(p.get('agentId'), {}).get('name', '?')} 상태 → {p.get('state')}"
            ev["detail"] = {"state": p.get("state")}
        elif et == "execution-token-usage":
            # 누적값으로 보고됨 → 직전 대비 델타가 이번 호출분
            cp, cc = p.get("promptTokens", 0), p.get("completionTokens", 0)
            dp = cp - prev_cum[0] if cp >= prev_cum[0] else cp
            dc = cc - prev_cum[1] if cc >= prev_cum[1] else cc
            prev_cum = (cp, cc)
            ev["agentId"] = cur_agent if phase == "execution" else squad.get("plannerAgentId")
            ev["tokens"] = {"prompt": dp, "completion": dc, "cumPrompt": cp, "cumCompletion": cc}
            ev["summary"] = f"모델 호출 — 입력 {dp:,} / 출력 {dc:,} 토큰 (누적 {cp + cc:,})"
            calls.append({"t": t, "agentId": ev["agentId"], "phase": phase, "prompt": dp, "completion": dc})
        elif et == "token-usage-update":
            ev["agentId"] = p.get("agentId")
            ev["summary"] = f"{agents.get(p.get('agentId'), {}).get('name', '?')} 누적 토큰 {p.get('total', 0):,}"
            ev["detail"] = {"cumPrompt": p.get("promptTokens"), "cumCompletion": p.get("completionTokens")}
        elif et == "task-completed":
            tk = tasks_idx.get(p.get("taskId"), {})
            ev["taskId"] = p.get("taskId"); ev["agentId"] = tk.get("assignedTo")
            ev["summary"] = f"태스크 '{p.get('taskTitle')}' 완료 ({'성공' if p.get('success') else '실패'})"
            ev["detail"] = {"success": p.get("success"), "error": p.get("error"), "taskCounts": p.get("taskCounts")}
        elif et == "aggregation-started":
            phase = "aggregation"; ev["phase"] = phase
            ev["agentId"] = squad.get("plannerAgentId")
            ev["summary"] = f"취합 시작 — 태스크 {len(p.get('taskIds', []))}개 결과 합성"
        elif et == "execution-completed":
            ev["summary"] = "실행 완료"
            ev["detail"] = {"result": p.get("result"), "tokenUsage": p.get("tokenUsage")}
        else:
            ev["summary"] = et
        if ev.get("agentId"):
            ev["agentName"] = agents.get(ev["agentId"], {}).get("name", "?")
        events.append(ev)

    by_agent = collections.defaultdict(lambda: {"prompt": 0, "completion": 0, "calls": 0})
    by_phase = collections.defaultdict(lambda: {"prompt": 0, "completion": 0, "calls": 0})
    for c in calls:
        for bucket in (by_agent[c["agentId"]], by_phase[c["phase"]]):
            bucket["prompt"] += c["prompt"]; bucket["completion"] += c["completion"]; bucket["calls"] += 1
    total_p = sum(c["prompt"] for c in calls); total_c = sum(c["completion"] for c in calls)
    fin = next((e for e in evs if e["eventType"] == "squad:execution-completed"), None)
    if fin and (fin.get("payload") or {}).get("tokenUsage"):
        tu = fin["payload"]["tokenUsage"]
        total_p, total_c = tu.get("promptTokens", total_p), tu.get("completionTokens", total_c)

    dup = collections.Counter((t["title"], t["agentId"]) for t in tasks)
    duplicates = sum(v - 1 for v in dup.values() if v > 1)

    meta_req = next((e["detail"]["request"] for e in events if e["type"] == "planning-started"), "")
    out = {
        "meta": {"squad": squad["name"], "request": meta_req,
                 "startedAt": evs[0]["timestamp"], "completedAt": evs[-1]["timestamp"],
                 "durationSec": round(ts(evs[-1]["timestamp"]) - t0, 1), "rejectedPlansBefore": rejected_plans},
        "agents": list(agents.values()),
        "tasks": tasks,
        "events": events,
        "tokens": {"prompt": total_p, "completion": total_c, "total": total_p + total_c,
                   "calls": len(calls),
                   "byAgent": {aid: {"name": agents.get(aid, {}).get("name", "?"), **v} for aid, v in by_agent.items()},
                   "byPhase": dict(by_phase)},
        "insights": {"taskCount": len(tasks), "duplicateTasks": duplicates,
                     "plannerShare": round(by_phase["planning"]["prompt"] + by_phase["planning"]["completion"], 0) / max(total_p + total_c, 1),
                     "callsPerTask": round(by_phase["execution"]["calls"] / max(len(tasks), 1), 1)},
    }
    if a.baseline and a.item:
        for l in open(a.baseline):
            r = json.loads(l)
            if r.get("item_id") == a.item:
                out["baseline"] = {"item": a.item, "model": r.get("model"), "correct": r.get("correct"),
                                   "prompt": r.get("input_tokens"), "completion": r.get("output_tokens"),
                                   "seconds": r.get("seconds")}
                break
    if a.calibration:
        bucket = collections.defaultdict(lambda: [0, 0])
        for l in open(a.calibration):
            r = json.loads(l)
            if "s1_conf" in r:
                b = bucket[r["s1_conf"]]; b[0] += bool(r["s1_correct"]); b[1] += 1
        out["calibration"] = [{"conf": k, "correct": v[0], "n": v[1]} for k, v in sorted(bucket.items())]
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"trace → {a.out}: events {len(events)}, tasks {len(tasks)}, calls {len(calls)}, tokens {total_p + total_c:,}, dup {duplicates}")

if __name__ == "__main__":
    main()
