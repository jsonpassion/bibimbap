# 뷰어 테스트 절차

## T0. 준비 (1분)
- [ ] `cd viewer && python3 -m http.server 8642` → 브라우저에서 `http://localhost:8642/viewer.html`
- [ ] 헤더에 `BIBIMBAP · 60.2s · 26,808 tok · 49 events` 형태의 메타가 뜨면 기본 trace 로드 성공

## T1. The Bowl — 리플레이 (3분)
- [ ] 그릇 둘레에 에이전트 8개, 중앙 "문항" 노드, 하단 태스크 칩 표시
- [ ] ▶ 재생 → 플래너(★)가 노랑(계획) → Math-Solver가 파랑(실행 중) → 초록(완료) 순으로 변함
- [ ] 에이전트 아래 토큰·호출 카운터가 재생 중 증가
- [ ] 스크러버를 끝까지 드래그 → 모든 태스크 칩 초록, 하단 `49/49`
- [ ] 배속 30× 선택 후 재생 → 60초 실행이 수 초 안에 끝남
- [ ] 타임라인의 아무 줄 클릭 → 그릇이 그 시점 상태로 되감김(현재 줄 보라색 하이라이트)

## T2. Decision Lens (2분)
- [ ] 타임라인에서 "모델 호출" 줄 클릭 → ② 탭 상단에 에이전트·요약·t값, 아래에 원본 JSON(tokens 포함)
- [ ] "이 실행의 결정들" 표 5행: 계획(중복 경고 포함)·승인 전 반려 횟수·호출 패턴·취합·비용 판단
- [ ] 중복 태스크 수가 `.squad.json`/tasks와 일치하는지 (run-001은 3태스크 중 2중복)

## T3. The Receipt (2분)
- [ ] KPI 6개: 총 토큰(보라 히어로) / 입력·출력 / 호출 / 시간 / 태스크(중복) / 단독 대비 배수
- [ ] "단독 vs 스쿼드" 막대 2개 + 아래 설명 문장(입력 토큰 비중 %)
- [ ] 에이전트별 토큰 막대(run-001은 Math-Solver 1개)
- [ ] 캘리브레이션 곡선: x축 0~10, 점 7개, 우상향(10→100%)

## T4. 원본 로그 직접 적재 (3분) — 채점 정합성 핵심
- [ ] 새 실행 후 `.squad.json` 드롭 → 헤더 "스쿼드 설정 적재됨" → `events.jsonl` 드롭 → 메타에 "원본 로그에서 브라우저 내 정규화" 표시
- [ ] 같은 로그를 `normalize.py`로 만든 trace.json과 비교: 총 토큰·이벤트 수·태스크 수가 동일
- [ ] `.squad.json` 없이 events.jsonl만 드롭해도 동작(에이전트명은 `agent-xxxxxx`로 대체)

## T5. 견고성 (2분)
- [ ] 네트워크 끊고(기내 모드) 새로고침 → 기본 trace가 로드되고 모든 화면 동작 (오프라인 데모 안전)
- [ ] 브라우저 창 폭 800px로 축소 → 그리드가 세로로 쌓이고 SVG가 폭에 맞게 축소
- [ ] 완주되지 않은 로그(execution-started 없음) 드롭 → 에러 메시지, 기존 화면 유지

## 합격 기준
T1~T4 전 항목 통과 + T5 첫 항목(오프라인) 통과. 데모 엑스포는 T5 조건에서 진행.

## T6. 뷰어 v2 (8/22 저녁) — 최신 스쿼드(5 agents) 기준 Before/After

- 기본 적재 = `traces/run-002.json` (v3.2 · 5 agents · 1,564 tok). 헤더 우측 **런 선택**으로 `run-001.json` (v1 · 8 agents · 26,808 tok)로 전환 → Before/After 리플레이.
- The Bowl: 에이전트 5개 방사형 + 각 노드 아래 모델명(gpt-oss-120b) + 중앙 **홉 카운터**.
- Decision Lens: **라우팅 근거**([PLANNING DIRECTIVE] → 담당 일치 ✅/⚠️), **원칙 0**(가동 에이전트 n/5), 비용 판단(최소 경로 도달 여부 + v1 대비 ÷N).
- The Receipt: KPI 8개(가동 에이전트/로스터, v1 대비 ÷17 추가) + **3단 막대**(단독 617 / v1 26,808 / v3.2 1,564) + 원칙 0 해설.
- 확인법: `python3 -m http.server 8765 --directory viewer` → http://localhost:8765/viewer.html → ③ The Receipt에서 막대 3개·라벨 잘림 없음, ② Decision Lens 첫 행이 "라우팅 근거".
- v3.4 스쿼드로 새 완주 로그가 생기면: `python3 viewer/normalize.py <workspace> -o viewer/traces/run-003.json --baseline <results.jsonl> --item math-visible-0001` 후 `meta.version`에 "v3.4 (5 agents · 원칙 0)" 기입, `#runsel`에 옵션 추가.
