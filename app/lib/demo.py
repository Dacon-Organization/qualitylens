"""데모 ↔ 실데이터 토글.

사이드바 라디오로 모드 전환. 데모 모드는 사전 캐싱된 결과만 사용.

세션 상태:
    st.session_state["_demo_mode_radio"] : str  (Streamlit widget 자동 보존)
    st.session_state["_demo_mode"]       : bool (외부 코드 읽기용 별도 키)

페이지 이동 시에도 사용자가 선택한 모드가 보존된다.
"""

from __future__ import annotations

import streamlit as st

_OPTIONS = ["데모 (결정론)", "실데이터 (UCI SECOM)"]


def demo_sidebar() -> bool:
    """사이드바 라디오 렌더링 + 모드 반환.

    Streamlit widget `key`를 사용하여 페이지 간 라디오 선택 상태를 자동 보존한다.
    `_demo_mode_radio` 는 widget이 직접 관리, `_demo_mode` 는 다른 모듈이
    읽기 편하도록 미러링한 bool 키.
    """
    st.sidebar.title("🎬 운영 모드")

    selected = st.sidebar.radio(
        "데이터 소스",
        options=_OPTIONS,
        key="_demo_mode_radio",  # Streamlit이 session_state에 자동 보존
        help="데모 모드는 사전 캐싱된 샘플로 결정론적 결과를 보장합니다.",
    )

    is_demo = selected.startswith("데모")
    # 외부 코드(data_loader, pages)에서 읽기 쉬운 bool 미러
    st.session_state["_demo_mode"] = is_demo

    st.sidebar.caption("발표용 시연은 항상 데모 모드를 권장.")
    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **운영 규칙**
        - 모델 재학습 금지
        - SHAP 재계산 금지
        - 데모 시연 중 모델 호출 금지

        자세히 → `skills/codex-bridge/`
        """
    )
    return is_demo
