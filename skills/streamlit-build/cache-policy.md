# cache-policy — Streamlit 캐싱 규칙

## 결정 표

| 대상 | 데코레이터 | 이유 |
|---|---|---|
| XGBoost 모델 (`.joblib`) | `@st.cache_resource` | 직렬화 객체, 전 세션 공유 |
| SHAP Explainer (`.pkl`) | `@st.cache_resource` | 동일 |
| 전처리 데이터 (`.pkl`) | `@st.cache_data` | DataFrame, hashable |
| threshold_table.csv | `@st.cache_data` | 작은 테이블 |
| 사용자 입력 변환 | 캐시 없음 | 매번 새로운 입력 |

## 코드 패턴

```python
import streamlit as st
import joblib
import pandas as pd

@st.cache_resource
def load_model():
    return joblib.load("models/xgb_secom.joblib")

@st.cache_resource
def load_explainer():
    return joblib.load("models/shap_explainer.pkl")

@st.cache_data
def load_data(demo_mode: bool = False):
    if demo_mode:
        return pd.read_pickle("data/processed/demo_sample.pkl")
    return pd.read_pickle("data/processed/secom_test.pkl")

@st.cache_data
def load_thresholds():
    return pd.read_csv("models/threshold_table.csv")
```

## 주의

- `@st.cache_resource`는 객체 동일성 보장. 모델 재학습 금지 원칙과 일치.
- 캐시 키에 `demo_mode` 같은 파라미터를 포함시켜 토글 시 자동 무효화.
- `st.session_state`는 페이지 간 상태가 필요할 때만 (예: 분석할 샘플 ID 공유).
