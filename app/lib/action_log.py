"""S-3 — 조치 이력 관리.

session_state 기반 인메모리 로그 (Streamlit Cloud의 ephemeral 환경에서도 동작).
시연 중에는 페이지를 떠나도 같은 세션이면 유지.
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict

import pandas as pd
import streamlit as st


class ActionLogEntry(TypedDict):
    timestamp: str  # KST ISO
    sample_id: str
    sensor: str
    deviation_sigma: float
    direction: str  # "초과" | "미달"
    recommendation: str
    accepted_by: str  # 페르소나명 (데모에선 "김 과장")


SESSION_KEY = "action_log"


def init_log() -> None:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = []


def append(entry: ActionLogEntry) -> None:
    init_log()
    st.session_state[SESSION_KEY].append(entry)


def get_all() -> list[ActionLogEntry]:
    init_log()
    return list(st.session_state[SESSION_KEY])


def as_dataframe() -> pd.DataFrame:
    rows = get_all()
    if not rows:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "sample_id",
                "sensor",
                "deviation_sigma",
                "direction",
                "recommendation",
                "accepted_by",
            ]
        )
    return pd.DataFrame(rows)


def clear() -> None:
    st.session_state[SESSION_KEY] = []


def now_kst() -> str:
    """KST ISO 형식 — 본선이 한국 시간 기준이라 명시."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")


def make_entry(
    sample_id: str | int,
    sensor: str,
    deviation_sigma: float,
    direction: str,
    recommendation: str,
    accepted_by: str = "김 과장",
) -> ActionLogEntry:
    return ActionLogEntry(
        timestamp=now_kst(),
        sample_id=str(sample_id),
        sensor=sensor,
        deviation_sigma=float(deviation_sigma),
        direction=direction,
        recommendation=recommendation,
        accepted_by=accepted_by,
    )
