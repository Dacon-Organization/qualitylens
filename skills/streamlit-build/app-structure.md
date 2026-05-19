# app-structure — 앱 진입점·라우팅

## 디렉터리

```
app/
├── app.py                 # 진입점 (Home / P1 통합 대시보드)
├── pages/
│   ├── 1_📊_실시간_예측.py    # P2
│   ├── 2_🔍_원인_분석.py      # P3
│   ├── 3_🛠_조치_가이드.py    # P4
│   └── 4_📜_이력_조회.py      # P5
├── lib/
│   ├── load.py            # 모델·데이터 로드 헬퍼 (cache_resource)
│   ├── viz.py             # 공용 차트 함수
│   └── demo.py            # 데모 토글 + 더미 데이터
└── assets/
    └── logo.png
```

## app.py 골격

```python
import streamlit as st
from lib.load import load_model, load_data
from lib.demo import demo_sidebar

st.set_page_config(
    page_title="QualityLens",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사이드바 — 데모 모드 토글
demo_mode = demo_sidebar()

# 메인 화면 — P1 통합 대시보드
st.title("🏭 QualityLens — Predict → Explain → Act")
st.caption("AI 기반 스마트 공장 운영 시스템")

# 모델·데이터 로드 (캐싱)
model = load_model()
df = load_data(demo_mode=demo_mode)

# KPI 카드
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 샘플", len(df))
col2.metric("이상 비율", f"{df['pred'].mean()*100:.1f}%")
col3.metric("MCC", "0.41")
col4.metric("응답 시간", "< 10ms")

# 시계열 차트 + 최근 이상 이력
# ... (page-specs.md 참조)
```

## 페이지 네비게이션 규칙

- Streamlit 멀티페이지(`pages/` 디렉터리) 사용 — `st.navigation` 불필요
- 파일명 접두 숫자로 정렬 (`1_`, `2_`, ...)
- 이모지로 시각적 구분
