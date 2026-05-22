# SESSION LOG — 작업 이력 (append-only, 절대 덮어쓰지 않음)

> 매 작업 세션마다 새 항목 추가. HANDOVER.md가 "현재 스냅샷"이라면 이 파일은 "전체 영화".
> 형식: `## YYYY-MM-DD HH:MM KST [도구] — 한 줄 제목` + 본문 5줄 이내

---

## 2026-05-22 14:35 KST [Claude Opus 4.7] — PR-24 작업 대시보드 A+B + 비즈니스 임팩트

- **사용자 피드백 #3 직접 반영**: 첨부 참조 `team_comparison_dashboard_v0.1.html` 같은 결과 시각화 필요. 4영역 패턴 적용 (KPI 4열 + Alert gradient + 비교표 색상 코딩 + Numbered + Verdict).
- **A: Streamlit 페이지** `app/pages/6_📋_종합_대시보드.py` — 7섹션 (KPI / Alert / 비교 / 권장 작업 Top3 / Verdict / 이력 의미 / CTA 4분할).
- **B: 정적 HTML** `docs/presentation/dashboard_summary.html` — A의 정적 미러. 발표 슬라이드 13 임베드 + 시연 네트워크 이슈 시 보험.
- **모듈** `app/lib/dashboard_cards.py`: 6 컴포넌트 — kpi_card, verdict_box, numbered_step, comparison_table, alert_gradient_card, render_kpi_grid. PR-22 viz_advanced.kpi_card_html과 일관.
- **Step 11 이력 의미**: "본 이력은 신규 작업자 교육용 지식 베이스 + 차기 AI 모델 재학습 핵심 데이터" 명시.
- **Step 12 비즈니스 임팩트**: 예방 불량 42건 + 절감 4,200만원 + 응답 3.2분 + 활성 작업자 8명 + action_log 누적 가산.
- **검증**: dashboard_cards 6 함수 import 정상, 회귀 20/20 PASS.

---

## 2026-05-22 14:15 KST [Claude Opus 4.7] — PR-26 인앱 UX (Step 8/9/13/14/15)

- **Step 8 데이터 딕셔너리**: `data/sensor_dictionary.csv` 15센서 한글 매핑 (sensor_003→식각 챔버 온도, sensor_017→증착 두께 등). `app/lib/sensor_names.py` neutral fallback (매핑 없으면 원본 ID).
- **Step 9 액션 룰베이스**: `app/lib/action_rules.py` 10센서 구체 권고 (priority/estimated_minutes/category). P3에 "AI 우선 권고" 섹션 신규 — SHAP top 3 자동 매칭 + `priority_badge()`.
- **Step 13 인앱 도움말**: P3에 `st.popover("💡 이 페이지 사용법")` — 4단계 설명 (샘플 선택→위반 목록→권고→수용).
- **Step 14 탭 간 CTA**: P0/P1/P2/P3 각 페이지 끝에 `st.switch_page()` 버튼 — P0 → P1/P2/P3/P5 4분할, P1 → P2/P3 (tier에 따라), P2 → P1/P3, P3 → P2/P4.
- **Step 7 SHAP 실시간 연결**: P1에서 `tier != normal` 시 `st.session_state["last_alert_sample"]` 저장 → P2 진입 시 활용 (다음 PR에서 자동 입력).
- **검증**: import 정상 (sensor_names + action_rules), graceful (sensor_999 → "sensor_999"), 회귀 20/20 PASS.

---

## 2026-05-22 13:45 KST [Claude Opus 4.7] — PR-22 시각화 풀 확장 (Step 4~7)

- **신규 모듈** `app/lib/viz_advanced.py`: 9함수 — violin_normal_anomaly / correlation_heatmap / boxplot_violations / roi_bar / cumulative_trend / confusion_matrix / pareto_cumulative / top_violations_bar / kpi_card_html.
- **PALETTE** (Okabe-Ito 기반 7색): normal/warn/danger/info/neutral/accent/highlight — PR-18 색맹 친화 UI 대비.
- **P2 통합**: 심화 분석 섹션 + st.tabs (Violin 정상/이상 분포 + 상위5 상관 heatmap). 상위 5 센서 selectbox로 동적.
- **P3 통합**: 위반 센서 시각화 섹션 + st.tabs (편차 분포 박스플롯 + ROI 막대 — 편차σ×100만원 보수적 추정).
- **P4 통합**: 분석 시각화 섹션 + st.tabs (누적 추세 듀얼축 + 혼동행렬 정확도 자동 표시).
- **P5 통합**: Pareto 섹션 st.tabs로 (기본 Pareto + 누적 곡선). 누적 곡선은 80% 기준선 + 필요 센서 수 자동 annotation.
- **성능**: st.tabs lazy 렌더, viz_advanced 단일 모듈로 의존성 추적 용이. 회귀 20/20 PASS.

