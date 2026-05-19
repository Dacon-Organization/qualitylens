# 본선까지의 발전 To-Do — 기획서 갭 분석 기반

> 작성일: 2026-05-19 (D-3)
> 본선: 2026-05-22 (금) 09:00 KST
> 기반: `QualityLens_기획서.pdf` 8슬라이드 정독 + agent_skills 강의 통찰 + pdf-to-md 통합
> 우선순위: **S = 평가 직접 영향** / **A = 발표 완성도** / **B = 마무리 폴리시**

---

## 0. 현재 산출물 vs 기획서 약속 — 갭 요약

| # | 기획서 약속 (Slide) | 현재 산출물 | 갭 | 우선순위 |
|---|---|---|---|---|
| G1 | **정상/경고/위험 3단계 컬러 코딩** + "비전문가 즉시 인지" (Slide 4 기능 1) | 게이지 단색만, 명시 라벨 X | ⚠️ 큼 | **S** |
| G2 | **SHAP Waterfall Plot + Dependence Plot** (Slide 4 기능 2, Slide 6 Step 3) | 막대 차트만 (force plot 없음) | ⚠️ 큼 | **S** |
| G3 | **원클릭 수용 버튼 + 조치 이력 자동 기록** (Slide 4 기능 3, Slide 6 Step 4) | 권고 카드만, 버튼·이력 X | ⚠️ 큼 | **S** |
| G4 | **스트리밍 시뮬레이션** + "정상→이상 주입→경고→복귀" (Slide 7) | 정적 데모만 | ⚠️ 큼 | **S** |
| G5 | **식각 공정 온도 스토리** (Slide 6 대표 시나리오) | 일반 데모 골든 패스 | △ 중 | **A** |
| G6 | **P1 KPI = 70%+ 사전 감지율·30분 대응** (Slide 1, 8) | "<10ms 응답" 기술 지표만 | △ 중 | **A** |
| G7 | **P5 주간 리포트 + 반복 원인 Top 5** (Slide 6 보조 시나리오) | 단순 이력 테이블 | △ 중 | **A** |
| G8 | **Fail-Safe 정상 구동 시연 영상** (Slide 7) | 데모 모드만 | △ 중 | **A** |
| G9 | **페르소나 A 김 과장 / B 박 팀장** (Slide 6) | 미반영 | ◯ 소 | **B** |
| G10 | **KNN Imputation** (Slide 5) | median imputation | ◯ 소 | **B** |
| G11 | **자동 재학습 (Phase 1)** (Slide 8) | Q&A 답변 외 없음 | ◯ 소 | **B** |

---

## 1. Tier S — 평가 직접 영향 (반드시)

### S-1. 정상/경고/위험 3단계 컬러 코딩 (G1)

**근거**: 기획서 핵심 가치 "비전문가도 즉시 이상 인지" — 색 자체가 의사결정 UI.

**작업**:
- `app/lib/viz.py` 에 `risk_tier(proba)` 함수 추가: `< 0.3 → 정상(녹색)` / `0.3~0.5 → 경고(주황)` / `≥ 0.5 → 위험(빨강)`
- `app/app.py` P1 KPI 카드 색상 + 시계열 차트 영역 배경에 3구간 표시
- `app/pages/1_📊_실시간_예측.py` 결과 영역에 큰 컬러 배지 (정상/경고/위험)
- `app/pages/3_🛠_조치_가이드.py` 위반 카드 색상도 같은 기준 적용 (이미 있지만 일관성 정리)

**모델 라우팅**: Sonnet (UI 디테일)

### S-2. SHAP Waterfall + Dependence Plot (G2)

**근거**: "글로벌 피처 중요도 + 개별 Waterfall 동시 제공" 약속. 막대 차트는 Waterfall이 아님.

**작업**:
- `scripts/03_shap.py` 에 데모 4건의 **Waterfall plot용 데이터** 사전 계산:
  - base_value (expected_value) + 각 피처 SHAP value + 누적
- `models/shap_waterfall_demo.csv` 또는 `models/shap_waterfall_demo.pkl` 저장
- `app/lib/viz.py` 에 `shap_waterfall(sample_row, top_n=10)` 함수 — plotly 직접 구현 (shap.plots.waterfall은 matplotlib 의존)
- `app/pages/2_🔍_원인_분석.py` 의 샘플별 분석 부분을 Waterfall로 교체
- **Dependence Plot**: 상위 1~2개 피처에 대해 산점도 (피처값 x SHAP value) — `app/lib/viz.py::shap_dependence(sensor, X_test, shap_values)`

**모델 라우팅**: Opus (SHAP 시각화 + 데이터 구조)

### S-3. 원클릭 수용 + 조치 이력 (G3)

