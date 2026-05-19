# Playwright MCP E2E 시나리오

> 실행 환경: Claude Code 세션에서 `mcp__playwright__*` 도구를 호출.
> 결과 산출: `assets/qa/playwright/{real,dummy,golden_path}/*.png` + `docs/reports/05_playwright_qa.html`

## 사전 조건

1. Streamlit 앱이 `localhost:8501` 에서 가동 중
2. 트랙 ① 은 두 번 실행: `DEMO_MODE=real`, 다음 `DEMO_MODE=dummy`
3. 트랙 ② 는 `DEMO_MODE=real` 에서만 실행

## 페이지 5종 (Streamlit multipage 파일명 → URL)

| 코드 | 파일 | URL 경로 (한글·이모지 포함) |
|---|---|---|
| P1 | `app/app.py` | `/` (통합 대시보드 — 홈) |
| P2 | `app/pages/1_📊_실시간_예측.py` | `/실시간_예측` |
| P3 | `app/pages/2_🔍_원인_분석.py` | `/원인_분석` |
| P4 | `app/pages/3_🛠_조치_가이드.py` | `/조치_가이드` |
| P5 | `app/pages/4_📜_이력_조회.py` | `/이력_조회` |

> URL 안정성을 위해 사이드바의 페이지 링크를 `browser_snapshot` 으로 확보한 뒤
> `browser_click` 으로 이동하는 방식이 가장 안전. 본 시나리오는 직접 `browser_navigate` 우선.

## 트랙 ① — 5페이지 스모크

각 페이지마다:

1. `mcp__playwright__browser_navigate` URL=`http://localhost:8501/{경로}`
2. `mcp__playwright__browser_wait_for` text=페이지 헤더 텍스트 (예: "실시간 예측")
3. `mcp__playwright__browser_console_messages` → `level == 'error'` 메시지 0건 어설션
4. `mcp__playwright__browser_snapshot` → 사이드바 배지 텍스트(`🟢 real` / `🟡 dummy`) 확인
5. `mcp__playwright__browser_take_screenshot` filename=`assets/qa/playwright/{source}/P{n}.png`, fullPage=true

## 트랙 ② — 식각 온도 골든 패스 (DEMO_MODE=real)

| Step | 액션 | 어설션 | 스크린샷 |
|---|---|---|---|
| 1 | P2 진입 → "▶️ 시뮬레이션 시작" 버튼 클릭 → 12초 대기 | FAIL 게이지 빨강 또는 위험 배지 텍스트 존재 | `golden_path/step1.png` |
| 2 | P3 진입 | Top 기여 센서 라벨 텍스트 존재 (`sensor_` 또는 `식각`) | `golden_path/step2.png` |
| 3 | P4 진입 → 첫 번째 "✅ 수용" 버튼 클릭 | 토스트 또는 카운터 1 이상 | `golden_path/step3.png` |
| 4 | P5 진입 → "조치 이력" 탭 클릭 | 방금 수용 항목 한 줄 이상 | `golden_path/step4.png` |
| 5 | P1 복귀 | KPI 상태 녹색 또는 "정상" 텍스트 존재 | `golden_path/step5.png` |

## 통과 기준

- 트랙 ① — **앱 코드 콘솔 에러 0건** (아래 화이트리스트 제외), 스크린샷 10장 모두 생성 (real 5장 + dummy 5장)
- 트랙 ② — 5단계 모두 어설션 통과, 스크린샷 5장 모두 생성
- 모든 스크린샷에서 한글이 깨지지 않음 (육안 검증)

### 콘솔 에러 화이트리스트 (Streamlit framework 알려진 이슈)

한글 multipage URL 에서 Streamlit framework 가 `_stcore/health`, `_stcore/host-config`
endpoint 를 **상대경로** 로 fetch 해 404 가 반환되는 알려진 이슈. 앱 코드 / 사용자 기능과 무관하며
화면 동작에는 영향이 없다. 어설션은 다음 패턴을 제외하고 평가한다:

- `_stcore/health:0` 404
- `_stcore/host-config:0` 404

본 PR-5 실행 (real 트랙 ① · dummy 트랙 ① · 골든 패스) 에서 위 두 패턴 외 콘솔 에러는 0 건이었음.

## 실행 흐름 요약

```text
[real 모드 가동]
  ├─ 트랙 ① real: P1 → P2 → P3 → P4 → P5  (5장)
  └─ 트랙 ② 골든 패스: step1 → step2 → step3 → step4 → step5  (5장)

[dummy 모드 재기동]
  └─ 트랙 ① dummy: P1 → P2 → P3 → P4 → P5  (5장)

[헬퍼 실행]
  └─ python tests/e2e/run_playwright_qa.py
      → docs/reports/05_playwright_qa.html (갤러리 15장 + 어설션 표)
      → docs/reports/index.html (5번 카드 ✅ 갱신)
```
