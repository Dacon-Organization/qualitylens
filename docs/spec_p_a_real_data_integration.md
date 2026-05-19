# Spec — P-A 실데이터 통합 & 검증 (UCI SECOM)

> 작성일: 2026-05-19 (D-3)
> 본선: 2026-05-22(금) 09:00 KST
> 작성자: 이동원 (kik328288@gmail.com)
> 모델 라우팅: 설계·검증 시나리오·비교 분석 = **Opus** / 스크립트 수정·HTML 렌더 헬퍼·반복 작업 = **Sonnet**
> 상태: 초안 → 사용자 검토 대기

---

## 1. 배경

QualityLens는 본선 D-3 시점까지 T1~T5 파이프라인과 S1~S4 본선 폴리시(3단계 컬러, SHAP Waterfall, 원클릭 수용, 스트리밍)가 모두 더미 데이터 기반으로 완성되어 있다. 그러나 다음 갭이 본선 평가 위험으로 남아 있다.

1. **실데이터 미검증** — `data/raw/` 가 비어 있고 더미 폴백만 가동 중. 발표 수치의 근거가 약함.
2. **기획서 약속 vs 실증 부재** — "SECOM 실데이터 학습 완료"를 슬라이드와 README에서 주장하려면 산출물이 있어야 함.
3. **단계별 결과 가시화 부족** — `docs/roadmap.html` 외에는 단계 결과를 한눈에 보여주는 HTML 보고서가 없음. 발표 백업 자료로도 부족.

P-A는 이 갭 중 가장 기반이 되는 "실데이터 파이프라인 완주 + 더미 대비 비교 + 단계별 HTML 보고서 + Playwright E2E 검증" 4점 세트를 다룬다. P-B(한글 폰트 전수 점검), P-C(HTML 시각화 자동 누적 시스템), P-D(10단계 전문가·벤치마킹)는 별도 spec.

## 2. 목표

- **G1**: UCI SECOM 실데이터(1567 × 591)로 T1→T2→T3 파이프라인을 무에러 완주, 산출물을 `_real` 접미사로 보관
- **G2**: 더미와 실데이터의 성능·SHAP·분포를 자동 비교하는 `docs/validation/real_vs_dummy_report.md` 생성
- **G3**: 단계별(T1 / T2 / T3 / 비교 / Playwright) **단독 HTML 보고서 5종 + 인덱스** 자동 생성 — 발표 백업·심사 위원 부록 자료
- **G4**: Playwright MCP로 5페이지 × 2 모드 스모크 + 식각 온도 골든 패스 자동 재현, 스크린샷 보관
- **G5**: Git 워크플로우 (pull → branch → commit → push → PR → auto merge) 를 GitHub MCP 기반으로 정착시켜 6개 sub-PR 단위로 머지

## 3. 비목표 (YAGNI)

- 실시간 데이터 수집 파이프라인 (SECOM 정적 데이터셋만)
- 다공정 확장 (반도체 식각 단일 시나리오)
- 모델 하이퍼파라미터 재튜닝 (기존 학습 설정 그대로 유지, 데이터만 교체)
- SHAP 의미 라벨 실증 (SECOM은 익명화 데이터 — 라벨 매핑은 기획 가정으로 유지)
- 단계별 HTML 보고서의 자동 인덱스화 시스템 (P-C에서 일반화)

## 4. 검증 1차 목적

사용자 확인: **모델 성능 수치 신뢰 확보 (1번)를 코어로**, 시간 여유 시 **3개 교차 검증 (4번)** 으로 확장. 단 SECOM이 익명화 데이터임을 정직하게 다룬다 — "센서 의미"는 검증 대상에서 제외하고 분포·기여도 패턴만 본다.

## 5. 데이터 입수 & 보관

