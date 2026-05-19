# streamlit-build — Streamlit 5페이지 구현 표준

> **Pipeline Position**: Stage 4 — Build (사전 작업 D-2 ~ D-1)
> **Input**: 학습 모델(`.joblib`), SHAP 캐시(`.pkl`), 전처리 데이터(`.pkl`)
> **Output**: `app/app.py` + `app/pages/P1~P5.py`
> **Downstream**: 본선장 데모
> **Recommended model**: 골격 `opus` → 디테일 `sonnet`

---

## 파일 목록

| 파일 | 설명 |
|------|------|
| [app-structure.md](app-structure.md) | 앱 진입점, 페이지 라우팅, 공용 상태 |
| [page-specs.md](page-specs.md) | P1~P5 페이지별 위젯·차트 상세 명세 |
| [cache-policy.md](cache-policy.md) | st.cache_data / st.cache_resource 사용 규칙 |
| [demo-toggle.md](demo-toggle.md) | 더미↔실데이터 토글, 데모 모드 동작 |

---

## 핵심 원칙

1. **모든 무거운 로드는 `@st.cache_resource`** — 모델·Explainer
2. **데이터 변환은 `@st.cache_data`** — DataFrame 가공
3. **페이지 간 상태는 `st.session_state` 최소 사용** — Streamlit 멀티페이지는 페이지 전환 시 변수 초기화
4. **데모 모드 토글** — 사이드바에 "데모 / 실데이터" 라디오, 더미 데이터로 결정론적 시연 가능
5. **`streamlit run app/app.py` 한 줄 실행** — 추가 설정 파일 의존성 X
