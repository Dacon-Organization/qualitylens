"""데모 ↔ 실데이터 토글.

사이드바 라디오로 모드 전환. 데모 모드는 사전 캐싱된 결과만 사용.
"""

from __future__ import annotations

import streamlit as st


def demo_sidebar() -> bool:
    st.sidebar.title("🎬 운영 모드")
    mode = st.sidebar.radio(
        "데이터 소스",
        options=["데모 (결정론)", "실데이터 (UCI SECOM)"],
        index=0,
        help="데모 모드는 사전 캐싱된 샘플로 결정론적 결과를 보장합니다.",
    )
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
    return mode.startswith("데모")
