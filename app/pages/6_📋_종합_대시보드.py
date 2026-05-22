"""📋 종합 대시보드 — 비즈니스 임팩트 + 작업 흐름 + 의사결정 (PR-24).

사용자 처방 Phase 4 핵심:
- Step 10 피드백 루프 (조치 완료 → 정상 시뮬)
- Step 11 이력 의미 부여 (지식 베이스 + AI 재학습)
- Step 12 비즈니스 임팩트 (예방 불량 N건, 절감 W원)

참조 `team_comparison_dashboard_v0.1.html` 패턴:
- KPI 4열 그리드 (큰 숫자 + delta)
- Alert gradient 카드 (진행 중 이상)
- 단계별 해설 numbered list
- Verdict 박스 (정상/주의/위험)
- 비교표 색상 코딩 (이번주 vs 지난주)
"""

from __future__ import annotations

import streamlit as st

from lib import action_log
from lib.dashboard_cards import (
    alert_gradient_card,
    comparison_table,
    kpi_card,
    numbered_step,
    render_kpi_grid,
    verdict_box,
)
from lib.data_loader import sidebar_badge
from lib.demo import demo_sidebar, get_source, has_user_data, get_user_data_meta
from lib.load import load_demo_result
from lib.onboarding import reopen_button_sidebar

st.set_page_config(
    page_title="QualityLens — 종합 대시보드",
    page_icon="📋",
    layout="wide",
)

demo_sidebar()
source = get_source()
sidebar_badge(source=source)
reopen_button_sidebar()
action_log.init_log()

st.title("📋 종합 대시보드")
st.caption(
    "조치 이력 + 비즈니스 임팩트 + 작업 흐름 — 경영진·생산관리자 한눈에 파악."
)

# PR-26 Step 13 — 인앱 도움말
with st.popover("💡 이 대시보드 사용법", use_container_width=False):
    st.markdown(
        "1. **KPI 4열**: 예방 불량 / 절감 비용 / 응답시간 / 활성 작업자 — 한눈에\n"
        "2. **진행 중 이상 알림**: 현재 시점 위험 신호 즉시 인지\n"
        "3. **이번 주 vs 지난 주 비교**: 색상 코딩 — 개선/유지/악화 즉시 파악\n"
        "4. **권장 작업 Top 3**: 이번 시프트 우선 처리\n"
        "5. **Verdict**: 라인 전체 상태 의사결정\n\n"
        "*경영진 정기 회의 + 생산관리자 일일 점검용 — 인쇄해서 회의 자료로 사용 가능.*"
    )

# -----------------------------------------------------------------------------
# 1. KPI 4열 그리드 — Step 12 비즈니스 임팩트
# -----------------------------------------------------------------------------
st.divider()
st.subheader("💼 비즈니스 임팩트 (이번 달 누적)")

# 데모 모드: 시연용 고정 + 사용자 모드: action_log 기반 계산
log_count = len(action_log.get_all())
demo_metrics = {
    "prevented": 42,
    "saved_kr": 4200,
    "response_min": 3.2,
    "active_workers": 8,
}
prevented = demo_metrics["prevented"] + log_count  # 시연 시 누적 표시
saved = demo_metrics["saved_kr"] + log_count * 100  # 1건당 100만원 가정
response_min = demo_metrics["response_min"]
workers = demo_metrics["active_workers"]

render_kpi_grid(
    [
        {
            "label": "예방한 불량 (이번 달)",
            "value": f"{prevented}건",
            "delta": "▲ 지난달 대비 +28%",
            "color": "win",
            "icon": "📊",
        },
        {
            "label": "절감된 예상 비용",
            "value": f"{saved:,}만원",
            "delta": f"▲ +{log_count * 100}만원 (이번 세션)",
            "color": "win",
            "icon": "💰",
        },
        {
            "label": "평균 조치 응답 시간",
            "value": f"{response_min}분",
            "delta": "▼ 지난달 대비 -42%",
            "color": "info",
            "icon": "⏱",
        },
        {
            "label": "활성 작업자 수",
            "value": f"{workers}명",
            "delta": "▲ +2명",
            "color": "accent",
            "icon": "👥",
        },
    ]
)

# -----------------------------------------------------------------------------
# 2. 진행 중 이상 알림 (Alert gradient)
# -----------------------------------------------------------------------------
st.divider()

try:
    demo_df = load_demo_result(source=source)
    high_risk_count = int((demo_df["pred_proba"] >= 0.5).sum())
    if high_risk_count > 0:
        st.markdown(
            alert_gradient_card(
                title=f"🚨 진행 중 이상 {high_risk_count}건 — 즉시 조치 필요",
                message=(
                    f"현재 분석 중인 샘플 {len(demo_df):,}건 중 <b>{high_risk_count}건</b>이 "
                    f"이상 확률 50% 이상. P3 조치 가이드로 이동하여 우선순위 처리 권고."
                ),
                severity="bad",
            ),
            unsafe_allow_html=True,
        )
except FileNotFoundError:
    pass

