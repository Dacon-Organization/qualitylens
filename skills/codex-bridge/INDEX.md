# codex-bridge — Claude ↔ Codex 환경 브릿지

> **Pipeline Position**: 메타 스킬 — 본선장(Codex 환경) 운영 규칙
> **Input**: 사전 작업으로 만들어진 산출물(`.joblib`, `.pkl`, `.html`)
> **Output**: 토큰 최소 사용 운영 흐름
> **Recommended model (Claude)**: `sonnet` — 규칙 명문화
> **Recommended model (Codex)**: `GPT-5.4` 기본 / 복잡 시 `GPT-5.5`

---

## 파일 목록

| 파일 | 설명 |
|------|------|
| [model-routing.md](model-routing.md) | 작업 복잡도 → 모델 선택 결정 표 |
| [token-saving.md](token-saving.md) | 본선장 토큰 절약 5대 원칙 |
| [prompt-templates.md](prompt-templates.md) | Claude → Codex 1:1 매칭 프롬프트 템플릿 |
| [fallback-playbook.md](fallback-playbook.md) | 환경 문제(네트워크/모델 오류) 폴백 절차 |

---

## 핵심 원칙

1. **모델 재학습·SHAP 재계산 금지** — 사전 직렬화된 결과만 로드
2. **컨텍스트는 채팅이 아닌 HTML 로드맵으로 외부화** — `docs/roadmap.html`의 작업 노트가 정본
3. **단일 파일 단위 호출** — 멀티 파일 동시 수정은 토큰 폭증의 가장 큰 원인
4. **프롬프트 템플릿 재사용** — Claude에서 검증된 템플릿을 Codex에서도 동일하게 사용
5. **데모 시연 중에는 모델 호출 금지** — 시연은 결정론적으로

---

## Claude → Codex 매핑

| Claude 작업 | Codex 폴백 | 트리거 |
|---|---|---|
| Opus 4.7 (설계·해석) | GPT-5.5 | 알고리즘 수정, SHAP 결과 재해석 |
| Sonnet 4.6 (구현) | GPT-5.4 | Streamlit 위젯 수정, 차트 스타일 |
| Haiku 4.5 (탐색) | GPT-5.4 (낮은 reasoning) | 변수명 grep, 포맷 확인 |