- **방식**: 원본 데이터를 git에 직접 커밋 (사용자 결정, ~1.5 MB, LFS 불필요)
- **위치**: `data/raw/secom.data`, `data/raw/secom_labels.data`
- **라이선스**: `data/raw/LICENSE.md` 신규 — UCI Machine Learning Repository 출처·인용 표기
- **`.gitignore` 정리**: 기존에 `data/raw/*` 패턴이 있다면 두 파일만 `!` 예외 처리
- **재현 도구**: `scripts/00_download_secom.py` 신규 — UCI에서 자동 다운로드 (CI·신규 개발자 재현용, 본선장에는 불필요)

## 6. 산출물 보관 구조

사용자 결정에 따라 **real / dummy 둘 다 보관, real을 기본 로드, dummy를 폴백**.

```
data/processed/
├── secom_train_real.pkl
├── secom_test_real.pkl
├── secom_train_dummy.pkl
└── secom_test_dummy.pkl

models/
├── xgb_secom_real.joblib
├── xgb_secom_dummy.joblib
├── threshold_table_real.csv
├── threshold_table_dummy.csv
├── shap_explainer_real.pkl
├── shap_explainer_dummy.pkl
├── shap_top20_real.csv
├── shap_top20_dummy.csv
├── shap_waterfall_demo_real.pkl
└── shap_waterfall_demo_dummy.pkl
```

## 7. 컴포넌트 변경 목록

| 파일 | 종류 | 변경 내용 | 모델 |
|---|---|---|---|
| `data/raw/secom.data`, `secom_labels.data` | 신규 | UCI 원본 커밋 | — |
| `data/raw/LICENSE.md` | 신규 | UCI 라이선스·인용 표기 | Sonnet |
| `scripts/00_download_secom.py` | 신규 | UCI 자동 다운로드 (재현용) | Sonnet |
| `scripts/01_preprocess.py` | 수정 | `--source {real,dummy}` 플래그 + 파일명 분기 | Sonnet |
| `scripts/02_train.py` | 수정 | 동일 플래그 + 모델·임계값 파일명 분리 | Sonnet |
| `scripts/03_shap.py` | 수정 | 동일 플래그 + SHAP 산출물 파일명 분리 | Sonnet |
| `scripts/04_compare_real_vs_dummy.py` | 신규 | 두 결과 로딩 → 표·차트·md·HTML 자동 생성 | **Opus** |
| `app/lib/data_loader.py` | 신규 | real 우선 → dummy 폴백 로직 단일화 + 사이드바 배지 데이터 노출 | Sonnet |
| `app/lib/report_render.py` | 신규 | HTML 보고서 공용 헤더·푸터·CSS·plotly 임베드 헬퍼. `scripts/0*.py` 에서도 `from app.lib.report_render import write, build_index` 로 import (기존 `app/lib/` 공용 사용 패턴 유지) | **Opus** |
| `app/lib/fonts.py` | 신규(또는 강화) | matplotlib·plotly·HTML CSS 3중 한글 폰트 적용 | Sonnet |
| `app/app.py` + `pages/*` | 수정 | `data_loader` 사용 + 사이드바 데이터 소스 배지 | Sonnet |
| `scripts/01_preprocess.py` (HTML 산출) | 추가 라인 | T1 끝에 `report_render.write("preprocessing", ctx)` | Sonnet |
| `scripts/02_train.py` (HTML 산출) | 추가 라인 | T2 끝에 `report_render.write("training", ctx)` | Sonnet |
| `scripts/03_shap.py` (HTML 산출) | 추가 라인 | T3 끝에 `report_render.write("shap", ctx)` | Sonnet |
| `scripts/04_compare_real_vs_dummy.py` (HTML 산출) | 자동 | 비교 보고서도 HTML 동시 출력 | (자동) |
| `tests/e2e/playwright_scenarios.md` | 신규 | MCP 호출 시퀀스 + 어설션 체크리스트 | **Opus** |
| `tests/e2e/run_playwright_qa.py` (선택) | 신규 | Playwright MCP 실행 결과를 `05_playwright_qa.html` 로 묶어주는 헬퍼 | Sonnet |
| `docs/reports/index.html` | 신규 | 5개 보고서로 통하는 카드 + D-Day 카운트다운 | **Opus** |
| `docs/validation/real_vs_dummy_report.md` | 자동 생성 | 4번 스크립트 산출물 | (자동) |
| `assets/qa/playwright/{real,dummy,golden_path}/` | 신규 디렉터리 | Playwright 스크린샷 보관 | (자동) |
| `assets/vendor/plotly.min.js` | 신규 | 오프라인 폴백용 plotly 미러 | Sonnet |
| `README.md` | 수정 | 실데이터 검증 섹션 + 본선 메시지 추가 | Sonnet |

