# demo-script — 5분 발표·시연 설계

> **Pipeline Position**: Stage 5 — Present (사전 작업 D-1, 본선 D-Day)
> **Input**: 완성된 Streamlit 앱 + 발표 슬라이드
> **Output**: 5분 발표 스크립트 + 백업 시나리오 2종
> **Recommended model**: `sonnet` (스크립트 작성) → `opus` (시나리오 검증)

---

## 파일 목록

| 파일 | 설명 |
|------|------|
| [five-min-flow.md](five-min-flow.md) | 5분 분당 토픽 + 화면 전환 큐 |
| [backup-scenarios.md](backup-scenarios.md) | 네트워크/모델 실패 대응 2종 |
| [qna-prep.md](qna-prep.md) | 심사위원 예상 질문 5개 + 답변 |

---

## 핵심 원칙

1. **첫 60초가 승부** — 문제 정의·해결 컨셉을 1분 내 전달
2. **시연 = 골든 패스만** — 즉흥 입력 금지, 사전 데모 샘플만 사용
3. **4:30 알람** — 5분 초과는 감점, 4분 30초 알람으로 마무리 신호
4. **백업 PDF** — 모든 시연이 실패해도 슬라이드로 끝까지 발표 가능
5. **질문 5개 외워두기** — Q&A에서 모델·데이터·확장성 질문 필연
