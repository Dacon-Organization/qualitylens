"""데모 ↔ 실데이터 토글 + 시나리오 토글 + session_state SSoT.

(PR-21 + PR-27 persistent key + PR-9F 시나리오 토글)

사이드바 라디오로 모드 전환. 데모 모드는 사전 캐싱된 결과만 사용.

세션 상태 (SSoT — 페이지 간 일관성):
    st.session_state["_demo_mode_radio"]     : str  (Streamlit widget — 페이지 이동 시 destroy 가능)
    st.session_state["_demo_mode_persistent"]: str  (PR-27 backup — widget destroy 무관 보존)
    st.session_state["_demo_mode"]           : bool (외부 코드 읽기용 bool 미러)
    st.session_state["_data_source"]         : str  ("dummy"|"real" — 캐시 키 source)
    st.session_state["_scenario"]            : str  (PR-9F: "NORMAL"|"WARN"|"ANOMALY" — 옵셔널)

PR-27 추가:
  - Streamlit 멀티페이지에서 widget이 destroy 되면 session_state[widget_key]가 사라지는 동작 회피
  - persistent backup key (_demo_mode_persistent)에 즉시 backup → 다음 페이지에서 widget을 올바른 값으로 재초기화
  - URL query param "mode" 양방향 동기화 (새로고침/직접 진입 시에도 모드 보존)

PR-9F 추가:
  - 시나리오 토글 세션 키 (_scenario) — 페이지에서 옵셔널 읽기
  - 사이드바 라디오 (NORMAL/WARN/ANOMALY) — 데모 시연 시 자동 샘플 선택 가이드
  - 호출처 변경 0건 (demo_sidebar() bool 반환 유지)
"""

from __future__ import annotations

import streamlit as st

_OPTIONS = ["데모 (결정론)", "실데이터 (UCI SECOM)"]
_WIDGET_KEY = "_demo_mode_radio"
_PERSISTENT_KEY = "_demo_mode_persistent"

# PR-9F — 시나리오 토글
SCENARIOS = ["NORMAL", "WARN", "ANOMALY"]
SCENARIO_LABELS = {
    "NORMAL": "🟢 정상 시퀀스",
    "WARN": "🟡 경고 발생",
    "ANOMALY": "🔴 이상 명백",
}
SCENARIO_DESCRIPTIONS = {
    "NORMAL": "정상 운영 시뮬레이션 — proba < 0.30 샘플 우선",
    "WARN": "경고 신호 단계 — 0.30 ≤ proba < 0.50 샘플 우선",
    "ANOMALY": "명백한 이상 — proba ≥ 0.50 샘플 우선",
}
_SCENARIO_KEY = "_scenario"
_SCENARIO_WIDGET_KEY = "_scenario_radio"


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

    # PR-9F — 시나리오 토글 (옵셔널: 호출처 무변경, session_state로만 노출)
    _render_scenario_toggle()

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


def _render_scenario_toggle() -> None:
    """PR-9F — 사이드바에 시나리오 토글 라디오 추가 (옵셔널).

    페이지 코드는 옵셔널 읽기: `get_scenario()` → "NORMAL" 폴백.
    호출처 5곳 (app/pages/1~5) 시그니처 무변경.
    """
    if _SCENARIO_WIDGET_KEY not in st.session_state:
        st.session_state[_SCENARIO_WIDGET_KEY] = SCENARIOS[0]

    st.sidebar.divider()
    st.sidebar.markdown("**🎭 시연 시나리오** *(데모 모드)*")
    selected = st.sidebar.radio(
        "발표 시 강조할 상황",
        options=SCENARIOS,
        key=_SCENARIO_WIDGET_KEY,
        format_func=lambda s: SCENARIO_LABELS[s],
        help=(
            "데모 시연 시 자동 추천 샘플을 시나리오에 맞게 필터링합니다.\n\n"
            + "\n".join(f"• {SCENARIO_LABELS[s]}: {SCENARIO_DESCRIPTIONS[s]}" for s in SCENARIOS)
        ),
    )
    st.session_state[_SCENARIO_KEY] = selected
    st.sidebar.caption(SCENARIO_DESCRIPTIONS[selected])


def get_scenario() -> str:
    """현재 시나리오 반환 ("NORMAL" | "WARN" | "ANOMALY"). 미설정 시 "NORMAL"."""
    return st.session_state.get(_SCENARIO_KEY, "NORMAL")


def set_scenario(scenario: str) -> None:
    """프로그래밍 방식 시나리오 설정 (테스트용 또는 외부 트리거)."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Invalid scenario: {scenario}. Must be one of {SCENARIOS}")
    st.session_state[_SCENARIO_KEY] = scenario


def filter_samples_by_scenario(
    demo_result,
    scenario: str | None = None,
    warn_threshold: float = 0.30,
    danger_threshold: float = 0.50,
):
    """시나리오에 맞는 샘플 인덱스 필터링.

    Parameters
    ----------
    demo_result : pd.DataFrame  (pred_proba 컬럼 필수)
    scenario : str | None — None이면 get_scenario() 호출
    warn_threshold / danger_threshold : 임계값

    Returns
    -------
    list[int] — 시나리오에 해당하는 demo_result 행 인덱스. 빈 리스트면 전체 폴백.
    """
    if scenario is None:
        scenario = get_scenario()
    if "pred_proba" not in demo_result.columns:
        return list(range(len(demo_result)))

    proba = demo_result["pred_proba"]
    if scenario == "NORMAL":
        mask = proba < warn_threshold
    elif scenario == "WARN":
        mask = (proba >= warn_threshold) & (proba < danger_threshold)
    elif scenario == "ANOMALY":
        mask = proba >= danger_threshold
    else:
        return list(range(len(demo_result)))

    indices = [i for i, v in enumerate(mask.values) if v]
    return indices if indices else list(range(len(demo_result)))


def has_user_data() -> bool:
    """사용자가 P0에서 업로드한 데이터가 session_state에 있는지 확인 (Step 3)."""
    return "user_data" in st.session_state and st.session_state["user_data"] is not None


def get_user_data():
    """업로드 데이터 반환 (없으면 None). Step 3 — 페이지 간 user_data SSoT."""
    return st.session_state.get("user_data")


def get_user_data_meta() -> dict:
    """업로드 데이터의 메타 정보 (n_samples, n_features, defect_rate 등). 없으면 빈 dict."""
    return st.session_state.get("user_data_meta", {})