## 8. 데이터 플로우 — real 우선, dummy 폴백

```python
# app/lib/data_loader.py (의사 코드)
def load_artifacts(source: str | None = None) -> Bundle:
    """
    source 우선순위:
      1. 명시 인자 source = 'real' | 'dummy'
      2. 환경변수 DEMO_MODE
      3. 기본: real 시도 → 실패 시 dummy 폴백
    """
    forced = source or os.getenv("DEMO_MODE")

    if forced == "dummy":
        return _load_bundle("dummy")

    try:
        bundle = _load_bundle("real")
        st.session_state["_data_source"] = "real"
        return bundle
    except (FileNotFoundError, EOFError):
        st.warning("실데이터 산출물 없음 → 더미 폴백")
        bundle = _load_bundle("dummy")
        st.session_state["_data_source"] = "dummy"
        return bundle
```

- 사이드바에 작은 배지로 현재 데이터 소스 표시: `🟢 real` / `🟡 dummy`
- 본선 시연 기본값: `DEMO_MODE=real`
- 개발·디버깅: `DEMO_MODE=dummy` 강제 가능

## 9. 비교 보고서 (`docs/validation/real_vs_dummy_report.md` + `docs/reports/04_real_vs_dummy.html`)

자동 생성 목차:
1. **데이터 비교 표** — 행 수, 피처 수, 결측치율, 양/음성 비율, 시간 범위
2. **분포 비교** — 상위 5개 피처 히스토그램 (real vs dummy) → PNG + plotly
3. **모델 성능 표** — ROC-AUC / PR-AUC / Precision@thr / Recall@thr / F1
4. **임계값 곡선** — Precision-Recall, ROC 두 곡선 겹쳐 표시
5. **SHAP Top 10 비교** — real 상위 10 vs dummy 상위 10 겹침 분석
6. **데모 4건 Waterfall 비교** — 같은 샘플 ID 4건의 real / dummy 기여 차이
7. **결론 요약 자동 문장** — "실데이터 ROC-AUC = X.XX, 더미 = Y.YY. 차이 Z." 1단락

마크다운과 HTML이 같은 데이터 소스로 동시 출력 — 발표용은 HTML, 부록 인쇄용은 마크다운.

## 10. 단계별 HTML 시각화 보고서 (G3 핵심)

| 단계 | 파일 | 핵심 내용 |
|---|---|---|
| T1 전처리 | `docs/reports/01_preprocessing.html` | 데이터 형상 표, 결측치율 바, 양/음성 비율, 분포 샘플 (real vs dummy 토글) |
| T2 학습 | `docs/reports/02_training.html` | ROC·PR 곡선, 혼동 행렬, 임계값 곡선, threshold table, feature importance |
| T3 SHAP | `docs/reports/03_shap.html` | Top 20 바, Waterfall 4건, Dependence 2건 (plotly 인라인) |
| 비교 | `docs/reports/04_real_vs_dummy.html` | 9번 섹션 보고서의 HTML 버전 |
| Playwright | `docs/reports/05_playwright_qa.html` | 트랙①·트랙② 스크린샷 갤러리 + 어설션 체크 표 |
| 인덱스 | `docs/reports/index.html` | 위 5개 카드 + D-Day 카운트다운 + 현재 데이터 소스 배지 |

