# BIBIMBAP — Squad Trace Viewer

JunctionX Korea 2026 · Lablup × FuriosaAI 트랙 · 팀 541

AI:GO Squad의 실행 로그(`logs/events.jsonl`)를 읽어 문제 해결 과정을 인터랙티브하게 리플레이하는 정적 뷰어입니다. 빌드 없음, 의존성 없음 — `viewer/viewer.html` 하나.

## 입력 (채점 기준: "로그(텍스트) 데이터로 표현된 Trace")

| 파일 | 역할 |
| --- | --- |
| `logs/events.jsonl` | **원본 Trace (source of truth)** — AI:GO가 기록한 이벤트 로그. 뷰어가 직접 읽음 |
| `.squad.json` | 에이전트 이름·역할·플래너 식별 (선택, 함께 드롭) |
| `traces/*.json` | `normalize.py`가 만든 정규화 캐시 — 베이스라인·캘리브레이션 등 부가 데이터 동봉용 |

뷰어의 모든 픽셀은 events.jsonl의 한 줄로 거슬러 올라갑니다(Traceability). 브라우저 안에서 정규화하므로 숨은 전처리가 없습니다.

## 실행

```bash
cd viewer && python3 -m http.server 8642
```
→ http://localhost:8642/viewer.html (기본으로 `traces/run-001.json` 로드)

## 새 실행 로그 보기

1. AI:GO에서 스쿼드 실행 완주
2. 워크스페이스의 `.squad.json`과 `logs/events.jsonl`을 뷰어 창에 **드래그 앤 드롭** (둘 다, 순서 무관)
3. 또는 CLI: `python3 viewer/normalize.py <workspace> -o viewer/traces/run-002.json [--baseline results.jsonl --item <id>] [--calibration confgate.jsonl]`

## 화면 = 루브릭 6축

| 화면 | 내용 | 축 |
| --- | --- | --- |
| ① The Bowl | 방사형 에이전트 그릇 + 상태·토큰 실시간 갱신 + 타임라인 스크러버·재생 | Observability · Clarity · Traceability |
| ② Decision Lens | 스텝 상세(원본 이벤트 JSON) + 이 실행의 결정 요약(계획·반려·호출 패턴·비용 판단) | Interpretability · Explainability |
| ③ The Receipt | 총 토큰·호출·시간·중복, 단독 모델 vs 스쿼드 비교, 에이전트별 토큰, 확신도 캘리브레이션 곡선 | Insightfulness |

## 테스트 절차

`docs/TESTING.md` 참조.

## v2 (8/22 저녁)
- 기본 런 = run-002(최신 5-agent 스쿼드), 헤더에서 run-001(v1)로 전환 가능 — Before/After.
- Decision Lens에 라우팅 근거·원칙 0(불필요한 에이전트 사용 금지) 행, Receipt에 3단 Before/After 막대.
