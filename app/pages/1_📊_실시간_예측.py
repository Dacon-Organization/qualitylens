"""P2 — 실시간 예측 + 스트리밍 시뮬레이션 (S-4).

데모 모드:
  - 단일 샘플 모드: 사전 결과 4건 중 선택
  - 스트리밍 모드: 정상 4 → FAIL 2 → 복귀 4 시퀀스 자동 재생

실데이터 모드: test set 샘플 선택 후 model.predict_proba()
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from lib import stream  # noqa: E402
from lib.demo import demo_sidebar  # noqa: E402
from lib.load import (  # noqa: E402
    load_demo_result,
    load_demo_sample,
    load_model,
    load_test_set,
)
from lib.viz import (  # noqa: E402
    DANGER_THRESHOLD,
    WARN_THRESHOLD,
    gauge_proba,
    render_tier_badge,
    risk_tier,
)

st.set_page_config(page_title="P2 — 실시간 예측", page_icon="📊", layout="wide")
demo_mode = demo_sidebar()
stream.init_state()

st.title("📊 P2 — 실시간 예측")
st.caption("센서값 입력 → 이상 확률 즉시 판정 · 스트리밍 시뮬레이션 지원")

model = load_model()


# -----------------------------------------------------------------------------
# 모드 선택 — 단일 샘플 / 스트리밍
# -----------------------------------------------------------------------------

mode = st.radio(
    "재생 모드",
    options=["📌 단일 샘플", "🎬 스트리밍 시뮬레이션"],
    horizontal=True,
    help="스트리밍은 페르소나 시나리오(정상→이상 주입→복귀)를 자동 재생합니다.",
)

# -----------------------------------------------------------------------------
# 단일 샘플 모드
# -----------------------------------------------------------------------------

if mode.startswith("📌"):
    if demo_mode or model is None:
        st.info("💡 데모 모드 — 사전 캐싱된 4건 중 선택해 결과를 확인합니다.")
        demo_sample = load_demo_sample()
        demo_result = load_demo_result()

        if "selected_demo_idx" not in st.session_state:
            st.session_state.selected_demo_idx = 0

        sel = st.selectbox(
            "데모 샘플 선택",
            options=range(len(demo_sample)),
            format_func=lambda i: f"샘플 #{demo_sample.index[i]}",
            key="selected_demo_idx",
        )
        proba = float(demo_result.iloc[sel]["pred_proba"])
        sample_id = str(demo_sample.index[sel])
        scenario_label = "단일 샘플"
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
        sample_id = str(idx)
        scenario_label = "단일 샘플"

# -----------------------------------------------------------------------------
# 스트리밍 모드 (S-4) — 페르소나 시나리오 자동 재생
# -----------------------------------------------------------------------------

else:
    if not (demo_mode or model is None):
        st.warning(
            "스트리밍은 데모 모드에서만 동작합니다. 사이드바에서 '데모 (결정론)' 선택."
        )
        st.stop()

    demo_sample = load_demo_sample()
    demo_result = load_demo_result()

    # 시퀀스가 없으면 빌드
    if not st.session_state.get(stream.STATE_SEQUENCE):
        st.session_state[stream.STATE_SEQUENCE] = stream.build_demo_sequence(
            demo_sample, demo_result
        )

    sequence = st.session_state[stream.STATE_SEQUENCE]
    total = len(sequence)
    current_idx = st.session_state.get(stream.STATE_INDEX, 0)

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 3])
    with ctrl1:
        if st.button("▶ 시작", use_container_width=True, disabled=stream.is_running()):
            stream.start(sequence)
            st.rerun()
    with ctrl2:
        if st.button(
            "⏸ 일시정지", use_container_width=True, disabled=not stream.is_running()
        ):
            stream.pause()
            st.rerun()
    with ctrl3:
        if st.button("🔁 리셋", use_container_width=True):
            stream.reset()
            st.session_state[stream.STATE_SEQUENCE] = []
            st.rerun()
    with ctrl4:
        st.progress(
            (current_idx + 1) / total if total else 0.0,
            text=f"tick {current_idx + 1} / {total}",
        )

    frame = stream.current_frame()
    if frame is None:
        st.info("▶ 시작 버튼을 눌러 페르소나 시나리오(정상→이상→복귀)를 재생하세요.")
        st.stop()

    proba = frame.proba
    sample_id = frame.sample_id
    scenario_label = frame.label

# -----------------------------------------------------------------------------
# 공통 — 컬러 배지 + 게이지 + 결과 카드
# -----------------------------------------------------------------------------

tier = risk_tier(proba)
st.markdown(
    f'<div style="margin: 8px 0 12px 0;">'
    f"{render_tier_badge(proba)}"
    f'<span style="color:#8b949e; font-size:12px; margin-left:14px;">'
    f"샘플 #{sample_id} · 시나리오: <strong>{scenario_label}</strong> · "
    f"임계치: 경고 {WARN_THRESHOLD:.2f} · 위험 {DANGER_THRESHOLD:.2f}"
    f"</span></div>",
    unsafe_allow_html=True,
)

col_a, col_b = st.columns([1, 1])

with col_a:
    st.plotly_chart(
        gauge_proba(proba), use_container_width=True, key=f"gauge_{sample_id}_{scenario_label}"
    )

with col_b:
    if tier.code == "danger":
        st.error(f"### 🚨 위험 — 이상 (FAIL)\n\n이상 확률 **{proba*100:.1f}%**")
        st.markdown("**즉시 조치 필요** — P3 원인 분석 → P4 조치 가이드 순으로 확인")
    elif tier.code == "warn":
        st.warning(f"### ⚠️ 경고 — 이상 가능성\n\n이상 확률 **{proba*100:.1f}%**")
        st.markdown("임계치 초과 가능성. P3 원인 분석으로 어느 센서가 영향 미치는지 점검")
    else:
        st.success(f"### ✅ 정상 (PASS)\n\n이상 확률 **{proba*100:.1f}%**")
        st.markdown("정상 범위 내에서 운영 중입니다.")

# -----------------------------------------------------------------------------
# 스트리밍 재생 루프 — st.rerun 패턴
# -----------------------------------------------------------------------------

if mode.startswith("🎬") and stream.is_running():
    time.sleep(1.0)  # 1초 간격 재생
    if stream.advance():
        st.rerun()
    else:
        st.success("🎬 시뮬레이션 완료 — 리셋으로 다시 재생할 수 있습니다.")

st.divider()
st.caption("다음 단계 → P3 원인 분석에서 어느 센서가 기여했는지 확인")
