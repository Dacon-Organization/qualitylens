"""P3 — 원인 분석.

사전 계산된 SHAP value 로드만 사용. TreeExplainer 재호출 금지.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402

from lib.demo import demo_sidebar  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_sample,
    load_shap_per_sample,
    load_shap_top20,
)
from lib.viz import shap_top_bar  # noqa: E402

st.set_page_config(page_title="P3 — 원인 분석", page_icon="🔍", layout="wide")
demo_mode = demo_sidebar()

st.title("🔍 P3 — 원인 분석")
st.caption("어느 센서가 이상 판정에 가장 크게 기여했는지 SHAP으로 설명")

top20 = load_shap_top20()
demo_sample = load_demo_sample()
shap_per_sample = load_shap_per_sample()

# 전체 평균 기여도
left, right = st.columns([1, 1])

with left:
    st.subheader("전체 평균 — 상위 15 센서")
    st.plotly_chart(shap_top_bar(top20, n=15), use_container_width=True)

with right:
    st.subheader("샘플별 분석")
    if shap_per_sample is None or len(shap_per_sample) == 0:
        st.warning(
            "샘플별 SHAP이 없습니다. `scripts/03_shap.py` 실행 필요. "
            "지금은 전체 평균만 표시됩니다."
        )
    else:
        sample_idx = st.selectbox(
            "데모 샘플 선택",
            options=range(len(shap_per_sample)),
            format_func=lambda i: f"샘플 #{shap_per_sample.index[i]}",
        )
        row = shap_per_sample.iloc[sample_idx]
        # 절댓값 기준 상위 10 추출, 부호는 유지
        top_sample = (
            row.abs()
            .sort_values(ascending=False)
            .head(10)
            .index.tolist()
        )
        sample_df = pd.DataFrame(
            {
                "sensor": top_sample,
                "shap_value": [float(row[s]) for s in top_sample],
            }
        ).iloc[::-1]
        fig = px.bar(
            sample_df,
            x="shap_value",
            y="sensor",
            orientation="h",
            color="shap_value",
            color_continuous_scale=["#7ee787", "#1f2630", "#ff7b72"],
            color_continuous_midpoint=0,
            title="샘플 SHAP — 상위 10 센서",
        )
        fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "🟥 양수 → 이상 확률 ↑ · 🟩 음수 → 정상 확률 ↑"
        )

st.divider()
st.subheader("📷 백업 — 상위 15 센서 (이미지)")
backup_img = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "processed"
    / "shap_demo.png"
)
if backup_img.exists():
    st.image(str(backup_img), use_column_width=True)
else:
    st.caption("백업 이미지 없음 — `scripts/03_shap.py` 실행 필요")