**구현 원칙**:
- 외부 의존 최소화 — vanilla HTML/CSS + plotly CDN, 본선장 오프라인 시 `assets/vendor/plotly.min.js` 로컬 폴백
- 한글 폰트는 `<style>`에서 `font-family: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif` 명시
- `app/lib/report_render.py` 가 공용 헤더/푸터/CSS 제공 — 각 스크립트는 본문 섹션만 채움
- 인덱스는 D-Day 카운트다운 + 카드 hover 효과 정도 (`roadmap.html` 톤과 일치)
- **P-C와의 관계**: P-C는 이 5개 보고서를 자동 인덱스화·확장하는 시스템. P-A는 보고서 자체 + 1차 인덱스를 직접 만들어 자기 완결.

## 11. Playwright MCP 자동 검증

### 트랙 ① — 5페이지 스모크 (필수)
- DEMO_MODE=real 로 앱 기동
- P1~P5 순차 방문, 각 페이지에서:
  - 콘솔 에러 0건 (`mcp__playwright__browser_console_messages`)
  - 사이드바 데이터 소스 배지 "🟢 real" 텍스트 존재 (`browser_snapshot`)
  - 핵심 차트 컨테이너 존재 (`canvas`, `svg`, `[data-testid='stPlotlyChart']`)
  - 전체 스크린샷 → `assets/qa/playwright/real/P1.png` ~ `P5.png`
- DEMO_MODE=dummy 로 재기동 → 동일 5페이지 스크린샷 → `assets/qa/playwright/dummy/`

### 트랙 ② — 식각 온도 골든 패스 (필수)
1. P2 "▶️ 시뮬레이션 시작" 클릭 → 11초 대기 → FAIL 주입 확인 (게이지 빨강 배지 어설션) → `golden_path/step1.png`
2. P3 진입 → SHAP Waterfall 렌더 확인 (top 기여 센서 텍스트 존재) → `step2.png`
3. P4 진입 → "✅ 수용" 버튼 클릭 → 토스트/카운터 증가 → `step3.png`
4. P5 진입 → 조치 이력 탭에서 방금 수용 항목 한 줄 이상 → `step4.png`
5. P1 복귀 → 시뮬레이션 정상 복귀 후 KPI 녹색 → `step5.png`

### 결과 산출물
- `tests/e2e/playwright_scenarios.md` — MCP 호출 시퀀스 + 어설션 체크리스트
- `docs/reports/05_playwright_qa.html` — 스크린샷 갤러리 + 통과/실패 표 (자동 생성)

### 부가 가치
- P-B(한글 폰트 점검) **사전 가시화** — 스크린샷에 깨진 글자가 있으면 P-B 작업 범위가 자동 도출
- 본선 백업 — Streamlit이 본선장에서 안 켜져도 스크린샷이 발표 자료 폴백 (기획서 G8 Fail-Safe 일부 충족)
- 회귀 방어 — 후속 S5~ 작업이 골든 패스를 깨면 즉시 감지

## 12. 에러 처리 & 폴백

| 시나리오 | 대응 |
|---|---|
| SECOM 데이터 파싱 실패 | T1 try/except + 명확한 에러 메시지 + dummy 자동 폴백 |
| 본선장 메모리 부족 (591 피처 × 1567 행) | float64 → float32 다운캐스트, XGBoost `tree_method='hist'` |
| joblib 버전 충돌 | `requirements.txt` 에 `scikit-learn`·`xgboost`·`joblib` 정확 버전 핀 |
| 앱 시작 시 `*_real.joblib` 누락 | data_loader가 dummy 폴백 + 사이드바 노란 배지 |
| 한글 차트 깨짐 | `app/lib/fonts.py` 가 matplotlib·plotly·HTML CSS 3중 폰트 명시 |
| SHAP 메모리 폭발 | `--shap-sample N` 옵션 (실데이터 1567 → 100 샘플로 충분) |
| plotly CDN 차단 | `assets/vendor/plotly.min.js` 로컬 폴백 자동 사용 |