**근거**: 차별점의 핵심 — "예측 → 설명 → 조치 → 피드백" 순환 루프의 마지막 고리.

**작업**:
- `app/pages/3_🛠_조치_가이드.py` 위반 카드 옆에 `st.button("✅ 수용")` 추가
- 수용 클릭 시 `st.session_state.action_log` 에 누적 (시점, 샘플 ID, 센서, 권고 텍스트)
- `data/processed/action_log.csv` 로 디스크 영속 (Streamlit Cloud는 ephemeral이라 세션만으로도 데모 충분)
- P5 이력 조회에 **조치 이력 탭** 추가 (예측 이력 / 조치 이력 두 탭)

**모델 라우팅**: Sonnet (Streamlit 위젯)

### S-4. 스트리밍 시뮬레이션 (G4)

**근거**: "정상 스트리밍 → 이상 주입 → 경고 → 복귀" — 5분 데모의 뼈대.

**작업**:
- `app/lib/stream.py` 신규: test set 또는 demo_sample 을 시간 순서로 1초 간격 yield
- P2 페이지 상단에 `▶️ 시뮬레이션 시작 / ⏸ 일시정지 / 🔁 리셋` 컨트롤
- `st.empty()` 자리표시자 + `time.sleep(1)` 루프 (Streamlit rerun 패턴)
- 데모용 사전 스크립트: 첫 10초 정상 → 11초째 FAIL 주입 → 15초째 정상 복귀
- **중요**: streamlit cloud의 5분 idle timeout 고려, 데모 시작 버튼 누를 때만 동작

**모델 라우팅**: Opus (Streamlit rerun + state 관리)

---

## 2. Tier A — 발표 완성도

### A-1. 식각 공정 온도 스토리 (G5)

기획서 Slide 6 "식각 공정 온도 이상 → 불량 급증 대응" 5단계를 우리 데모 시나리오에 그대로 매핑:

| 기획서 Step | 우리 시연 액션 |
|---|---|
| Step 1 (08:30 P1) "금일 불량률 12.3%" 경고 | 시뮬레이션 시작 → P1 KPI 카드 빨갛게 + 알림 배너 |
| Step 2 (08:35 P2) 배치 #B-2252 78% | 시뮬레이션에서 FAIL 샘플이 P2 게이지로 등장 |
| Step 3 (08:37 P3) 식각 온도 1위 | P3 Waterfall에서 가장 큰 양의 기여 센서 강조 (sensor_XXX → "식각 온도"로 라벨 매핑) |
| Step 4 (08:40 P4) "165~175°C 하향" 팝업 + 수용 | P4 권고 카드 + 수용 버튼 클릭 |
| Step 5 (09:00 P1) 정상 복귀 | 시뮬레이션이 정상 샘플로 돌아오며 KPI 녹색 |

**작업**:
- `app/lib/persona.py` 신규: SECOM의 sensor_NNN → "식각 온도", "압력" 등 의미 있는 라벨 매핑 (상위 10개만)
- `docs/demo_script.md` 골든 패스를 위 표의 액션으로 재작성
- `docs/slides_outline.md` Slide 4 자리표시자에 위 5단계 스크린샷 명시

**모델 라우팅**: Sonnet (문서·라벨 매핑)

### A-2. 비즈니스 KPI 노출 (G6)

P1 통합 대시보드 상단에 기획서가 약속한 KPI 명시:

| KPI | 표시 위치 | 값 |
|---|---|---|
| 사전 감지율 | P1 큰 메트릭 | `recall@threshold` × 100 → "75.3% 사전 감지" |
| 평균 대응 시간 | P1 큰 메트릭 | 데모 모드: "약 30분 (기존 2~3일 대비 95%↓)" |
| 추정 손실 절감 | P1 큰 메트릭 | "연 20%+ (가정)" — 가정 라벨 명시 |
| 모델 응답 시간 | P1 보조 | "< 10ms" (기존 위치 유지) |

**작업**: `app/app.py` KPI 카드 4개 재정의 + 의미 있는 라벨

**모델 라우팅**: Sonnet

### A-3. P5 주간 리포트 (G7)

박 팀장 페르소나 시나리오:

- 기간 필터(주간/월간) → 불량률 추이 라인 차트
- **반복 원인 Top 5** — 기간 내 SHAP 상위 기여 센서 누적 카운트
- 다운로드 CSV는 이미 있음 ✓

**작업**: `app/pages/4_📜_이력_조회.py` 에 "주간 리포트" 탭 추가

**모델 라우팅**: Sonnet

### A-4. 시연 영상 사전 녹화 (G8)

기획서 "Fail-Safe: 정상 구동 시연 영상 사전 준비" 명시 — 본선장에서 Streamlit 자체가 안 켜지는 최악의 경우 대비.

