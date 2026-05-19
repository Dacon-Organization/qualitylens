"""QualityLens — Streamlit 진입점 (P1 통합 대시보드).

실행::

    streamlit run app/app.py
"""

from __future__ import annotations

import streamlit as st

from lib.data_loader import sidebar_badge
from lib.demo import demo_sidebar
from lib.load import (
    load_demo_result,
    load_model,
    load_shap_top20,
    load_test_set,
    load_thresholds,
    status_banner,
)
from lib.viz import proba_timeline, render_tier_badge, risk_tier

st.set_page_config(
    page_title="QualityLens",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

sidebar_badge()
demo_mode = demo_sidebar()

st.title("🏭 QualityLens")
st.caption("AI 기반 스마트 공장 운영 시스템 · Predict → Explain → Act")

status_banner()

# -----------------------------------------------------------------------------
# 데이터
# -----------------------------------------------------------------------------

model = load_model()
X_test, y_test = load_test_set()
thresholds = load_thresholds()
top20 = load_shap_top20()
demo_result = load_demo_result()

if demo_mode or model is None:
    # 데모 모드: 사전 결과만 표시 (모델 호출 X)
    sample_size = len(demo_result)
    fail_count = int(demo_result["pred_label"].sum())
    fail_rate = fail_count / sample_size * 100 if sample_size else 0.0
else:
    # 실데이터 모드 — 사전 직렬화 결과만 사용 (재학습 X)
    proba = model.predict_proba(X_test)[:, 1]
    sample_size = len(X_test)
    fail_count = int((proba >= 0.5).sum())
    fail_rate = fail_count / sample_size * 100

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

col1, col2, col3, col4 = st.columns(4)
col1.metric("총 샘플", f"{sample_size:,}")
col2.metric("이상 판정", f"{fail_count:,}", f"{fail_rate:.1f}%")
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
    if demo_mode or model is None:
        proba_series = demo_result["pred_proba"]
    else:
        import pandas as pd

        proba_series = pd.Series(proba[:100])
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