## 13. Git 워크플로우 (G5)

CLAUDE.md `skills/git-workflow/` 규칙 + GitHub MCP 활용.

### spec 커밋 (이 PR — 단일)

| 단계 | 명령 / 도구 |
|---|---|
| pull | `git fetch origin main && git pull --rebase origin main` |
| branch | 현재 워크트리 브랜치 `claude/youthful-mcnulty-4f813e` 사용 |
| commit | HEREDOC + Co-Authored-By + 한국어 메시지 |
| push | `git push -u origin claude/youthful-mcnulty-4f813e` |
| PR | **GitHub MCP** `mcp__github__create_pull_request` (base=main, 한국어 title·body) |
| auto merge | **1차**: GitHub MCP `mcp__github__merge_pull_request` (CI 통과 후). **폴백**: `gh pr merge --auto --squash` (MCP 미가용 시) |

### 구현 시점 sub-PR 분할 (writing-plans에서 확정)

| PR | 내용 | 추정 LOC |
|---|---|---|
| PR-1 | UCI 데이터 + `00_download_secom.py` + LICENSE | ~80 |
| PR-2 | T1~T3 `--source` 플래그 + `data_loader.py` + `fonts.py` | ~250 |
| PR-3 | `04_compare_real_vs_dummy.py` + 비교 보고서 (md + html) | ~300 |
| PR-4 | 단계별 HTML 리포트 5종 + 인덱스 + `report_render.py` | ~400 |
| PR-5 | Playwright 시나리오 + 결과 리포트 | ~200 |
| PR-6 | 발표 자료 + README 보강 + 사이드바 배지 | ~50 |

각 sub-PR은 GitHub MCP로 생성, CI 통과 시 auto merge.

## 14. 실행·검증 순서

```powershell
# 1) 데이터 입수 (최초 1회)
python scripts/00_download_secom.py     # 또는 수동 배치

# 2) 실데이터 파이프라인 (HTML 보고서 자동 출력)
python scripts/01_preprocess.py --source real     # → docs/reports/01_preprocessing.html
python scripts/02_train.py --source real          # → docs/reports/02_training.html
python scripts/03_shap.py --source real           # → docs/reports/03_shap.html

# 3) 더미 결과 갱신
python scripts/01_preprocess.py --source dummy
python scripts/02_train.py --source dummy
python scripts/03_shap.py --source dummy

# 4) 비교 보고서 + HTML
python scripts/04_compare_real_vs_dummy.py        # → docs/validation/*.md + docs/reports/04_real_vs_dummy.html

# 5) 앱 검증
$env:DEMO_MODE = "real"
streamlit run app/app.py                          # 사이드바 🟢 real

# 6) Playwright MCP 자동 검증 (트랙 ① + ②)
# Claude Code 세션에서 tests/e2e/playwright_scenarios.md 의 시퀀스 실행
# → assets/qa/playwright/ 스크린샷 + docs/reports/05_playwright_qa.html

# 7) 인덱스 페이지 갱신
python -c "from app.lib.report_render import build_index; build_index()"   # → docs/reports/index.html
```

## 15. 검증 통과 기준

- [ ] `data/raw/secom.data` 가 1567 × 591 로 정확히 로드
- [ ] real ROC-AUC ≥ 0.65 (SECOM 표준 벤치마크 0.70대 근처)
- [ ] real SHAP top 20 산출 완료
- [ ] `docs/validation/real_vs_dummy_report.md` + HTML 동시 생성
- [ ] `docs/reports/0{1,2,3,4,5}_*.html` 5개 + `index.html` 모두 존재
- [ ] 모든 HTML 보고서에서 한글이 깨지지 않음 (육안 검증, P-B 사전 점검 겸용)
- [ ] 앱이 `DEMO_MODE=real` / `DEMO_MODE=dummy` 양쪽에서 5페이지 무에러
- [ ] 사이드바 데이터 소스 배지 정상 표시
- [ ] Playwright 트랙 ① 콘솔 에러 0건 + 스크린샷 10장
- [ ] Playwright 트랙 ② 골든 패스 5단계 스크린샷 5장
- [ ] 6개 sub-PR 모두 GitHub MCP 경로로 생성·머지

