# v0 — P-A 작업 누적 캡처 (이관본)

> 시점: 2026-05-19 ~ 2026-05-22 (P-A 본선 직전까지)
> 이관 PR: P-B/PR-2 (루트 디렉토리 정리)
> 트리거: 발표 슬라이드 빌드 (`build_pptx.py`, `build_pptx_v2.py`) + QA 검증

## 폴더 구조

| 폴더 | 내용 | 개수 |
|---|---|---|
| `slides/` | 발표용 슬라이드 PNG/JPG (slide-1 ~ slide-8) | 8 |
| `qa/` | QA 검증 캡처 (qa-slide1 ~ qa-slide8) | 8 |
| `./` | 썸네일 이미지(`thumbnails.jpg`) + 테스트 산출물(`test-slide2.jpg`) | 2 |

## 출처 / 빌드

- 슬라이드 8종: `build_pptx_v2.py` 의 PPTX 빌드 결과를 PNG로 export
- QA 8종: P-A PR-5 Playwright MCP E2E 검증 시 캡처 (참고: `docs/validation/`)
- 썸네일/테스트: PPTX 빌드 중간 산출물 — 정식 자료 아님

## 보존 이유

- 발표 백업: 본선 시 슬라이드 PPTX가 망가질 경우 JPG로 대체 표시 가능
- 회고 자료: P-A 단계별 화면 진화를 v0 → v1 → ... 으로 추적

## 다음 (v1 발행 조건)

- P-B/PR-1 hotfix 머지 후 Streamlit Cloud 재배포 → 메인 페이지 첫 정상 진입 시점에 v1 캡처 (5페이지 × dummy 모드)
