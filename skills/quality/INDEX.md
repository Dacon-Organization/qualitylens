> **Pipeline Position**: Stage 5 — Quality & Delivery
> **Input**: 완성된 MVP 전체 (data-pipeline + modeling + xai + ui)
> **Output**: 검증된 MVP + 발표 자료 + 배포 환경
> **Recommended model**: `sonnet` (testing, deployment) / `opus` (demo-prep, scoring)

## 파일 목록

| 파일 | 역할 |
|------|------|
| `testing.md` | 단위/통합 테스트, 데모 시나리오 검증, 성능 벤치마크 |
| `demo-prep.md` | 5분 데모 스크립트, 페일세이프, Q&A 준비 |
| `deployment.md` | requirements.txt, 환경변수, 캐싱, 배포 체크리스트 |
| `scoring-strategy.md` | 5개 평가항목 전략, 점수 극대화, 리스크 완화 |

## 실행 순서

1. `testing.md` — MVP 완성 후 즉시 검증
2. `deployment.md` — 배포 환경 고정
3. `demo-prep.md` — 데모 리허설 (최소 3회)
4. `scoring-strategy.md` — 발표 전 최종 점검

## 의존성

- **Upstream**: 모든 Stage (data-pipeline, modeling, xai, ui) 완료 후 진입
- **Critical path**: testing → deployment → demo-prep (순서 의존)
