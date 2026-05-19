"""P5 — 이력 조회.

데모 모드: demo_result.csv 4건
실데이터 모드: test set 예측 결과 전체
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib.demo import demo_sidebar  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_result,
    load_model,
    load_test_set,
)

st.set_page_config(page_title="P5 — 이력 조회", page_icon="📜", layout="wide")
demo_mode = demo_sidebar()

st.title("📜 P5 — 이력 조회")
st.caption("예측 이력 검색 · 필터 · CSV export")

model = load_model()

if demo_mode or model is None:
    df = load_demo_result()
    df = df.assign(label=df["pred_label"].map({0: "PASS", 1: "FAIL"}))
else:
    X_test, y_test = load_test_set()
    proba = model.predict_proba(X_test)[:, 1]
    df = pd.DataFrame(
        {
            "sample_id": X_test.index,
            "pred_proba": proba,
            "pred_label": (proba >= 0.5).astype(int),
            "actual": y_test.values,
        }
    )
    df = df.assign(label=df["pred_label"].map({0: "PASS", 1: "FAIL"}))

# 필터
col1, col2 = st.columns([2, 1])
with col1:
    label_filter = st.multiselect(
        "결과 필터", options=["PASS", "FAIL"], default=["PASS", "FAIL"]
    )
with col2:
    min_proba = st.slider("최소 이상 확률", 0.0, 1.0, 0.0, 0.05)

filtered = df[df["label"].isin(label_filter) & (df["pred_proba"] >= min_proba)]

st.metric("조회 건수", f"{len(filtered):,}")
st.dataframe(
    filtered.style.format({"pred_proba": "{:.4f}"}),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "📥 필터 결과 CSV 다운로드",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="qualitylens_history.csv",
    mime="text/csv",
)
