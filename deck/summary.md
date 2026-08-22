[541] BIBIMBAP — 관측할 수 있으면 줄일 수 있다

손에 쥘 수 있는 모델(FuriosaAI RNGD 위 gpt-oss-120b)로 AI:GO 에이전트 스쿼드를 만들고, 그 스쿼드의 모든 판단을 Trace로 되감아 보게 했습니다.

첫 스쿼드는 같은 수학 문항에 단독 모델(617 tok·5.09 s)의 43배인 26,808 tok·60.2 s를 썼습니다. 로그를 해부하자 낭비는 세 층이었습니다 — 플래너의 동일 태스크 3중 생성, 태스크당 최대 11회의 루프 공회전(총 28회 호출), 비용의 91%를 차지한 입력 재전송. 루프 규약을 역공학하고, 로컬 로그에 없던 플래너 thinking 비용을 라우터 통계로 찾아 /no_think(1,229→54 tok)로 잘라내자 같은 문항이 1,611 tok·17 s(÷17)가 됐습니다.

솔버 프롬프트는 공개 연습 세트 전수로 검증했습니다: generic 140문항 79.1→80.9%(출력 토큰 −16%), math 164문항 79.8→82.6%(−21%), LCB 20문항 75.0→88.9%(−15%), AIME-2024는 Reasoning: high로 72.4→78.6%. Qwen3와 EXAONE은 측정 후 제외했고, 20문항 베이스라인 60%가 표본 불운이었음도 전수로 정정했습니다.

가장 큰 교훈은 리더보드였습니다. 로컬에선 정답을 내던 3 솔버+Judge 앙상블(v7.1)이 0.045 — Judge의 답이 채점기에 닿지 않았습니다. 공개 보드의 요청 수가 Trace였습니다: 상위 3팀 모두 gpt-oss ≈ 1회/문항(DemoDayCare는 정확히 147회 = 1/문항), 즉 채점기는 계획 단계 플래너의 최종 메시지를 읽습니다. 최종 v6.0 DIRECT는 2 에이전트(전원 gpt-oss, Reasoning: high): Conductor가 0 태스크·0 도구로 직접 답을 쓰고, 같은 페르소나의 Solver가 fan-out 보험을 섭니다(러너 충실 조건 generic 76.0%, 재측정 중).

산출물: .squad.json + one-shot, Trace Viewer(간단/원장 모드, 루브릭 6축 1:1, 원본 events.jsonl 재생, 로그에 없는 답 텍스트는 '미기록'으로 표시), 그림책 kids.html. 리포 github.com/jsonpassion/bibimbap · 데모 jsonpassion.github.io/bibimbap/
