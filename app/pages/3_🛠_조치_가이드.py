"""P4 — 조치 가이드.

threshold_table 위반 센서를 식별하고 권고안을 카드로 표시.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib.demo import demo_sidebar  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_sample,
    load_test_set,
    load_thresholds,
)

st.set_page_config(page_title="P4 — 조치 가이드", page_icon="🛠", layout="wide")
demo_mode = demo_sidebar()

st.title("🛠 P4 — 조치 가이드")
st.caption("threshold 위반 센서 → 우선순위 + 권고 조치")

thresholds = load_thresholds()

if demo_mode:
    samples = load_demo_sample()
    sample_choice = st.selectbox(
        "데모 샘플",
        options=range(len(samples)),
        format_func=lambda i: f"샘플 #{samples.index[i]}",
    )
    sample = samples.iloc[sample_choice]
else:
    X_test, _ = load_test_set()
    idx = st.selectbox(
        "샘플 ID",
        options=X_test.index.tolist(),
        format_func=lambda i: f"sample #{i}",
    )
    sample = X_test.loc[idx]


def find_violations(sample_row: pd.Series, table: pd.DataFrame) -> pd.DataFrame:
    """sample 의 각 센서가 정상 범위(lower~upper)를 벗어났는지 식별."""
    common = table["sensor"].isin(sample_row.index)
    table = table[common].copy()
    table["value"] = table["sensor"].map(sample_row.to_dict())
    table["violation"] = (table["value"] < table["lower"]) | (
        table["value"] > table["upper"]
    )
    table["deviation"] = (
        (table["value"] - table["mean_pass"]).abs() / (table["std_pass"] + 1e-9)
    )
    return table[table["violation"]].sort_values("deviation", ascending=False)


violations = find_violations(sample, thresholds)

sort_by = st.radio(
    "우선순위 정렬",
    options=["편차 큰 순", "센서명 순"],
    horizontal=True,
)
if sort_by == "센서명 순":
    violations = violations.sort_values("sensor")

st.metric("위반 센서 수", len(violations))

if len(violations) == 0:
    st.success("✅ 모든 센서가 정상 범위 내. 추가 조치 불필요.")
else:
    for _, row in violations.head(10).iterrows():
        sensor = row["sensor"]
        deviation = row["deviation"]
        value = row["value"]
        lower = row["lower"]
        upper = row["upper"]
        direction = "초과" if value > upper else "미달"

        if deviation > 4:
            box = st.error
            urgency = "🚨 긴급"
        elif deviation > 3:
            box = st.warning
            urgency = "⚠️ 높음"
        else:
            box = st.info
            urgency = "ℹ️ 중간"

        box(
            f"**{urgency} · {sensor}** — 정상 범위 {direction} "
            f"(편차 {deviation:.2f}σ)\n\n"
            f"- 현재값: `{value:.4f}`\n"
            f"- 정상 범위: `{lower:.4f}` ~ `{upper:.4f}`\n"
            f"- 권고: 해당 센서의 공정 단계 점검 및 캘리브레이션 확인"
        )

st.divider()
st.caption(
    "권고 텍스트는 일반화된 가이드. 실제 운영 시 도메인 전문가 검토 필수 · "
    "관련 스킬 → `skills/xai/action-guide.md`"
)
