# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 12:30 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
P-B 확장 진행 중 — PR-1/3/2/7 ✅, **PR-19+20(CSV 업로드 + onboarding) commit 대기** → 다음 PR-8(UI) → PR-10(데이터) → PR-15/14/11 → P-E(발표 산출물).

## 1. 환경
- 워크트리: `C:\Users\kik32\workspace\Dacon\.claude\worktrees\confident-allen-747529\smart-factory-hackathon`
- 브랜치: `claude/confident-allen-747529` (origin/main 동기, squash merge 후 force-with-lease)
- Python 3.12.4 · 의존성 OK · 인코딩 `PYTHONIOENCODING=utf-8` 강제 (Windows)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22 12:30: PR-19+20 묶음 commit (의존성 + 시간 효율). 단위 검증 PASS (591 컬럼 + 검증 리포트)
- 2026-05-22 11:50: PR-7 mode 버그 fix 머지 (#84) — widget key 패턴, 호출처 무변경
- 2026-05-22 11:32: MVP 핵심 갭 — PR-19(CSV 업로드)·PR-20(onboarding 모달) 필수 격상
- 2026-05-22 11:18: 평가 배점 — PT 15분+Q&A 5분, 5항목 100점 (AI 25, MVP 25 최대)
- 2026-05-22 11:05: 대회 정보 — MVP 4단계, 4영역 통합, 산출물 3종 (PDF+HTML+영상)

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **PR-19+20 마무리** — commit + push + PR + squash merge (충돌 시 git checkout --theirs HANDOVER/SESSION_LOG)
2. **PR-8 착수** — `app/app.py:94-102` KPI delta + `pages/2:65` SHAP brief + `pages/3:142` toast/balloons (45분)
3. **PR-10 착수** — `scripts/build_demo_result.py` 신규, timestamp+state 컬럼 (120분, SPC/Pareto 전제)

## 4. 차단 요소 / 사용자 확인 대기
- 없음. Auto mode 진행 자율 위임.

## 5. 도구 전환 가이드
**Claude → Codex** 트리거: 5시간 한도 / 단순 반복.
**Codex 받을 컨텍스트** (3개): `HANDOVER.md` + `SESSION_LOG.md` 최근 5건 + `~/.claude/plans/qualitylens-gentle-panda.md`.
**Codex 복귀**: HANDOVER + SESSION_LOG에 1줄 기록.

## 6. 진행 중 sub-PR 상태판 (필수 11개)
| PR | 제목 | 상태 |
|---|---|---|
| PR-1/3/2/7 | hotfix + 메모리 + 캡처 + mode 버그 | ✅ #81/#82/#83/#84 |
| **PR-19+20** | CSV 업로드 + onboarding 모달 | 🚧 commit 대기 |
| PR-8/10/15/14/11 | UI/데이터/Pareto/SPC/브랜딩 | ⏳ |
| PR-E1/E2/E3 | 발표 PDF + 자유양식 + 시연 가이드 | ⏳ 대회 제출 필수 |

---
*갱신 규칙: 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신. 50줄 초과 시 §2 오래된 항목 → SESSION_LOG로 이동.*
