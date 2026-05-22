"""QualityLens — Streamlit 진입점 (P1 통합 대시보드).

실행::

    streamlit run app/app.py
"""

from __future__ import annotations

import streamlit as st

from lib.data_loader import sidebar_badge
from lib.demo import demo_sidebar, get_source, has_user_data, get_user_data
from lib.load import (
    load_demo_result,
    load_model,
    load_shap_top20,
    load_test_set,
    load_thresholds,
    status_banner,
)
from lib.onboarding import maybe_show_onboarding, reopen_button_sidebar
from lib.viz import proba_timeline, render_tier_badge, risk_tier

st.set_page_config(
    page_title="QualityLens",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 첫 접속 시 사용 안내 모달 (PR-20)
maybe_show_onboarding()

# PR-21: demo_sidebar() → session_state SSoT 갱신 → get_source()로 캐시 키 일치
demo_mode = demo_sidebar()
source = get_source()
sidebar_badge(source=source)
reopen_button_sidebar()

st.title("🏭 QualityLens")
st.caption("AI 기반 스마트 공장 운영 시스템 · Predict → Explain → Act")

status_banner(source=source)

# -----------------------------------------------------------------------------
# 데이터 — PR-21: 모든 cached 함수에 source 명시 (캐시 키 분리)
# Step 3 (사용자 PM 처방): user_data가 있으면 우선 사용 (페이지 간 데이터 흐름)
# -----------------------------------------------------------------------------

model = load_model(source=source)
thresholds = load_thresholds(source=source)
top20 = load_shap_top20(source=source)
demo_result = load_demo_result(source=source)


def _demo_metrics() -> tuple[int, int, float]:
    n = len(demo_result)
    failed = int(demo_result["pred_label"].sum())
    rate = failed / n * 100 if n else 0.0
    return n, failed, rate


# Step 3: user_data 우선 흐름 (P0 업로드 → 메인 카드 갱신)
if has_user_data():
    user_df = get_user_data()
    if "pred_proba" in user_df.columns and "pred_label" in user_df.columns:
        sample_size = len(user_df)
        fail_count = int(user_df["pred_label"].sum())
        fail_rate = fail_count / sample_size * 100 if sample_size else 0.0
        proba_series = user_df["pred_proba"]
        st.info(
            f"📤 **업로드 데이터 분석 중** — {sample_size:,}건 · 평균 이상 확률 "
            f"{user_df['pred_proba'].mean():.3f}"
        )
    else:
        sample_size, fail_count, fail_rate = _demo_metrics()
        proba_series = demo_result["pred_proba"]
elif demo_mode or model is None:
    # 데모 모드: 사전 결과만 표시 (모델·테스트셋 로드 X)
    sample_size, fail_count, fail_rate = _demo_metrics()
    proba_series = demo_result["pred_proba"]
else:
    # 실데이터 모드 — test set 로드 실패 시 데모 결과로 자동 폴백 (graceful degradation)
    try:
        X_test, y_test = load_test_set(source=source)
        proba = model.predict_proba(X_test)[:, 1]
        sample_size = len(X_test)
        fail_count = int((proba >= 0.5).sum())
        fail_rate = fail_count / sample_size * 100
        import pandas as pd

        proba_series = pd.Series(proba[:100])
    except FileNotFoundError as exc:
        st.warning(f"⚠️ 테스트셋 부재 — 데모 결과로 폴백: {exc}")
        sample_size, fail_count, fail_rate = _demo_metrics()
        proba_series = demo_result["pred_proba"]

# -----------------------------------------------------------------------------
# 라인 상태 — 3단계 컬러 배지 (S-1)
# -----------------------------------------------------------------------------

line_proba = fail_rate / 100  # 라인 전체 이상 비율을 등급 입력으로
line_tier = risk_tier(line_proba)
st.markdown(
    f'<div style="margin: 8px 0 16px 0;">'
    f'<span style="color: #8b949e; font-size: 13px; margin-right: 12px;">현재 라인 상태</span>'
    f"{render_tier_badge(line_proba)}"
    f"</div>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# KPI 카드
# -----------------------------------------------------------------------------

# PR-8: KPI delta — 평소 대비 증감을 색상으로 즉시 인지 (delta_color inverse: 위 = 빨강)
# baseline은 SECOM 원본의 ~6.6% 불량률 (model_card 참조). 시연 임팩트 위해 명시.
BASELINE_FAIL_RATE = 6.6  # %
delta_pct = fail_rate - BASELINE_FAIL_RATE

col1, col2, col3, col4 = st.columns(4)
col1.metric("총 샘플", f"{sample_size:,}")
col2.metric(
    "이상 판정",
    f"{fail_count:,}",
    f"{delta_pct:+.1f}%p (평소 6.6% 대비)",
    delta_color="inverse",  # 상승 = 빨강 (위험), 하락 = 초록 (개선)
    help="평소(SECOM 원본 6.64%) 대비 이상 비율 증감",
)
col3.metric(
    "운영 threshold",
    "0.50" if model is None else "사전 산출",
    help="Youden's J 기반 — model_card.md 참조",
)
col4.metric("응답 시간", "< 10ms", help="단일 샘플 추론 SLA")

st.divider()

# -----------------------------------------------------------------------------
# 시계열 + 상위 기여 센서
# -----------------------------------------------------------------------------

left, right = st.columns([2, 1])

with left:
    st.subheader("📈 시간대별 이상 확률")
    st.plotly_chart(proba_timeline(proba_series), use_container_width=True)

with right:
    st.subheader("🔥 평균 기여 센서 Top 5")
    st.dataframe(
        top20.head(5).rename(
            columns={"sensor": "센서", "mean_abs_shap": "평균 |SHAP|"}
        ),
        hide_index=True,
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# 알림 배너
# -----------------------------------------------------------------------------

if fail_rate > 10:
    st.warning(f"⚠️ 이상 비율이 {fail_rate:.1f}% 로 평소보다 높습니다. 원인 분석을 권장.")
elif fail_rate > 5:
    st.info(f"이상 비율 {fail_rate:.1f}% — 모니터링 강화 필요")
else:
    st.success(f"이상 비율 {fail_rate:.1f}% — 정상 운영")

st.divider()
st.caption(
    "📋 P2~P5 는 왼쪽 사이드바에서 이동 · "
    "운영 규칙은 `skills/codex-bridge/token-saving.md` 참조"
)
