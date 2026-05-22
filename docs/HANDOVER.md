# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 16:30 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
**P-F 본선 직전 12건 모두 머지 완료!** 필수 7건 + 선택 PR-17/18/9F/28 + 발표/대시보드 동기화 PR-29 (#90~103). 회귀 65/65 PASS. Streamlit Cloud 자동 배포 대기 → 사용자 직접 검증 + 발표 PDF 출력 + 영상 녹화.

## 1. 환경
- 원본 디렉토리: `C:\Users\kik32\workspace\Dacon\smart-factory-hackathon` (워크트리 미사용, origin 직접 작업)
- 브랜치: 머지 후 main 최신화 (`dbed4cd` 이상)
- Python 3.12.4 · 인코딩 `PYTHONIOENCODING=utf-8` 강제 (Windows)
- Plan: `~/.claude/plans/qualitylens-gentle-panda.md` (P-F 섹션 11건 + 검증/핫픽스)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22 16:30: **PR-29** — 발표/대시보드 동기화. slides.html 16→17장 (슬라이드 17=Cpk+색맹+시나리오+Mode 4축 강화) + 색상 Okabe-Ito 통일. freeform §8 4행 추가. dashboard_summary §7 강화 표. P6 §7 강화 패키지 카드.
- 2026-05-22 16:00: **PR-28** 머지(#102) — Mode persistence 3중 방어 핫픽스. Playwright 검증 중 발견된 ?mode strip + widget reset 회귀. widget+persistent sync + URL push + JS click interceptor. 14/14 tests
- 2026-05-22 15:45: **PR-9F** 머지(#101) — 시나리오 토글 (NORMAL/WARN/ANOMALY). SCENARIOS dict + filter_samples_by_scenario. demo_sidebar bool 시그니처 유지 (Pitfall C-1). 12/12 tests
- 2026-05-22 15:30: **PR-18** 머지(#100) — Okabe-Ito 색맹 친화. RiskTier에 symbol(●▲■)/plotly_marker 추가. viz/viz_advanced/dashboard_cards 팔레트 통일. 12/12 tests
- 2026-05-22 15:15: **PR-17** 머지(#99) — Cpk/Cp 공정 능력 게이지 (AIAG SPC). app/lib/cpk.py numpy only + cpk_gauge() + cpk_card_html() + P5 ④섹션. 17/17 tests
- 2026-05-22 14:55: **PR-E5** 머지(#96) — slides.html 12 → 16장 (대시보드/임팩트/시연/평가)
- 2026-05-22 14:35: **PR-24** 머지(#95) — dashboard_cards 6컴포넌트 + P6 + 정적 HTML 미러
- 2026-05-22 14:15: **PR-26** 머지(#94) — sensor_dictionary + action_rules + P3 AI 우선 권고 + CTA
- 2026-05-22 13:45: **PR-22** 머지(#93) — viz_advanced.py 9함수. st.tabs lazy 렌더
- 2026-05-22 13:15: **PR-23** 머지(#92) — onboarding 4→7슬라이드 + SVG inline 3장

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **사용자 직접 검증** — Streamlit Cloud Reboot 후 6 시나리오 (모드 토글 / 페이지 이동 / 업로드 / F5 / Cpk 슬라이더 / 시나리오 토글)
2. **사용자 직접 작업** — slides.html → 브라우저 Ctrl+P → PDF **17장** 출력 + demo_video_guide.md 따라 OBS 녹화 → YouTube Unlisted 업로드
3. **남은 선택 PR** — PR-16 (OEE 3각형 45분) · 사용자 결정 대기

## 4. 차단 요소 / 사용자 확인 대기
- 없음. Auto mode 진행 자율 위임.

## 5. 도구 전환 가이드
**Codex 받을 컨텍스트** (3개): `HANDOVER.md` + `SESSION_LOG.md` 최근 5건 + `~/.claude/plans/qualitylens-gentle-panda.md` (P-F 섹션)
**Codex 복귀**: HANDOVER + SESSION_LOG에 1줄 기록.

## 6. P-F 12건 + 동기화 상태판 (총 13건 머지)
| PR | 제목 | 상태 |
|---|---|---|
| PR-21~E5 | 필수 7건 (Mode/16:9/Onboarding/시각화/UX/대시보드/결과) | ✅ 머지(#90~96) |
| PR-27 | 본선 직전 종합 핫픽스 (9개 버그) | ✅ 머지(#98) |
| PR-17 | Cpk/Cp 공정 능력 게이지 (AIAG SPC) | ✅ 머지(#99) |
| PR-18 | Okabe-Ito 색맹 친화 UI | ✅ 머지(#100) |
| PR-9F | 시나리오 토글 (NORMAL/WARN/ANOMALY) | ✅ 머지(#101) |
| PR-28 | Mode persistence 3중 방어 핫픽스 | ✅ 머지(#102) |
| PR-29 | 발표/대시보드 동기화 (slides 17장 + 색상 통일) | ✅ 머지(#103) |
| 사용자 작업 | reboot 검증 + PDF 17장 출력 + 영상 녹화 + 제출 | ⏳ 대회 제출 |
| PR-16 | OEE 3각형 (45분) — 선택 | ⏳ |

---
*갱신 규칙: 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신. 50줄 초과 시 §2 오래된 항목 → SESSION_LOG로 이동.*