---

## 2026-05-22 13:15 KST [Claude Opus 4.7] — PR-23 Onboarding 7슬라이드 + SVG 시각화

- **사용자 처방 반영**: "처음 튜토리얼 모달이 상당히 자세해야 함. 실제 예시 동작도 자연스럽게 보여주는 것도 좋을 듯!" → onboarding.py 4슬라이드 → **7슬라이드** 확장.
- **신규 슬라이드 5/6/7**:
  - (5) 데모 따라하기 — P1→P2→P3→P4 흐름 SVG (4단계 색상 카드 + 화살표 + 실제 값: 샘플 #1305, 81.2%, Feature_59 78%)
  - (6) SHAP 비전문가 해설 — Waterfall 정적 SVG (base 0.066 → +0.45 Feature_59 → final 0.812 81%, 색상 코딩 빨강/초록 + 한줄 해석)
  - (7) 조치 흐름 — 5단계 원형 배지 (감지→권고→수용→기록→복귀, 81% → 12% 복귀 + 100만원 절감 결과)
- **렌더 함수 분리**: 각 슬라이드를 `_slide_welcome / _upload / _four_domains / _cycle / _demo_walkthrough / _shap_explainer / _action_flow` 7개 함수로 분리 → 유지보수 용이.
- **자산 전략**: Streamlit dialog 내 plotly 회피 (메모리 누수). SVG inline으로 즉시 렌더 + scripts/generate 외부 의존성 0.
- **다음**: PR-22 시각화 풀 확장 (5페이지 P0/P1 차트). PR-26 인앱 UX (데이터 딕셔너리 + CTA + 빈 화면).

---

## 2026-05-22 12:55 KST [Claude Opus 4.7] — PR-E1R 발표 자료 16:9 변환

- **사용자 피드백 #4**: "발표 자료는 16:9 비율로 무조건 진행해야 된다고 합니다!" 즉시 반영.
- **CSS 변경** (`docs/presentation/slides.html` 라인 6-116): @page size A4 landscape → 320×180mm, .slide width/height 273×186mm → 320×180mm + aspect-ratio 16/9.
- **폰트 비례 확대**: 헤더 22→28pt, h2 14→19pt, body 12→15pt, card h3 11→14pt, footer 8.5→11pt, cover h1 44→56pt, logo 56→72pt, tagline 16→22pt.
- **신규 스타일**: `.kpi-grid`/`.kpi-card` (KPI 4열 그리드, 참조 dashboard 패턴) + `.verdict.win/warn/bad` (PR-24 종합 대시보드와 일관). PR-E5 슬라이드 13~16에서 사용 예정.
- **화면 미리보기 폴리시**: `@media screen { .slide { transform: scale(0.85); } }` — 16:9 슬라이드 전체가 화면에 들어오도록.
- **검증**: 사용자가 브라우저에서 열고 Ctrl+P → PDF 저장 (여백 None) → 12장 모두 16:9 한 페이지 확인.

---

## 2026-05-22 12:40 KST [Claude Opus 4.7] — PR-21 Mode + 상태 전역화 (P-F 첫 PR)

- **진짜 원인 발견**: PR-7 widget key는 radio만 보존, `@st.cache_data` 캐시 키에 source 미포함 → 페이지 이동 시 첫 호출의 자동 감지 source가 영구 캐싱됨. 사용자 검증 후 reboot에서도 재현 확인.
- **Fix A** (~200줄, 10개 파일): app.py + pages/0~5 모든 cached 함수 호출부에 `source=source` 명시. data_loader `sidebar_badge(source)`, `status_banner(source)` 시그니처 확장.
- **Fix B** (demo.py): `ensure_demo_state()` + `get_source()` 헬퍼 추가. session_state SSoT 4키 (`_demo_mode_radio`, `_demo_mode`, `_data_source`, `user_data`) 일관성 보장.
- **Step 3 user_data SSoT** (사용자 PM 처방): P0 업로드 결과 → `st.session_state["user_data"]` 저장 → app.py 메인 카드가 우선 사용. 페이지 간 데이터 흐름 끊김 해결.
- **회귀 테스트**: `tests/unit/test_mode_global_state.py` 10건 신규 (resolve_source 명시 우선/cached signature/ensure_demo_state/get_source/user_data SSoT). 전체 20/20 PASSED.

---

## 2026-05-22 14:35 KST [Claude Opus 4.7] — P-E 발표 산출물 3종 (PR-E1+E2+E3 묶음)

- **PR-E1 slides.html**: 가로 A4 12장 HTML/CSS @media print + Noto Sans KR. MVP 4단계 흐름 (표지→문제정의 3→AI 활용 3→플랫폼 2→시연→Q&A→로드맵). 사용자가 Ctrl+P → PDF 출력.
- **PR-E2 freeform.html**: 단일 페이지 스크롤 보조 자료 (10섹션) — About, 문제, AI, 플랫폼, MVP, 벤치마크, Q&A 10답변, 의사결정 로그(11건), 기술 스택, 로드맵.
- **PR-E3 demo_video_guide.md**: 5분30초 시나리오 + 자막 SRT + 녹화 체크리스트 + 비상 시나리오 + YouTube 업로드 매뉴얼. 사용자가 OBS 녹화·업로드.
- **평가 매핑**: 문제정의 20점 + AI 25점 + 플랫폼 20점 + MVP 25점 + 발표 10점 = 100점 전 항목 직접 기여.
- **다음**: commit + PR + merge → **P-B + P-E 완성** → 사용자가 PDF 출력 + 영상 녹화 + 대회 제출.

## 2026-05-22 13:55 KST [Claude Opus 4.7] — P-B 확장 PR-8+11 묶음 (UI 디테일 + 브랜딩)

- **PR-8 KPI delta**: `app/app.py:94-102` col2 이상 판정 → `delta=+/-Xp.p (평소 6.6% 대비)` `delta_color="inverse"`
- **PR-8 SHAP brief**: `pages/2_🔍_원인_분석.py` waterfall 직전 `st.error()` 자동 텍스트 — top SHAP 변수 + 영향도 %
- **PR-8 toast/balloons**: `pages/3_🛠_조치_가이드.py:143` 수용 버튼 → `st.toast()` + `st.balloons()` 추가
- **PR-11 pitch_30s.md 신규**: 30초 낭송 스크립트(균형 톤) + 핵심 카피 5종 + Q&A 5종 답변 템플릿
- **PR-11 README 보강**: 차별화 3개 + 3대 페르소나 매트릭스 + 4영역 통합(품질/안전/설비/생산) + MVP 사용 흐름 3단계
- **다음**: commit + PR + merge → PR-E1 발표 PDF HTML (120분)

## 2026-05-22 13:15 KST [Claude Opus 4.7] — P-B 확장 PR-14+15 묶음 (SPC + Pareto)

- **PR-14 (SPC)**: `app/lib/spc.py` 신규. Western Electric Rules 4종(3σ/2σ/1σ/연속 8점) 자동 검출. `compute_limits`/`detect_western_electric`/`violation_summary`.
- **PR-15 (Pareto + 히스토그램)**: `app/lib/viz.py` 확장 (`spc_chart`, `pareto_chart`, `sensor_histogram` 3종). 80/20 누적% 라인 + 임계선 마킹.
- **신규 페이지**: `app/pages/5_📊_SPC_Pareto.py` — SPC 관리도 + Pareto + 센서 분포 3섹션. PR-10 timestamp 시계열 X축 활용.
- **단위 검증**: 명백한 이상점(>3σ) 1개 삽입 → Rule 1 검출 ✅. viz/spc.py 모두 ast.parse OK.
- **다음**: commit + PR + merge → PR-8 (UI 디테일, 45분)

## 2026-05-22 12:50 KST [Claude Opus 4.7] — P-B 확장 PR-10 머지 (#86)

- **scripts/build_demo_result.py 신규** — RANDOM_STATE=42 결정성 보장
- **51 샘플 / 5분 간격 / 5컬럼** (sample_id + timestamp + pred_proba + pred_label + state)
- **스토리텔링**: 정상 36 → 경고 6 → 위험 9 → 복귀 (시연 임팩트)
- **다음**: PR-14+15 (SPC + Pareto) 묶음 진행

## 2026-05-22 12:30 KST [Claude Opus 4.7] — P-B 확장 PR-19+20 묶음 (MVP 핵심)

- **PR-19 (CSV 업로드)**: `app/pages/0_📤_데이터_업로드.py` + `app/lib/upload.py` 신규. 591 sensor_NNN 컬럼 검증·정렬·예측. 누락 자동 0 채움. utf-8/utf-8-sig/cp949 자동 감지. 결과 CSV 다운로드.
- **PR-20 (onboarding 모달)**: `app/lib/onboarding.py` 신규. `st.dialog` 4슬라이드 워크스루(정체성 → 업로드 가이드 → 4영역 흐름 → Predict→Explain→Act). 사이드바 재오픈 버튼.
- **app.py 통합**: `maybe_show_onboarding()` 진입 호출, `reopen_button_sidebar()` 추가.
- **단위 검증 PASS**: 591 컬럼 + 99/591 입력 → 492 자동 채움 + 경고 메시지 + 템플릿 (3×592).
- **다음**: commit + PR + merge → PR-8 UI 디테일 (45분)

## 2026-05-22 11:50 KST [Claude Opus 4.7] — P-B 확장 PR-7 mode 버그 fix 머지 (#84)

- **문제**: `app/lib/demo.py:11-31`의 `st.sidebar.radio(..., index=0)` 하드코딩 + session_state 미사용 → 페이지 이동 시 라디오 강제 reset
- **수정**: widget `key="_demo_mode_radio"` 도입으로 Streamlit 자동 보존 + 외부 읽기용 `_demo_mode` 별도 미러
- **호출처 영향**: 0 (반환 시그니처 동일, app.py + pages/1~4 무변경)
- **검증**: ast.parse OK, import OK, lines 52
- **다음**: PR-19+20 묶음 → PR-8 → ...

## 2026-05-22 11:32 KST [Claude Opus 4.7] — P-B 확장 plan 최종 확정 (필수 11개)

- **MVP 핵심 갭 발견** — 사용자 피드백: 실무자 자기 데이터 업로드 + 사용 안내 모달 부재
- **PR-19/20 필수 격상** — CSV 업로드 90분, onboarding 모달 45분
- **평가 배점 매핑** — PR-7/19/20/10 = MVP 구현 25점 직접 / PR-8/14/17 = AI 활용 25점
- **plan 파일**: `C:\Users\kik32\.claude\plans\qualitylens-gentle-panda.md` (10번 갱신, 변경 이력 누적)
- **총 작업**: 11개 필수 + 5개 여유 = 약 9.7시간 (Phase A 코드 7시간 + Phase B 발표 3시간)

## 2026-05-22 09:50 KST [Claude Opus 4.7] — P-B/PR-2 캡처 인프라 머지 완료 (#83)

- **이관**: 루트 18종(slide-1~8, qa-slide1~8, thumbnails, test-slide2) → `docs/captures/v0/{slides,qa,./}` (git mv)
- **신규**: `docs/captures/INDEX.md` 발행 규칙 + `v0/notes.md` + `v1/README.md` 가이드
- **운영 규칙**: 신규 v 발행 트리거 4종 — UI/폰트/소스/리허설
- **다음**: PR-7 → PR-19 → PR-20 → ...

## 2026-05-22 09:13 KST [Claude Opus 4.7] — P-B/PR-3 HANDOVER + SESSION_LOG 구축

- **목적**: Claude ↔ Codex 전환 시 컨텍스트 손실 0으로 만들기 위한 인계 인프라
- **산출**: `docs/HANDOVER.md`(50줄, 현재 스냅샷) + `docs/SESSION_LOG.md`(이 파일, append-only)
- **운영 규칙**: HANDOVER 50줄 한도, 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신
- **다음**: PR-2 캡처 인프라 → PR-4 대시보드 → PR-6 발표 보강

## 2026-05-22 09:10 KST [Claude Opus 4.7] — P-B/PR-1 Hotfix 머지 완료 (#81)

- **트리거**: Streamlit Cloud `FileNotFoundError: secom_X_test_dummy.pkl 부재` → 앱 시작 실패
- **5섹션 분석 결론**: A(dummy 7종 커밋, ~5MB) + E(graceful degradation) 조합
- **변경**: `.gitignore` 화이트리스트 + `app/app.py` try/except + dummy 산출물 7개 신규
- **검증**: 로컬 `from lib.data_loader import load_test_set` → (314, 591) test set 정상
- **다음**: PR #81 머지 후 Streamlit Cloud 재배포 확인 필요 (사용자 또는 PR-2 캡처에서)

## 2026-05-22 08:55 KST [Claude Opus 4.7] — P-B 스펙 작성 + 사용자 승인

- **산출**: `docs/spec_p_b_streamlit_deploy_hotfix.md` (15섹션, 280줄, 6 sub-PR 분할 계획)
- **결정**: 한글 폰트 점검은 P-C로 분리, P-B는 운영 안정화 + 협업 인프라에 집중
- **사용자 확인 사항**: 본선 진행 중, Codex 라우팅 = 하이브리드(5.4/5.5), 캡처는 docs/captures/v{n}/, real은 본선 후 연구
- **셀프 리뷰 통과**: 8/10 항목 ✓, 일정 현실성만 ❌ → 본선 후로 PR-5 미루기로 합의

---
*과거 세션(P-A: 2026-05-19 ~ 2026-05-21) 로그는 `docs/progress/` 폴더 참조. P-B 시작 시점부터 이 파일에 누적.*
