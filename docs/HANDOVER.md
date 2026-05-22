# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 12:40 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
**P-F 진행 중** — P-F PR-21(#90)+PR-E1R(#91)+PR-23(#92) 머지, **PR-22 시각화 풀 확장 완료** (viz_advanced 9함수 + P2/P3/P4/P5 통합) → 다음 PR-26 인앱 UX.

## 1. 환경
- 원본 디렉토리: `C:\Users\kik32\workspace\Dacon\smart-factory-hackathon` (워크트리 미사용, origin 직접 작업)
- 브랜치: `claude/p-f-pr21-mode-global-state` (PR-21용, 머지 후 새 브랜치)
- Python 3.12.4 · 인코딩 `PYTHONIOENCODING=utf-8` 강제 (Windows)
- Plan: `~/.claude/plans/qualitylens-gentle-panda.md` (P-F 섹션 11건)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22 13:45: **PR-22** — viz_advanced.py 신규 9함수 (violin / heatmap / boxplot / roi / cumulative / confusion / pareto_cumulative / top_violations / kpi_card_html). P2 (정상/이상 분포+상관) + P3 (박스플롯+ROI) + P4 (누적 추세+confusion) + P5 (Pareto 누적 곡선) 통합. st.tabs lazy 렌더.
- 2026-05-22 13:15: **PR-23** 머지(#92) — onboarding.py 4→7슬라이드. SVG inline 시각화 3장 (demo flow / SHAP example / action flow). 비전문가용 자세한 해설.
- 2026-05-22 12:55: **PR-E1R** 머지(#91) — slides.html 16:9 변환 (273×186mm → 320×180mm). 폰트 비례 확대. KPI 카드 + Verdict 박스 신규 (PR-E5 대비).
- 2026-05-22 12:40: **PR-21** 머지(#90) — Mode 진짜 원인=cache 키 source 미명시. data_loader cached 9개 + sidebar_badge/status_banner 모두 source 인자 받도록 변경. Step 3 user_data SSoT 신규.
- 2026-05-22 12:15: **P-F 종합 패키지 plan** 작성 — 사용자 4가지 검증 피드백(Mode 재발/시각화 부족/대시보드/16:9) + 15단계 PM 처방(맥락 단절). 11건 PR (PR-21~26 + E1R + E5 + 선택 3).
- 2026-05-22 11:50: PR-E1+E2+E3 머지(#89) — 발표 산출물 3종
- 2026-05-22 13:15: PR-14+15 묶음(#87) — Western Electric Rules 4종 + Pareto + 센서 히스토그램
- 2026-05-22 11:18: 평가 배점 PT 15분+Q&A 5분, 5항목 100점 (AI 25, MVP 25 최대)

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **PR-22 commit + push + PR + auto merge** (브랜치 `claude/p-f-pr22-viz-advanced`)
2. **PR-26 인앱 UX** — sensor_dictionary.csv + action_rules.py + CTA switch_page + 빈 화면 방어
3. **PR-24 작업 대시보드 A+B** — `pages/6_📋_종합_대시보드.py` 신규 + `docs/presentation/dashboard_summary.html`

## 4. 차단 요소 / 사용자 확인 대기
- 없음. Auto mode 진행 자율 위임.

## 5. 도구 전환 가이드
**Codex 받을 컨텍스트** (3개): `HANDOVER.md` + `SESSION_LOG.md` 최근 5건 + `~/.claude/plans/qualitylens-gentle-panda.md` (P-F 섹션)
**Codex 복귀**: HANDOVER + SESSION_LOG에 1줄 기록.

## 6. P-F 11건 상태판 (사용자 확정 7~8시간)
| PR | 제목 | 상태 |
|---|---|---|
| PR-21 | Mode deep fix (cache source) + 상태 전역화 | ✅ 머지(#90) |
| PR-E1R | 발표 16:9 재작업 | ✅ 머지(#91) |
| PR-23 | Onboarding 7슬라이드 + SVG 3장 | ✅ 머지(#92) |
| **PR-22** | 시각화 풀 확장 (viz_advanced 9함수 + P2/3/4/5 통합) | ✅ 로컬 완료, commit/push 대기 |
| PR-26 | 인앱 UX (데이터 딕셔너리+action_rules+CTA+빈화면) | 🚧 다음 |
| PR-22 | 시각화 풀 확장 (Step 4~7) | ⏳ |
| PR-26 | 인앱 UX (Step 8/9/13/14/15) — 데이터 딕셔너리 + CTA | ⏳ |
| PR-24 | 작업 대시보드 A+B + 비즈니스 임팩트 | ⏳ |
| PR-E5 | 발표 결과 시각화 4장 추가 | ⏳ |
| PR-17/18/9F | 선택 (Cpk/색맹/시나리오) | ⏳ 시간 여유 시 |

---
*갱신 규칙: 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신. 50줄 초과 시 §2 오래된 항목 → SESSION_LOG로 이동.*