# -----------------------------------------------------------------------------
# 3. 이번 주 vs 지난 주 비교 (Comparison table 색상 코딩)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📊 이번 주 vs 지난 주 비교")

comparison_data = [
    {"지표": "예방 불량 (건)", "이번 주": "12", "지난 주": "9", "변화": "+33.3%"},
    {"지표": "절감 비용 (만원)", "이번 주": "1,250", "지난 주": "920", "변화": "+35.9%"},
    {"지표": "평균 응답 시간 (분)", "이번 주": "3.0", "지난 주": "4.1", "변화": "-26.8%"},
    {"지표": "오탐 (False Positive)", "이번 주": "2", "지난 주": "5", "변화": "-60.0%"},
    {"지표": "이상 확률 평균", "이번 주": "0.082", "지난 주": "0.095", "변화": "-13.7%"},
]

st.markdown(
    comparison_table(
        rows=comparison_data,
        headers=["지표", "이번 주", "지난 주", "변화"],
    ),
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4. 이번 시프트 권장 작업 Top 3 (Numbered)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📋 이번 시프트 권장 작업 Top 3")

st.markdown(
    numbered_step(
        [
            "<b>sensor_003 (식각 챔버 온도)</b> 점검 — 최근 24시간 위반 5회, "
            "냉각 밸브 5% 개방 권고. 예상 소요 3분.",
            "<b>sensor_146 (진공도)</b> 누설 점검 — 터보 펌프 + O-링 확인. "
            "예상 소요 20분. 미조치 시 다음 시프트 영향 가능.",
            "<b>P5 SPC 차트 점검</b> — Western Electric Rules 위반 패턴 확인. "
            "Rule 4 (연속 8점 한쪽) 위반 감지 시 평균 이동 의심.",
        ]
    ),
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Verdict — 라인 전체 상태
# -----------------------------------------------------------------------------
st.divider()
st.subheader("🎯 의사결정 — 라인 전체 상태")

try:
    demo_df = load_demo_result(source=source)
    fail_rate = (demo_df["pred_label"].sum() / len(demo_df)) * 100 if len(demo_df) else 0
    if fail_rate < 5:
        st.markdown(
            verdict_box("win", f"<b>정상 운영 중</b> — 이상률 {fail_rate:.1f}% (목표 5% 이하 달성)."),
            unsafe_allow_html=True,
        )
    elif fail_rate < 10:
        st.markdown(
            verdict_box(
                "warn",
                f"<b>주의 필요</b> — 이상률 {fail_rate:.1f}% (평소 6.6% 대비 다소 증가). "
                "P5 SPC 패턴 점검 권고.",
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            verdict_box(
                "bad",
                f"<b>위험 — 즉시 대응 필요</b> — 이상률 {fail_rate:.1f}% (평소의 1.5배 이상). "
                "라인 일시 정지 + 전체 점검 권고.",
            ),
            unsafe_allow_html=True,
        )
except FileNotFoundError:
    st.info("demo_result 데이터 부재 — Verdict 생략")

# -----------------------------------------------------------------------------
# 6. Step 11 — 이력의 의미
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📚 이력 데이터의 의미")
st.info(
    "본 이력은 **신규 작업자 교육용 지식 베이스(Knowledge Base)** 로 활용되며, "
    "**차기 AI 모델 재학습(Retraining)** 의 핵심 데이터가 됩니다. "
    "→ 누적될수록 모델 정확도 + 작업자 숙련도 향상."
)

# 사용자 업로드 데이터 메타 표시 (있을 경우)
if has_user_data():
    meta = get_user_data_meta()
    st.success(
        f"📤 **사용자 업로드 데이터 연동 중** — "
        f"{meta.get('n_samples', 0):,}건 · "
        f"불량률 {meta.get('defect_rate', 0)*100:.1f}% · "
        f"🔴 위험 {meta.get('high_risk', 0)}건"
    )

# -----------------------------------------------------------------------------
# 7. CTA — 다른 페이지로 이동
# -----------------------------------------------------------------------------
st.divider()
cta1, cta2, cta3, cta4 = st.columns(4)
with cta1:
    if st.button("📊 P1 실시간 예측", use_container_width=True, key="dash_cta_p1"):
        st.switch_page("pages/1_📊_실시간_예측.py")
with cta2:
    if st.button("🔍 P2 원인 분석", use_container_width=True, key="dash_cta_p2"):
        st.switch_page("pages/2_🔍_원인_분석.py")
with cta3:
    if st.button("🛠 P3 조치 가이드", use_container_width=True, key="dash_cta_p3"):
        st.switch_page("pages/3_🛠_조치_가이드.py")
with cta4:
    if st.button("📊 P5 SPC/Pareto", use_container_width=True, key="dash_cta_p5"):
        st.switch_page("pages/5_📊_SPC_Pareto.py")

st.caption(
    "*KPI 값은 시연용 — 실제 운영 시 action_log + DB 연동으로 자동 산출. "
    "본 대시보드는 경영진 회의 + 일일 점검 + 시프트 인계 자료로 활용.*"
)