## 16. 평가 위원 방어 메시지 (발표 자료 보강)

| 위치 | 추가 문장 |
|---|---|
| README "데이터" 섹션 | "UCI SECOM 실데이터 1567행 591피처로 학습·검증 완료. 더미 모드는 폴백 전용." |
| 슬라이드 4 (기능) | "Real Data Verified — 실데이터 ROC-AUC X.XX (참고: SECOM 표준 0.70대)" |
| 슬라이드 7 (시연) | "사이드바 데이터 소스 배지로 real/dummy 실시간 가시화" |
| Q&A 노트 | "Q: 라벨이 진짜 식각 온도인가? → A: SECOM은 익명화 데이터이므로 의미 라벨은 기획 가정. 분포·기여도 패턴은 실데이터 그대로." |
| 발표 부록 | `docs/reports/index.html` 전체 화면 — 단계별 보고서 5종을 슬라이드 백업으로 즉시 호출 |

## 17. 위험 요소

| 위험 | 영향 | 완화책 |
|---|---|---|
| UCI 사이트 다운 | 데이터 입수 실패 | 원본을 git 직접 커밋 — 본선장 인터넷 끊겨도 OK |
| 실데이터 ROC-AUC가 너무 낮음 (< 0.6) | 신뢰성 손상 | 임계값 표만 갱신, 발표에서 "데모용 임계값"으로 명시 (모델 재튜닝은 비목표) |
| HTML 보고서 plotly CDN 차단 | 빈 차트 | `assets/vendor/plotly.min.js` 로컬 폴백 자동 사용 |
| Playwright 트랙 ② 시뮬레이션 타이밍 불안정 | E2E 실패 | `browser_wait_for` 명시적 대기 + 골든 패스 결정론적 시드 강제 |
| GitHub Actions CI 실패로 auto merge 미동작 | 머지 지연 | 수동 머지 폴백 (사용자 결정), CI 룰 사전 확인 |
| 6개 sub-PR 머지 충돌 | 작업 시간 손실 | PR-1~PR-6 의존성 순서대로 직렬 머지, 병렬 금지 |

## 18. 후속 작업

본 spec 머지 후:

1. `writing-plans` 스킬로 P-A 구현 계획서 작성 → `docs/plan_p_a_real_data_integration.md`
2. PR-1 ~ PR-6 순차 진행 (GitHub MCP 활용)
3. P-A 완료 후 P-B (한글 폰트 전수 점검) 진입 — Playwright 스크린샷이 이미 1차 점검 완료
4. P-D (10단계 전문가 + 벤치마킹) 는 Opus 서브에이전트 위임으로 P-A·P-B와 병렬
5. P-C (HTML 시각화 자동 누적 시스템) 는 P-A의 5개 보고서를 기반으로 일반화

---

## 부록 A — 사용자 결정 사항 요약

1. **검증 목적**: 1번 (성능 수치 신뢰) 코어 + 4번 (3개 교차) 욕심. SHAP 의미 검증은 익명화 한계 인정하고 분포·기여도만.
2. **데이터 입수**: 옵션 2 (원본 git 직접 커밋, LFS 불필요).
3. **산출물 보관**: 옵션 1 (real·dummy 둘 다 보관, real 기본 로드, dummy 폴백).
4. **E2E 검증**: Playwright MCP 사용 (5페이지 × 2 모드 + 골든 패스 5단계).
5. **HTML 보고서**: 단계별 5종 + 인덱스 자동 생성 — 발표·심사 부록 자료.
6. **Git 워크플로우**: pull → branch → commit → push → PR → auto merge (GitHub MCP `mcp__github__create_pull_request` / `merge_pull_request`).
