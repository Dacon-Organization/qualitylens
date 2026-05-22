# HANDOVER — Claude ↔ Codex 인계 노트

> **마지막 갱신**: 2026-05-22 09:13 KST · **도구**: Claude Opus 4.7
> **이 파일만 읽으면** 다음 액션을 5분 내 식별 가능해야 함. 50줄 한계 유지.

---

## 0. 한 줄 현황
P-B PR-1(Streamlit 배포 hotfix) **완료 / 머지** → PR-3(이 파일) 진행 중 → 다음 PR-2(캡처) → PR-4(대시보드) → PR-6(발표) → PR-5(real 연구).

## 1. 환경
- 워크트리: `C:\Users\kik32\workspace\Dacon\.claude\worktrees\confident-allen-747529\smart-factory-hackathon`
- 브랜치: `claude/confident-allen-747529` (origin/main과 동기)
- Python 3.12.4 · 모든 의존성 OK (xgboost/shap/sklearn/imblearn)
- 인코딩: 스크립트 실행 시 `PYTHONIOENCODING=utf-8` 강제 (Windows cp949 회피)

## 2. 마지막 결정 사항 (최근 5건, 신규 → 과거)
- 2026-05-22: **A+E 조합 채택** — dummy 7종 git 커밋 + graceful degradation (PR #81)
- 2026-05-22: P-B 전체 6 sub-PR 분할 — Hotfix → 메모리 → 캡처 → 대시보드 → 발표 → real연구
- 2026-05-22: 한글 폰트 전수 점검은 **P-C로 분리** (별도 spec)
- 2026-05-22: Codex 라우팅 = 하이브리드 (기본 5.4, 설계·분석만 5.5)
- 2026-05-22: 캡처 위치 = `docs/captures/v{n}/` (PR-2에서 구축)

## 3. 다음 액션 (TOP 3, 우선순위 순)
1. **PR-3 마무리** — 이 HANDOVER + `SESSION_LOG.md` 신규 + commit + push + PR (브랜치 `claude/confident-allen-747529`)
2. **PR-2 착수** — `docs/captures/v0/`(루트 산만 캡처 이관) + `v1/`(현 시점 스크린샷 5종) + `INDEX.md`. 별도 PR.
3. **PR-4 착수** — `docs/dashboard/index.html` (Linear/Notion/Basecamp 정보 구조 벤치마킹), `scripts/06_build_dashboard.py`. 별도 PR.

## 4. 차단 요소 / 사용자 확인 대기
- 없음. 진행 자율 위임.

## 5. 도구 전환 가이드

**Claude → Codex** 전환 트리거:
- Claude 5시간 토큰 한도 도달
- 단순 반복 작업 (HTML 템플릿 채움, 파일 rename, INDEX 갱신)

**Codex가 받아야 할 컨텍스트** (이 3개면 충분):
1. `docs/HANDOVER.md` (이 파일) — 현황 + 다음 액션
2. `docs/SESSION_LOG.md` 최근 5일 — 결정 이력
3. `docs/spec_p_b_streamlit_deploy_hotfix.md` — 전체 P-B 계획
4. (선택) `docs/dashboard/data.json` — 진행도 데이터 (PR-4 머지 후)

**Codex 작업 후 복귀 시**:
- Codex가 이 HANDOVER + SESSION_LOG에 자신의 작업을 기록 (날짜·도구·결정 1줄)
- Claude는 이 파일들만 다시 읽고 이어받음

## 6. 진행 중 sub-PR 상태판
| PR | 제목 | 상태 | 비고 |
|---|---|---|---|
| **PR-1** | Hotfix: dummy + graceful | ✅ 머지 (#81) | 06ccd76 |
| **PR-3** | HANDOVER + SESSION_LOG | 🚧 진행 중 | 이 파일 |
| PR-2 | 캡처 v{n} 인프라 | ⏳ 대기 | 다음 |
| PR-4 | 작업 추적 대시보드 v1 | ⏳ 대기 | |
| PR-6 | 기획서 변경점 + 발표 보강 | ⏳ 대기 | |
| PR-5 | real 배포 연구 | ⏳ 본선 후 | |

---
*갱신 규칙: 매 sub-PR 머지 후 §0, §2, §3, §6를 동시에 업데이트. 50줄 초과 시 §2 가장 오래된 항목 1건을 SESSION_LOG로 이동.*
