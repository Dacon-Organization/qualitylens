"""P5 — 이력 조회 (S-3: 예측 이력 + 조치 이력 두 탭)."""

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
    load_demo_result,
    load_model,
    load_test_set,
)

st.set_page_config(page_title="P5 — 이력 조회", page_icon="📜", layout="wide")
# PR-21: demo_sidebar() 먼저 → session_state → get_source() → sidebar_badge에 명시
demo_mode = demo_sidebar()
source = get_source()
sidebar_badge(source=source)
action_log.init_log()

st.title("📜 P5 — 이력 조회")
st.caption("예측 이력 + P4에서 수용한 조치 이력 한 화면에 · CSV export 지원")

tab_pred, tab_action = st.tabs(["📊 예측 이력", "✅ 조치 이력"])

# -----------------------------------------------------------------------------
# 탭 1 — 예측 이력
# -----------------------------------------------------------------------------

with tab_pred:
    model = load_model(source=source)
    if demo_mode or model is None:
        df = load_demo_result(source=source)
        df = df.assign(label=df["pred_label"].map({0: "PASS", 1: "FAIL"}))
    else:
        X_test, y_test = load_test_set(source=source)
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
        "📥 예측 이력 CSV 다운로드",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="qualitylens_predictions.csv",
        mime="text/csv",
        key="dl_predictions",
    )

# -----------------------------------------------------------------------------
# 탭 2 — 조치 이력 (S-3)
# -----------------------------------------------------------------------------

with tab_action:
    log_df = action_log.as_dataframe()

    col_m, col_btn = st.columns([3, 1])
    col_m.metric("이번 세션 누적 조치", len(log_df))
    with col_btn:
        if len(log_df) > 0 and st.button("🗑 이력 초기화", use_container_width=True):
            action_log.clear()
            st.rerun()

    if len(log_df) == 0:
        st.info(
            "아직 수용된 조치가 없습니다. P4 조치 가이드에서 위반 센서 권고를 "
            "✅ 수용 버튼으로 기록하세요."
        )
    else:
        display = log_df.rename(
            columns={
                "timestamp": "수용 시각",
                "sample_id": "샘플 ID",
                "sensor": "센서",
                "deviation_sigma": "편차(σ)",
                "direction": "방향",
                "recommendation": "권고",
                "accepted_by": "수용자",
            }
        )
        st.dataframe(
            display.style.format({"편차(σ)": "{:.2f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "📥 조치 이력 CSV 다운로드",
            data=display.to_csv(index=False).encode("utf-8-sig"),
            file_name="qualitylens_action_log.csv",
            mime="text/csv",
            key="dl_actions",
        )

        # 반복 원인 Top 5 (페르소나 B 박 팀장 시나리오 선반영)
        st.divider()
        st.subheader("🔁 반복 원인 Top 5")
        st.caption("같은 센서가 여러 번 수용된 경우 — 설비 점검 우선순위")
        repeat = (
            log_df.groupby("sensor")
            .size()
            .reset_index(name="누적 수용 수")
            .sort_values("누적 수용 수", ascending=False)
            .head(5)
            .rename(columns={"sensor": "센서"})
        )
        st.dataframe(repeat, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "조치 이력은 세션 메모리 보관 (Streamlit Cloud ephemeral 환경 호환). "
    "운영 시 DB 연동 권장."
)
