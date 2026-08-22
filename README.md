# 🥣 BIBIMBAP — Squad Trace Viewer

JunctionX Korea 2026 · Lablup × FuriosaAI "Build the Ultimate Agent Squad" — 팀 CouchPotato(541).

**"관측할 수 있으면 줄일 수 있다."** 첫 스쿼드는 단독 모델보다 43배의 토큰을 썼다(26,808 vs 617). 그 과정을 로그로 해부해 17배를 걷어냈고, 플래너 모델·프롬프트·출력 규칙을 측정으로 바꿨다. 이 저장소는 그 Trace를 보는 도구다.

## 데모 (GitHub Pages)
- `viewer/viewer.html` — **Trace Viewer**: 간단 모드(스코어보드 · 5단계 투어 · 자동 데모) ↔ 원장 모드(6축 루브릭: observability · interpretability · traceability · explainability · clarity · insightfulness). 단독 베이스라인 vs 스쿼드(같은 문항), 트랙별 정확도·토큰(전수 측정), 원장(← 로그 줄 링크), 판단 카드, 정직 각주.
- `viewer/kids.html` — **BIBIMBAP 친구들**: 실제 에이전트 스크립트에서 뽑은 다섯 캐릭터가 진짜 기록으로 문제를 푸는 그림책 + 실전 재생.

둘 다 단일 HTML, 외부 의존성 0, 파일 더블클릭으로 열림(trace 내장). 원본 AI:GO 로그(`logs/events.jsonl` + `.squad.json`)를 드래그앤드롭하면 브라우저 안에서 정규화해 재생한다.

## 구성
```
viewer/viewer.html      Trace Viewer v3 (간단/원장)
viewer/kids.html        의인화 그림책
viewer/traces/*.json    공개 연습 세트 문항의 로컬 완주 로그(정규화) — 히든 문항 없음
viewer/normalize.py     AI:GO 워크스페이스 → trace.json (누적 토큰 → 호출별 Δ, 실행 구간 선택 --execution)
viewer/analyze_run.py   마지막 실행 요약(태스크·호출·토큰·시간)
viewer/test.js          derive()/normalizeRaw() 수용값 테스트 (node test.js)
docs/viewer-v3-spec.md  설계 스펙 · docs/TESTING.md 테스트 절차
```

## 데이터 출처와 정직성
- 정확도·토큰 수치는 jxc-selfeval(공식 채점 방식 재현: math-verify · letter_match · LiveCodeBench 실행)로 **공개 연습 세트 전수**를 측정한 값.
- 솔버의 답 텍스트는 AI:GO 로그에 기록되지 않는다(형식 고정) — 뷰어는 이를 숨기지 않고 "로그에 없는 것"으로 표시한다.
- 모델: furiosa-ai/gpt-oss-120b(솔버), Qwen3-32B-FP8(플래너, /no_think). EXAONE은 측정 후 제외.

## 라이선스·출처
연습 세트: SWE-bench, LiveCodeBench, MATH-500, AIME 2024, MMLU-Pro(각 출처의 고지 유지). 코드: MIT.
