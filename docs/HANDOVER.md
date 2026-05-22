# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 11:50 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
P-B 확장 진행 중 — PR-1/3/2 ✅, **PR-7 mode 버그 fix 진행 중** → 다음 PR-19(CSV 업로드) → PR-20(모달) → PR-8(UI) → PR-10(데이터) → PR-15/14/11 → P-E(발표 산출물 E1/E2/E3).

## 1. 환경
- 워크트리: `C:\Users\kik32\workspace\Dacon\.claude\worktrees\confident-allen-747529\smart-factory-hackathon`
- 브랜치: `claude/confident-allen-747529` (origin/main과 동기, squash merge 후 force-with-lease 패턴)
- Python 3.12.4 · 의존성 OK · 인코딩 `PYTHONIOENCODING=utf-8` 강제 (Windows)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22 11:32: MVP 핵심 갭 — PR-19(CSV 업로드)·PR-20(onboarding 모달) 필수 격상
- 2026-05-22 11:18: 평가 배점 확정 — PT 15분+Q&A 5분, 5항목 100점 (AI 25, MVP 25 최대 비중)
- 2026-05-22 11:05: 대회 정보 재명확 — MVP 4단계, 4영역 통합, 산출물 3종 (PDF+HTML+영상)
- 2026-05-22 10:48: 필수 9→11개 확정, PR-10 A+B 함께 (timestamp + state)
- 2026-05-22 10:35: 실무 시각화 5종 (SPC/Pareto/OEE/Cpk/색맹) 추가 후보

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **PR-7 마무리** — demo.py 패치 완료, commit + push --force-with-lease + PR + squash merge
2. **PR-19 착수** — `app/pages/0_📤_데이터_업로드.py` + `app/lib/upload.py` 신규 (90분, MVP 핵심)
3. **PR-20 착수** — `app/lib/onboarding.py` st.dialog 4슬라이드 모달 (45분)

## 4. 차단 요소 / 사용자 확인 대기
- 없음. Auto mode 진행 자율 위임.

## 5. 도구 전환 가이드

**Claude → Codex** 전환 트리거: Claude 5시간 한도 도달 / 단순 반복 작업.

**Codex가 받아야 할 컨텍스트** (3개면 충분):
1. `docs/HANDOVER.md` (이 파일) — 현황 + 다음 액션
2. `docs/SESSION_LOG.md` 최근 5건 — 결정 이력
3. `C:\Users\kik32\.claude\plans\qualitylens-gentle-panda.md` — P-B 확장 + P-E 발표 산출물 전체 plan (PR-7~20, PR-E1~E4)

**Codex 작업 후 복귀**: HANDOVER + SESSION_LOG에 자신의 작업 1줄 기록.

## 6. 진행 중 sub-PR 상태판 (필수 11개)
| PR | 제목 | 상태 |
|---|---|---|
| PR-1/3/2 | hotfix + 메모리 + 캡처 | ✅ #81/#82/#83 |
| **PR-7** | mode 버그 fix | 🚧 commit 대기 |
| PR-19/20 | CSV 업로드 + onboarding 모달 | ⏳ MVP 핵심 |
| PR-8/10/15/14/11 | UI/데이터/Pareto/SPC/브랜딩 | ⏳ |
| PR-E1/E2/E3 | 발표 PDF + 자유양식 + 시연 가이드 | ⏳ 대회 제출 필수 |

---
*갱신 규칙: 매 sub-PR 머지 후 §0/§2/§3/§6 동시 갱신. 50줄 초과 시 §2 오래된 항목 → SESSION_LOG로 이동.*