**작업**:
- D-1에 로컬에서 5분 시연 1회를 OBS Studio 또는 Windows 게임바(`Win+G`)로 녹화
- `docs/demo_video.mp4` (gitignored — 큰 파일) + USB 별도 저장
- 발표 슬라이드 1장 추가: "시연 영상 재생" 슬라이드 (PPTX 삽입 영상)

**모델 라우팅**: 사용자 직접 (도구 작업)

---

## 3. Tier B — 마무리 폴리시

### B-1. 페르소나 카드 (G9)

P1 사이드바 하단 또는 About 페이지에 페르소나 A/B 카드 — 발표 시 "누가 쓰는가" 즉답 가능.

### B-2. KNN Imputation 옵션 (G10)

`scripts/01_preprocess.py` 에 `--imputation knn` 플래그 추가 (기본은 median 유지, 발표 시 "KNN도 지원" 한 마디 가능).

### B-3. 자동 재학습 더미 (G11)

P1 사이드바 하단 "🔄 모델 재학습" 버튼 (실제로는 데모 토스트만 표시, 향후 Phase 1 로드맵 시사).

---

## 4. agent_skills 통찰 반영

### 4-1. 스킬 description 보강 (Codex 자동 발동용)

각 `skills/*/INDEX.md` 첫 부분에 frontmatter 추가:

```markdown
---
name: codex-bridge
description: Claude ↔ Codex(GPT-5.x) 환경 전환 시 모델 라우팅과 토큰 절약 규칙. 본선장 운영 시 자동 발동.
---
```

이미 SKILL.md 컨벤션을 따르는 codex-bridge / streamlit-build / demo-script 3개에만 적용 (data-pipeline·modeling 등 stage 스킬은 작업 기준이 다르니 생략).

### 4-2. Codex 경로 노출

본선장에서 Codex가 우리 스킬을 자동 발동하려면 `~/.codex/skills/` 또는 `.agents/skills/` 경로 필요. 가장 가벼운 방법:

- 본선 D-1에 사용자가 직접: `cp -r smart-factory-hackathon/skills .agents/`
- 또는 Codex CLI 의 `/skills` 명령으로 등록

이건 **사용자 액션** — 코드로 자동화 어려움 (사용자 홈 디렉터리 접근).

---

## 5. pdf-to-md 활용 시점

| 시점 | 작업 |
|---|---|
| D-2 | `install.bat -Auto` 로 설치 (Documents/pdf-to-md/ 생성됨) |
| D-2 | `QualityLens_기획서.pdf` 변환 → `markdown/` 에 .md 생성 |
| D-2 | 변환된 .md를 우리 `docs/qualitylens_brief.md` 로 복사 후 발표 스크립트 보강에 인용 |
| 본선 후 | 심사 피드백 자료 변환 → 회고용 |

---

## 6. 실행 우선순위 (시간 배분 권장)

D-3 ~ D-Day 사이 약 60 작업 시간 가정.

| 트랙 | 항목 | 소요 | 누적 |
|---|---|---|---|
| 1 | **S-1** 3단계 컬러 코딩 | 2h | 2h |
| 2 | **S-2** Waterfall + Dependence | 4h | 6h |
| 3 | **S-3** 원클릭 수용 + 이력 | 3h | 9h |
| 4 | **S-4** 스트리밍 시뮬레이션 | 5h | 14h |
| 5 | **A-1** 식각 온도 스토리 정렬 | 2h | 16h |
| 6 | **A-2** 비즈니스 KPI 노출 | 1h | 17h |
| 7 | **A-3** P5 주간 리포트 | 2h | 19h |
| 8 | **A-4** 시연 영상 녹화 | 1h | 20h |
| 9 | **4-1** 스킬 description 보강 | 1h | 21h |
| 10 | **pdf-to-md** 설치 + 기획서 변환 | 1h | 22h |
| 11 | 5분 리허설 × 3회 | 3h | 25h |
| 12 | PPTX 슬라이드 4번 스크린샷 갱신 + PDF export | 2h | 27h |
| — | 여유 시간 (디버깅·정리) | 33h | 60h |

**Tier B는 시간 여유 시.** 25시간 안에 본선 준비 완성 가능 — 충분히 여유.

---

## 7. 권장 실행 순서

1. **본 PR 머지** — To-Do 문서 + pdf-to-md 통합
2. **S-1 ~ S-4를 각각 별도 PR**로 — 작은 단위 머지, 토큰 절약
3. 각 PR 머지 후 로컬 `streamlit run app/app.py` 검증
4. **A 시리즈는 묶어서 1~2 PR**
5. D-1 저녁: 발표 자료 폴리시 + 영상 녹화 + 리허설
6. D-Day 아침: roadmap.html 체크리스트로 환경 점검 → 5분 발표
