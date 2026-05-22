"""첫 접속 onboarding 모달 — 사용 안내 + 데이터 형식.

st.dialog(Streamlit 1.35+) 기반 4슬라이드 워크스루.
사용자가 한 번 닫으면 세션 내 재표시 안 함 (`_onboarded` session_state).
"""

from __future__ import annotations

import streamlit as st


def _ensure_state() -> None:
    st.session_state.setdefault("_onboarded", False)
    st.session_state.setdefault("_onboarding_step", 0)


@st.dialog("👋 QualityLens — 처음 오셨나요? (1분 안내)", width="large")
def _onboarding_dialog() -> None:
    """4슬라이드 워크스루 (welcome → 데이터 형식 → 4영역 흐름 → 시작)."""
    step = st.session_state.get("_onboarding_step", 0)

    slides = [
        {
            "title": "🏭 QualityLens — 투명한 제조 AI",
            "body": (
                "기존 제조 AI는 *왜 불량인지* 알려주지 않는 블랙박스였습니다.\n\n"
                "QualityLens는 **Quality(품질)** 를 **Lens(렌즈)** 로 들여다보는 "
                "투명 AI 플랫폼입니다.\n\n"
                "- 591개 센서 데이터를 30초 안에 분석\n"
                "- SHAP 기반 설명력 — *어떤 센서가 왜 문제인지* 시각화\n"
                "- 중소 제조 현장 작업자가 첫날부터 사용 가능"
            ),
        },
        {
            "title": "📤 1단계 — 자기 공장 데이터 업로드",
            "body": (
                "왼쪽 사이드바 **`📤 데이터 업로드`** 메뉴에서:\n\n"
                "1. **샘플 CSV 템플릿 다운로드** — 591개 sensor 컬럼 형식 확인\n"
                "2. **자기 공장 CSV 업로드** — `sensor_000` ~ `sensor_590` 컬럼\n"
                "   - 누락된 센서는 자동으로 0 처리 (z-score 평균)\n"
                "   - `sample_id` 컬럼 선택 사항\n"
                "3. **즉시 추론** — 행마다 이상 확률 + 위험 등급 (🟢/🟡/🔴)\n\n"
                "💡 처음에는 **데모 모드** 로 둘러보세요 — 사이드바 라디오에서 전환."
            ),
        },
        {
            "title": "🔄 2단계 — 4영역 통합 흐름",
            "body": (
                "QualityLens는 단순 품질 모듈이 아닌 **통합 플랫폼 MVP** 입니다.\n\n"
                "| 영역 | 페이지 | 핵심 기능 |\n"
                "|---|---|---|\n"
                "| 🛡️ **품질** | 메인 + P1/P2 | 이상 확률 + SHAP 원인 분석 |\n"
                "| 🚨 **안전** | 메인 상단 배너 | 임계값 초과 자동 알림 (3단계) |\n"
                "| ⚙️ **설비** | P2 + SPC 탭 | Western Electric Rules 자동 감지 |\n"
                "| 📈 **생산** | P4 이력 | 누적 이력 + 조치 효과 추적 |"
            ),
        },
        {
            "title": "🎯 3단계 — Predict → Explain → Act 사이클",
            "body": (
                "**P1 실시간 예측** → **P2 원인 분석 (SHAP)** → "
                "**P3 조치 가이드** → **P4 이력**\n\n"
                "현장 작업자가 사고하고 행동하는 표준 절차(SOP)를 그대로 따릅니다.\n\n"
                "**시작하기**:\n"
                "- 📤 데이터 업로드 (자기 공장 CSV) **또는**\n"
                "- 🎬 데모 모드 (사이드바, 결정론적 시연)\n\n"
                "*이 안내는 한 번만 표시됩니다 — 사이드바 `❓ 도움말` 에서 다시 볼 수 있습니다.*"
            ),
        },
    ]

    current = slides[step]
    st.subheader(current["title"])
    st.markdown(current["body"])

    st.progress((step + 1) / len(slides), text=f"{step + 1} / {len(slides)}")

    col_back, col_skip, col_next = st.columns([1, 2, 1])
    if step > 0:
        if col_back.button("◀ 이전", use_container_width=True, key="ob_back"):
            st.session_state["_onboarding_step"] = step - 1
            st.rerun()
    if col_skip.button("나중에 보기 (X)", use_container_width=True, key="ob_skip"):
        st.session_state["_onboarded"] = True
        st.rerun()
    if step < len(slides) - 1:
        if col_next.button("다음 ▶", use_container_width=True, key="ob_next"):
            st.session_state["_onboarding_step"] = step + 1
            st.rerun()
    else:
        if col_next.button("✅ 시작하기", use_container_width=True, key="ob_done"):
            st.session_state["_onboarded"] = True
            st.session_state["_onboarding_step"] = 0
            st.rerun()


def maybe_show_onboarding() -> None:
    """앱 진입 시 호출 — 첫 접속이면 모달 자동 표시."""
    _ensure_state()
    if not st.session_state["_onboarded"]:
        _onboarding_dialog()


def reopen_button_sidebar() -> None:
    """사이드바 도움말 버튼 — 모달 재오픈."""
    if st.sidebar.button("❓ 사용 안내 다시 보기", use_container_width=True):
        st.session_state["_onboarded"] = False
        st.session_state["_onboarding_step"] = 0
        st.rerun()
