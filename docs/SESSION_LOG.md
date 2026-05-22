# SESSION LOG — 작업 이력 (append-only, 절대 덮어쓰지 않음)

> 매 작업 세션마다 새 항목 추가. HANDOVER.md가 "현재 스냅샷"이라면 이 파일은 "전체 영화".
> 형식: `## YYYY-MM-DD HH:MM KST [도구] — 한 줄 제목` + 본문 5줄 이내

---

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
