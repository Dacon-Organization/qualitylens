"""데모 ↔ 실데이터 토글 + session_state SSoT (PR-21).

사이드바 라디오로 모드 전환. 데모 모드는 사전 캐싱된 결과만 사용.

세션 상태 (SSoT — 페이지 간 일관성):
    st.session_state["_demo_mode_radio"] : str  (Streamlit widget 자동 보존)
    st.session_state["_demo_mode"]       : bool (외부 코드 읽기용 bool 미러)
    st.session_state["_data_source"]     : str  ("dummy"|"real" — 캐시 키 source)

PR-21 핵심:
  - 페이지 진입 시 ensure_demo_state() 호출로 session_state 일관성 보장
  - get_source() 헬퍼로 "dummy"|"real" 문자열을 모든 페이지에서 동일하게 도출
  - 모든 load_*(source=source) 호출부와 캐시 키 일치 → mode 전환 시 캐시 무효화

페이지 이동 시에도 사용자가 선택한 모드 + cache key가 모두 보존된다.
"""

from __future__ import annotations

import streamlit as st

_OPTIONS = ["데모 (결정론)", "실데이터 (UCI SECOM)"]


def ensure_demo_state() -> tuple[bool, str]:
    """세션 상태 SSoT 초기화 — 모든 페이지 진입 시 자동 호출 가능.

    호출 후 보장:
      - st.session_state["_demo_mode_radio"] 존재
      - st.session_state["_demo_mode"] : bool
      - st.session_state["_data_source"] : "dummy" | "real"

    반환: (is_demo, source)
    """
    if "_demo_mode_radio" not in st.session_state:
        st.session_state["_demo_mode_radio"] = _OPTIONS[0]

    selected = st.session_state["_demo_mode_radio"]
    is_demo = selected.startswith("데모")
    source = "dummy" if is_demo else "real"

    st.session_state["_demo_mode"] = is_demo
    st.session_state["_data_source"] = source
    return is_demo, source


def get_source() -> str:
    """현재 모드에 해당하는 source 문자열 반환 ("dummy" | "real").

    페이지 코드에서 다음 패턴으로 사용:
        from lib.demo import demo_sidebar, get_source
        demo_mode = demo_sidebar()
        source = get_source()
        df = load_demo_result(source=source)
    """
    if "_data_source" not in st.session_state:
        ensure_demo_state()
    return st.session_state["_data_source"]


def demo_sidebar() -> bool:
    """사이드바 라디오 렌더링 + 모드 반환.

    Streamlit widget `key`로 페이지 간 라디오 상태 자동 보존.
    `_demo_mode_radio`는 widget 직접 관리, `_demo_mode` / `_data_source`는
    외부 모듈이 읽기 편하도록 미러링.
    """
    # 페이지 진입 시 session_state 초기화 (없으면 데모 기본)
    ensure_demo_state()

    st.sidebar.title("🎬 운영 모드")

    selected = st.sidebar.radio(
        "데이터 소스",
        options=_OPTIONS,
        key="_demo_mode_radio",  # Streamlit이 session_state에 자동 보존
        help="데모 모드는 사전 캐싱된 샘플로 결정론적 결과를 보장합니다.",
    )

    is_demo = selected.startswith("데모")
    source = "dummy" if is_demo else "real"

    # 외부 코드(data_loader, pages)에서 읽기 쉬운 미러 키
    st.session_state["_demo_mode"] = is_demo
    st.session_state["_data_source"] = source

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


def has_user_data() -> bool:
    """사용자가 P0에서 업로드한 데이터가 session_state에 있는지 확인 (Step 3)."""
    return "user_data" in st.session_state and st.session_state["user_data"] is not None


def get_user_data():
    """업로드 데이터 반환 (없으면 None). Step 3 — 페이지 간 user_data SSoT."""
    return st.session_state.get("user_data")


def get_user_data_meta() -> dict:
    """업로드 데이터의 메타 정보 (n_samples, n_features, defect_rate 등). 없으면 빈 dict."""
    return st.session_state.get("user_data_meta", {})
