# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 13:15 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
P-B + P-E 완성 단계 — PR-1/3/2/7/19+20/10/14+15/8+11 ✅ (10/11), **PR-E1+E2+E3 (발표 산출물 3종) commit 대기** → 본선 발표 준비 완료.

## 1. 환경
- 워크트리: `C:\Users\kik32\workspace\Dacon\.claude\worktrees\confident-allen-747529\smart-factory-hackathon`
- 브랜치: `claude/confident-allen-747529` (force-with-lease 패턴, conflict 시 `git checkout --theirs HANDOVER/SESSION_LOG`)
- Python 3.12.4 · 인코딩 `PYTHONIOENCODING=utf-8` 강제 (Windows)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22 13:15: PR-14+15 묶음 — Western Electric Rules 4종 + Pareto 80/20 + 센서 히스토그램. 새 페이지 5_📊_SPC_Pareto.py
- 2026-05-22 12:50: PR-10 머지(#86) — demo_result 51샘플 timestamp+state (NORMAL 36/WARN 6/ANOMALY 9)
- 2026-05-22 12:35: PR-19+20 머지(#85) — CSV 업로드(591컬럼 자동 정렬) + onboarding 모달 4슬라이드
- 2026-05-22 11:50: PR-7 머지(#84) — mode 버그 fix (widget key 패턴)
- 2026-05-22 11:18: 평가 배점 — PT 15분+Q&A 5분, 5항목 100점 (AI 25, MVP 25 최대)

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **PR-E1+E2+E3 마무리** — commit + push + PR + squash merge
2. **사용자 직접 실행** — `slides.html`을 브라우저에서 열고 Ctrl+P → PDF 인쇄(A4 가로) → 대회 제출
3. **사용자 직접 실행** — `demo_video_guide.md` 시나리오대로 OBS 녹화 → YouTube Unlisted 업로드 → URL 확보

## 4. 차단 요소 / 사용자 확인 대기
- 없음. Auto mode 진행 자율 위임.

## 5. 도구 전환 가이드
**Codex 받을 컨텍스트** (3개): `HANDOVER.md` + `SESSION_LOG.md` 최근 5건 + `~/.claude/plans/qualitylens-gentle-panda.md`
**Codex 복귀**: HANDOVER + SESSION_LOG에 1줄 기록.

## 6. 진행 중 sub-PR 상태판 (필수 11개)
| PR | 제목 | 상태 |
|---|---|---|
| PR-1~PR-8+11 (10건) | 모든 코드 + 브랜딩 완료 | ✅ #81~88 |
| **PR-E1+E2+E3** | 발표 PDF HTML + 자유양식 HTML + 시연 가이드 | 🚧 commit 대기 — 마지막 |
| 사용자 작업 | slides.html → PDF 인쇄 / 시연 영상 녹화·업로드 | ⏳ |
| PR-E1/E2/E3 | 발표 PDF + 자유양식 + 시연 가이드 | ⏳ 대회 제출 필수 |

---
*갱신 규칙: 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신. 50줄 초과 시 §2 오래된 항목 → SESSION_LOG로 이동.*
