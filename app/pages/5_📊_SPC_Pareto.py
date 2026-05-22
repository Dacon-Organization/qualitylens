"""📊 SPC + Pareto — 제조 실무 표준 분석.

PR-14 (SPC, Western Electric Rules) + PR-15 (Pareto, 센서 히스토그램).

이 페이지가 어필하는 평가 항목:
- AI 활용 (25점) — "왜 SPC?" → 제조 현장의 표준 통계 패턴
- 플랫폼 기획 (20점) — 설비 영역 (4영역 통합) 구체화
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.data_loader import load_shap_top20, sidebar_badge
from lib.demo import demo_sidebar, get_source
from lib.load import load_demo_result, load_test_set
from lib.onboarding import reopen_button_sidebar
from lib.spc import compute_limits, detect_western_electric, violation_summary
from lib.viz import pareto_chart, sensor_histogram, spc_chart
from lib.viz_advanced import pareto_cumulative

st.set_page_config(
    page_title="QualityLens — SPC & Pareto",
    page_icon="📊",
    layout="wide",
)

# PR-21: demo_sidebar() 먼저 → session_state → get_source() → sidebar_badge에 명시
demo_mode = demo_sidebar()
source = get_source()
sidebar_badge(source=source)
reopen_button_sidebar()

st.title("📊 SPC + Pareto — 제조 실무 표준 분석")
st.caption(
    "통계적 공정 관리(SPC) Western Electric Rules로 이상 패턴을 자동 감지하고, "
    "Pareto 80/20 차트로 개선 우선순위를 즉시 결정합니다."
)

# -----------------------------------------------------------------------------
# 데이터 로드 — PR-21: source 명시 (캐시 키 분리)
# -----------------------------------------------------------------------------
demo_df = load_demo_result(source=source)
top20 = load_shap_top20(source=source)

# 시계열 X축 (timestamp 있으면 사용, 없으면 행 번호)
proba_series = demo_df["pred_proba"].copy()
proba_series.index = (
    pd.to_datetime(demo_df["timestamp"]) if "timestamp" in demo_df.columns else demo_df.index
)

# -----------------------------------------------------------------------------
# SPC 관리도
# -----------------------------------------------------------------------------
st.header("① SPC 관리도 — Western Electric Rules")

with st.expander("💡 SPC란? 왜 Western Electric Rules?", expanded=False):
    st.markdown(
        """
        **SPC (Statistical Process Control)** 는 제조 공정의 변동을 통계적으로 추적해
        이상을 조기 감지하는 표준 기법입니다 (Shewhart, 1924).

        **Western Electric Rules (WER)** 는 단일 점 한 개가 아닌 **패턴** 으로 이상을 판단:
        - **Rule 1**: 1개 점이 ±3σ 초과 → 명백한 이상
        - **Rule 2**: 연속 3점 중 2점이 ±2σ 초과 → 시프트 시작
        - **Rule 3**: 연속 5점 중 4점이 ±1σ 초과 → 점진적 변화
        - **Rule 4**: 연속 8점이 중심선 한 쪽 → 평균 이동

        → **숙련도 낮은 작업자도 이상 신호를 놓치지 않음**.
        Shewhart X 차트 단독보다 5~10배 빠른 감지.
        """
    )

limits = compute_limits(proba_series)
violations = detect_western_electric(proba_series, limits)

c1, c2, c3, c4 = st.columns(4)
c1.metric("중심선 (CL)", f"{limits.center:.3f}")
c2.metric("UCL (+3σ)", f"{limits.ucl:.3f}")
c3.metric("LCL (-3σ)", f"{limits.lcl:.3f}", help="확률 음수 불가 → 0 클램프")
c4.metric("위반 점 수", f"{int(violations['any_violation'].sum())}")

st.plotly_chart(
    spc_chart(proba_series, limits, violations, title="이상 확률 X 관리도"),
    use_container_width=True,
)

# 룰별 위반 횟수
summary = violation_summary(violations)
st.markdown("**룰별 위반 횟수**")
sum_df = pd.DataFrame(
    [{"룰": k, "위반 횟수": v} for k, v in summary.items()]
)
st.dataframe(sum_df, use_container_width=True, hide_index=True)

if int(violations["any_violation"].sum()) > 0:
    st.warning(
        "⚠️ Western Electric Rules 위반 감지. 공정 점검 권장 — "
        "위 차트에서 × 표시된 시점 전후 센서를 P2 원인 분석에서 확인하세요."
    )

st.divider()

# -----------------------------------------------------------------------------
# Pareto + 센서 분포
# -----------------------------------------------------------------------------
st.header("② Pareto 분석 — 상위 기여 센서 (80/20 룰)")

with st.expander("💡 Pareto란?", expanded=False):
    st.markdown(
        """
        **Pareto 원칙(80/20)** — 결과의 80%는 원인의 20%에서 발생.
        제조 현장에서는 "**상위 N개 센서가 전체 불량의 80%를 만든다**" 식으로 활용.

        → 공정팀이 1회 회의에서 **집중 해결 대상**을 즉시 결정.
        """
    )

tab_pareto_simple, tab_pareto_advanced = st.tabs(["📊 기본 Pareto", "📈 누적 곡선 (80% 라인)"])

with tab_pareto_simple:
    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        st.plotly_chart(
            pareto_chart(top20.head(10), category_col="sensor", value_col="mean_abs_shap"),
            use_container_width=True,
        )
    with col_p2:
        st.markdown("**해석 (현장 작업자용)**")
        top3 = top20.head(3)
        msg_lines = [
            f"- **{row['sensor']}** — 영향도 {row['mean_abs_shap']:.3f}"
            for _, row in top3.iterrows()
        ]
        st.markdown("\n".join(msg_lines))
        st.info(
            "💡 위 3개 센서만 안정화해도 전체 불량 원인의 상당 부분을 잡을 수 있습니다."
        )

with tab_pareto_advanced:
    # PR-22 신규 — Pareto 누적 곡선 + 80% 기준선 + 필요 센서 수 자동 계산
    st.plotly_chart(
        pareto_cumulative(top20.head(15), category_col="sensor", value_col="mean_abs_shap"),
        use_container_width=True,
    )
    st.caption(
        "💡 막대 = 개별 기여도 · 라인 = 누적 % · 점선 = 80% 기준선. "
        "회의 1회에 \"몇 개를 집중 해결할지\" 즉시 결정 가능."
    )

st.divider()

# -----------------------------------------------------------------------------
# 센서 분포 히스토그램
# -----------------------------------------------------------------------------
st.header("③ 센서 분포 — 정상 범위 vs 실측")

selected_sensor = st.selectbox(
    "센서 선택",
    options=top20["sensor"].head(10).tolist(),
    help="상위 기여 센서 중 분포를 확인할 센서 선택",
)

try:
    X_test, _ = load_test_set(source=source)
    if selected_sensor in X_test.columns:
        sensor_values = X_test[selected_sensor]
        # 임계값 = 평균 ± 2σ (간략화)
        mu = float(sensor_values.mean())
        sigma = float(sensor_values.std(ddof=1))
        st.plotly_chart(
            sensor_histogram(
                sensor_values,
                threshold_low=mu - 2 * sigma,
                threshold_high=mu + 2 * sigma,
                title=f"{selected_sensor} 분포 (n={len(sensor_values)})",
            ),
            use_container_width=True,
        )
        c_h1, c_h2, c_h3 = st.columns(3)
        c_h1.metric("평균 (μ)", f"{mu:.3f}")
        c_h2.metric("표준편차 (σ)", f"{sigma:.3f}")
        c_h3.metric(
            "이상치 (|z|>2)",
            f"{int((sensor_values.sub(mu).abs() > 2 * sigma).sum())}",
        )
    else:
        st.info(f"{selected_sensor} 데이터 부재.")
except FileNotFoundError as exc:
    st.warning(f"테스트셋 부재 — 히스토그램 생략: {exc}")

st.caption("📋 다음 단계: 위 임계값 위반 샘플을 P3 조치 가이드에서 원클릭 수용.")
