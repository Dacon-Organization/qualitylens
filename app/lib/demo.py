"""데모 ↔ 실데이터 토글 + session_state SSoT (PR-21 + PR-27 persistent key).

사이드바 라디오로 모드 전환. 데모 모드는 사전 캐싱된 결과만 사용.

세션 상태 (SSoT — 페이지 간 일관성):
    st.session_state["_demo_mode_radio"]     : str  (Streamlit widget — 페이지 이동 시 destroy 가능)
    st.session_state["_demo_mode_persistent"]: str  (PR-27 backup — widget destroy 무관 보존)
    st.session_state["_demo_mode"]           : bool (외부 코드 읽기용 bool 미러)
    st.session_state["_data_source"]         : str  ("dummy"|"real" — 캐시 키 source)

PR-27 추가:
  - Streamlit 멀티페이지에서 widget이 destroy 되면 session_state[widget_key]가 사라지는 동작 회피
  - persistent backup key (_demo_mode_persistent)에 즉시 backup → 다음 페이지에서 widget을 올바른 값으로 재초기화
  - URL query param "mode" 양방향 동기화 (새로고침/직접 진입 시에도 모드 보존)
"""

from __future__ import annotations

import streamlit as st

_OPTIONS = ["데모 (결정론)", "실데이터 (UCI SECOM)"]
_WIDGET_KEY = "_demo_mode_radio"
_PERSISTENT_KEY = "_demo_mode_persistent"


def _sync_from_query_params() -> None:
    """URL ?mode=real|dummy → session_state (페이지 진입/새로고침 시)."""
    try:
        mode = st.query_params.get("mode")
        if mode == "real" and st.session_state.get(_PERSISTENT_KEY) != _OPTIONS[1]:
            st.session_state[_PERSISTENT_KEY] = _OPTIONS[1]
        elif mode == "dummy" and st.session_state.get(_PERSISTENT_KEY) != _OPTIONS[0]:
            st.session_state[_PERSISTENT_KEY] = _OPTIONS[0]
    except Exception:  # noqa: BLE001 — query_params API는 Streamlit 버전마다 불안정
        pass


def _sync_to_query_params(source: str) -> None:
    """session_state → URL ?mode=... (사용자 변경 시)."""
    try:
        if st.query_params.get("mode") != source:
            st.query_params["mode"] = source
    except Exception:  # noqa: BLE001
        pass


def ensure_demo_state() -> tuple[bool, str]:
    """세션 상태 SSoT 초기화 — 모든 페이지 진입 시 자동 호출.

    PR-27: persistent backup key + URL query param 양방향 동기로
    멀티페이지 widget destroy + 새로고침 양쪽에서 모드 보존.
    """
    # 1순위: URL query param (외부 진입)
    _sync_from_query_params()

    # 2순위: persistent backup (이전 페이지에서 backup 한 값)
    if _PERSISTENT_KEY in st.session_state:
        # widget 키가 없거나 다르면 persistent로 복원
        if st.session_state.get(_WIDGET_KEY) != st.session_state[_PERSISTENT_KEY]:
            st.session_state[_WIDGET_KEY] = st.session_state[_PERSISTENT_KEY]
    # 3순위: 기본 데모
    elif _WIDGET_KEY not in st.session_state:
        st.session_state[_WIDGET_KEY] = _OPTIONS[0]
        st.session_state[_PERSISTENT_KEY] = _OPTIONS[0]

    selected = st.session_state[_WIDGET_KEY]
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

    PR-27 fix: persistent backup key + URL query param 양방향 동기 →
    멀티페이지 widget destroy / 새로고침 양쪽에서 모드 보존.
    """
    # 페이지 진입 시 session_state 초기화 (URL → persistent → widget 순)
    ensure_demo_state()

    st.sidebar.title("🎬 운영 모드")

    selected = st.sidebar.radio(
        "데이터 소스",
        options=_OPTIONS,
        key=_WIDGET_KEY,  # Streamlit widget key (페이지 이동 시 destroy 가능)
        help="데모 모드는 사전 캐싱된 샘플로 결정론적 결과를 보장합니다.",
    )

    is_demo = selected.startswith("데모")
    source = "dummy" if is_demo else "real"

    # PR-27: 사용자 선택 → persistent backup + URL query param 즉시 동기
    st.session_state[_PERSISTENT_KEY] = selected
    _sync_to_query_params(source)

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
