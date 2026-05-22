"""P4 — 조치 가이드 + 원클릭 수용 (S-3).

threshold 위반 센서를 식별하고 권고안 표시 + 수용 버튼으로 조치 이력 자동 기록.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib import action_log  # noqa: E402
from lib.data_loader import sidebar_badge  # noqa: E402
from lib.demo import demo_sidebar, get_source  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_sample,
    load_test_set,
    load_thresholds,
)
from lib.viz_advanced import boxplot_violations, roi_bar  # noqa: E402

st.set_page_config(page_title="P4 — 조치 가이드", page_icon="🛠", layout="wide")
# PR-21: demo_sidebar() 먼저 → session_state → get_source() → sidebar_badge에 명시
demo_mode = demo_sidebar()
source = get_source()
sidebar_badge(source=source)

action_log.init_log()

st.title("🛠 P4 — 조치 가이드")
st.caption(
    "threshold 위반 센서 → 우선순위 + 권고 조치 · "
    "✅ 수용 버튼으로 조치 이력이 P5에 자동 기록"
)

thresholds = load_thresholds(source=source)

if demo_mode:
    samples = load_demo_sample(source=source)
    sample_choice = st.selectbox(
        "데모 샘플",
        options=range(len(samples)),
        format_func=lambda i: f"샘플 #{samples.index[i]}",
    )
    sample = samples.iloc[sample_choice]
    sample_id = samples.index[sample_choice]
else:
    X_test, _ = load_test_set(source=source)
    idx = st.selectbox(
        "샘플 ID",
        options=X_test.index.tolist(),
        format_func=lambda i: f"sample #{i}",
    )
    sample = X_test.loc[idx]
    sample_id = idx


def find_violations(sample_row: pd.Series, table: pd.DataFrame) -> pd.DataFrame:
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

col_m1, col_m2 = st.columns(2)
col_m1.metric("위반 센서 수", len(violations))
col_m2.metric("이번 세션 누적 조치", len(action_log.get_all()))

if len(violations) == 0:
    st.success("✅ 모든 센서가 정상 범위 내. 추가 조치 불필요.")
else:
    for _, row in violations.head(10).iterrows():
        sensor = row["sensor"]
        deviation = float(row["deviation"])
        value = float(row["value"])
        lower = float(row["lower"])
        upper = float(row["upper"])
        direction = "초과" if value > upper else "미달"

        if deviation > 4:
            urgency = "🚨 긴급"
            box = st.error
        elif deviation > 3:
            urgency = "⚠️ 높음"
            box = st.warning
        else:
            urgency = "ℹ️ 중간"
            box = st.info

        recommendation = (
            f"{sensor} 정상 범위 {direction} ({deviation:.2f}σ) — "
            f"해당 공정 단계 점검 및 캘리브레이션 확인 권고"
        )

        with st.container():
            box(
                f"**{urgency} · {sensor}** — 정상 범위 {direction} "
                f"(편차 {deviation:.2f}σ)\n\n"
                f"- 현재값: `{value:.4f}`\n"
                f"- 정상 범위: `{lower:.4f}` ~ `{upper:.4f}`\n"
                f"- 권고: {recommendation}"
            )

            # 원클릭 수용 버튼 (S-3 핵심)
            btn_col, status_col = st.columns([1, 4])
            btn_key = f"accept_{sample_id}_{sensor}"
            already_logged = any(
                e["sample_id"] == str(sample_id) and e["sensor"] == sensor
                for e in action_log.get_all()
            )

            with btn_col:
                if already_logged:
                    st.success("✓ 수용됨")
                else:
                    if st.button("✅ 수용", key=btn_key, use_container_width=True):
                        action_log.append(
                            action_log.make_entry(
                                sample_id=sample_id,
                                sensor=sensor,
                                deviation_sigma=deviation,
                                direction=direction,
                                recommendation=recommendation,
                            )
                        )
                        # PR-8: 극적 피드백 — 발표 시연 임팩트
                        st.toast(f"✅ '{sensor}' 조치가 설비팀에 전달됐습니다!", icon="🚀")
                        st.balloons()
                        st.rerun()
            with status_col:
                if not already_logged:
                    st.caption("수용 시 P5 이력 조회의 '조치 이력' 탭에 자동 기록")

st.divider()

# -----------------------------------------------------------------------------
# PR-22 신규 — 시각화: 위반 센서 분포 + ROI
# -----------------------------------------------------------------------------

st.subheader("📊 위반 센서 시각화 — 편차 분포 + 예상 절감")

tab_box, tab_roi = st.tabs(["📊 편차 분포 (Top 10)", "💰 예상 절감 (ROI)"])

with tab_box:
    if len(violations) > 0:
        st.plotly_chart(
            boxplot_violations(violations, title="위반 센서 σ 편차 (큰 순)"),
            use_container_width=True,
        )
        st.caption(
            "💡 3σ 이상 = 명백한 이상, 4σ 이상 = 긴급. 색상: 🔴 4σ↑ / 🟡 3σ↑ / 🔵 그 외."
        )
    else:
        st.success("✅ 위반 센서 없음 — 박스플롯 생략")

with tab_roi:
    if len(violations) > 0:
        # ROI 추정: 편차 σ × 가중치 (100만원/σ — 보수적 추정)
        top_n = violations.head(6)
        savings = [float(d) * 100 for d in top_n["deviation"]]
        st.plotly_chart(
            roi_bar(
                sensors=top_n["sensor"].tolist(),
                expected_savings_kr=savings,
                title="센서별 예상 절감액 (조치 시) — 편차 σ × 100만원",
            ),
            use_container_width=True,
        )
        st.caption(
            "💡 보수적 추정: 편차 1σ당 평균 100만원 절감 가정. "
            "실제 ROI는 공정/제품에 따라 다를 수 있음."
        )
    else:
        st.info("✅ 위반 센서 없음 — ROI 차트 생략")

st.divider()
st.caption(
    "권고 텍스트는 일반화된 가이드. 실제 운영 시 도메인 전문가 검토 필수 · "
    "관련 스킬 → `skills/xai/action-guide.md`"
)
