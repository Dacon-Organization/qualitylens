"""P2 — 실시간 예측.

데모 모드: 사전 결과 4건 표시 (모델 호출 X)
실데이터 모드: test set에서 샘플 선택 후 model.predict_proba()
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from lib.demo import demo_sidebar  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_result,
    load_demo_sample,
    load_model,
    load_test_set,
)
from lib.viz import gauge_proba  # noqa: E402

st.set_page_config(page_title="P2 — 실시간 예측", page_icon="📊", layout="wide")
demo_mode = demo_sidebar()

st.title("📊 P2 — 실시간 예측")
st.caption("센서값 입력 → 이상 확률 즉시 판정")

model = load_model()

if demo_mode or model is None:
    st.info("💡 데모 모드 — 사전 캐싱된 4건 중 선택해 결과를 확인합니다.")
    demo_sample = load_demo_sample()
    demo_result = load_demo_result()

    if "selected_demo_idx" not in st.session_state:
        st.session_state.selected_demo_idx = 0

    idx = st.selectbox(
        "데모 샘플 선택",
        options=range(len(demo_sample)),
        format_func=lambda i: f"샘플 #{demo_sample.index[i]}",
        key="selected_demo_idx",
    )
    proba = float(demo_result.iloc[idx]["pred_proba"])
    label = int(demo_result.iloc[idx]["pred_label"])
else:
    st.info("💡 실데이터 모드 — test set 샘플 선택")
    X_test, _ = load_test_set()
    idx = st.selectbox(
        "샘플 ID",
        options=X_test.index.tolist(),
        format_func=lambda i: f"sample #{i}",
    )
    sample = X_test.loc[[idx]]
    proba = float(model.predict_proba(sample)[0, 1])
    label = int(proba >= 0.5)

col_a, col_b = st.columns([1, 1])

with col_a:
    st.plotly_chart(gauge_proba(proba), use_container_width=True)

with col_b:
    if label == 1:
        st.error(f"### 🚨 이상 (FAIL)\n\n이상 확률 **{proba*100:.1f}%**")
        st.markdown("**즉시 조치 필요** — P3 원인 분석 → P4 조치 가이드 순으로 확인")
    else:
        st.success(f"### ✅ 정상 (PASS)\n\n이상 확률 **{proba*100:.1f}%**")
        st.markdown("정상 범위 내에서 운영 중입니다.")

st.divider()
st.caption("다음 단계 → P3 원인 분석에서 어느 센서가 기여했는지 확인")
