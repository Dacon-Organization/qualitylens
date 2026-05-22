"""P3 — 원인 분석.

사전 계산된 SHAP value 로드만 사용. TreeExplainer 재호출 금지.

S-2: 막대 차트 → plotly Waterfall + Dependence Plot 으로 업그레이드.
기획서 G2 약속 — "글로벌 피처 중요도 + 개별 Waterfall + Dependence Plot 동시 제공".
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib.data_loader import sidebar_badge  # noqa: E402
from lib.demo import demo_sidebar, get_source  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_sample,
    load_shap_per_sample,
    load_shap_top20,
    load_shap_values_test,
    load_shap_waterfall_demo,
    load_test_set,
)
from lib.viz import (  # noqa: E402
    shap_dependence,
    shap_top_bar,
    shap_waterfall,
)
from lib.viz_advanced import correlation_heatmap, violin_normal_anomaly  # noqa: E402

st.set_page_config(page_title="P3 — 원인 분석", page_icon="🔍", layout="wide")
# PR-21: demo_sidebar() 먼저 → session_state → get_source() → sidebar_badge에 명시
demo_mode = demo_sidebar()
source = get_source()
sidebar_badge(source=source)

st.title("🔍 P3 — 원인 분석")
st.caption("어느 센서가 이상 판정에 가장 크게 기여했는지 SHAP으로 설명")

# PR-21: 모든 cached 함수에 source 명시 — 캐시 키 분리
top20 = load_shap_top20(source=source)
demo_sample = load_demo_sample(source=source)
shap_per_sample = load_shap_per_sample(source=source)
waterfall_pkg = load_shap_waterfall_demo(source=source)

# -----------------------------------------------------------------------------
# (1) 전체 평균 — 글로벌 피처 중요도
# -----------------------------------------------------------------------------

st.subheader("📊 전체 평균 — 글로벌 피처 중요도 (Top 15)")
st.plotly_chart(shap_top_bar(top20, n=15), use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# (2) 개별 Waterfall — base → 누적 → 최종
# -----------------------------------------------------------------------------

st.subheader("💧 개별 Waterfall — 샘플별 누적 기여")
st.caption(
    "base_value(평균 logit)에서 시작해 피처별 SHAP가 누적되어 최종 예측 logit으로 도달. "
    "🟥 양수 = 이상 확률 ↑, 🟩 음수 = 정상 확률 ↑"
)

if waterfall_pkg is None or not waterfall_pkg.get("samples"):
    st.warning(
        "Waterfall 사전 패키지가 없습니다. `python scripts/03_shap.py` 재실행 필요. "
        "아래는 사전 결과 없이 표시되는 메시지입니다."
    )
elif demo_mode:
    sample_ids = list(waterfall_pkg["samples"].keys())
    selected_id = st.selectbox(
        "데모 샘플 선택",
        options=sample_ids,
        format_func=lambda i: f"샘플 #{i}",
    )
    pkg = waterfall_pkg["samples"][selected_id]

    # PR-8: SHAP brief — 비전문가용 AI 요약 텍스트 (차트 위에 먼저 표시)
    shap_vals = pkg["shap"]
    feats = pkg["features"]
    top_idx = max(range(len(shap_vals)), key=lambda i: abs(shap_vals[i]))
    top_sensor = feats[top_idx]
    top_value = shap_vals[top_idx]
    total_abs = sum(abs(v) for v in shap_vals) or 1.0
    top_ratio = abs(top_value) / total_abs * 100
    direction = "이상 확률을 높이는" if top_value > 0 else "정상으로 끌어내리는"
    st.error(
        f"🚨 **AI 원인 분석 결과**: 현재 샘플의 예측에서 **'{top_sensor}'** 가 "
        f"가장 큰 {direction} 요인입니다 — **전체 SHAP 영향도의 {top_ratio:.0f}%** 차지."
    )

    fig = shap_waterfall(
        features=pkg["features"],
        shap_values=pkg["shap"],
        base_value=waterfall_pkg["base_value"],
        sample_values=pkg["values"],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"base = {waterfall_pkg['base_value']:+.4f} · "
        f"final logit = {pkg['final_logit']:+.4f}"
    )
else:
    # 실데이터 모드 — shap_per_sample 의 첫 N개에서 선택
    if shap_per_sample is None:
        st.warning("샘플별 SHAP 없음 — 데모 모드로 전환하세요.")
    else:
        sample_idx = st.selectbox(
            "샘플 선택 (test set 데모 4건)",
            options=range(len(shap_per_sample)),
            format_func=lambda i: f"샘플 #{shap_per_sample.index[i]}",
        )
        row = shap_per_sample.iloc[sample_idx]
        top10 = row.abs().sort_values(ascending=False).head(10).index.tolist()
        fig = shap_waterfall(
            features=top10,
            shap_values=[float(row[f]) for f in top10],
            base_value=waterfall_pkg["base_value"] if waterfall_pkg else 0.0,
            sample_values=None,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# (3) Dependence Plot — 단일 센서의 값↔SHAP 관계
# -----------------------------------------------------------------------------

st.subheader("🔬 Dependence Plot — 센서값 ↔ SHAP value")
st.caption(
    "특정 센서의 값이 어떻게 변할 때 모델 출력에 어떻게 기여하는지. "
    "예: 식각 온도가 180°C 이상에서 빨갛게(SHAP 양수) → 이상 확률 급등"
)

X_test, _ = load_test_set(source=source)
shap_values_test = load_shap_values_test(source=source)

if shap_values_test is None:
    st.info(
        "Dependence Plot은 `scripts/03_shap.py` 실행 후 표시됩니다. "
        "현재는 글로벌 Top 1 센서만 더미로 안내."
    )
else:
    top_sensors = top20["sensor"].head(5).tolist()
    selected_sensor = st.selectbox("센서 선택 (상위 5)", options=top_sensors)
    sensor_idx = list(X_test.columns).index(selected_sensor)
    feature_values = X_test[selected_sensor]
    shap_for_sensor = pd.Series(shap_values_test[:, sensor_idx], index=X_test.index)

    highlight_id = None
    if waterfall_pkg and waterfall_pkg.get("samples"):
        ids = list(waterfall_pkg["samples"].keys())
        # 데모 샘플 중 test_set에 있는 것 1개 강조
        for cand in ids:
            if cand in X_test.index:
                highlight_id = cand
                break

    fig = shap_dependence(
        sensor=selected_sensor,
        feature_values=feature_values,
        shap_values_for_sensor=shap_for_sensor,
        highlight_sample_id=highlight_id,
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# (4) PR-22 신규 — 심화 분석: 정상/이상 분포 비교 + 상관 행렬
# -----------------------------------------------------------------------------

st.subheader("🔬 심화 분석 — 정상/이상 분포 + 센서 상관 행렬")
st.caption(
    "비전문가도 직관적으로: \"이 센서가 이상일 때 vs 정상일 때 분포가 어떻게 다른가?\" "
    "+ \"이 센서와 함께 튀는 다른 센서는?\""
)

if shap_values_test is not None and len(top20) >= 5:
    tab_adv1, tab_adv2 = st.tabs(["📊 정상/이상 분포 (Violin)", "🔗 상위 5 센서 상관 행렬"])

    top5_sensors = top20["sensor"].head(5).tolist()

    with tab_adv1:
        try:
            X_t, y_t = load_test_set(source=source)
            sel_sensor = st.selectbox(
                "센서 선택 (상위 5)",
                options=top5_sensors,
                key="violin_sensor_select",
            )
            if sel_sensor in X_t.columns:
                proba_test = shap_values_test.sum(axis=1) if hasattr(shap_values_test, "sum") else None
                # y_test 라벨 기반 분리
                normal_vals = X_t.loc[y_t == 0, sel_sensor]
                anomaly_vals = X_t.loc[y_t == 1, sel_sensor]
                if len(normal_vals) > 0 and len(anomaly_vals) > 0:
                    st.plotly_chart(
                        violin_normal_anomaly(normal_vals, anomaly_vals, sensor_name=sel_sensor),
                        use_container_width=True,
                    )
                else:
                    st.info("정상/이상 샘플 분리 부족 — Violin 생략")
        except FileNotFoundError:
            st.info("실데이터 부재 — Violin 생략. 사이드바에서 실데이터 모드 전환 시 표시됩니다.")

    with tab_adv2:
        try:
            X_t, _ = load_test_set(source=source)
            present = [s for s in top5_sensors if s in X_t.columns]
            if len(present) >= 2:
                st.plotly_chart(
                    correlation_heatmap(X_t[present], title="상위 5 센서 간 상관 행렬"),
                    use_container_width=True,
                )
                st.caption(
                    "💡 절대값 |0.7| 이상은 강한 상관 — 함께 움직이는 센서. "
                    "원인 분석 시 이 그룹을 동시에 점검."
                )
            else:
                st.info("센서 수 부족 — 상관 행렬 생략")
        except FileNotFoundError:
            st.info("실데이터 부재 — 상관 행렬 생략")

st.divider()

# -----------------------------------------------------------------------------
# (5) 백업 이미지
# -----------------------------------------------------------------------------

st.subheader("📷 백업 — 상위 15 센서 정적 이미지")
st.caption("Streamlit 자체 차트가 깨질 경우 폴백 이미지.")
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
