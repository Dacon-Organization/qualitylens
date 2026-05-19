"""S-4 — 스트리밍 시뮬레이션 헬퍼.

기획서 데모 시나리오: "정상 → 이상 주입 → 복귀"를 P2에서 자동 재생.
Streamlit rerun 패턴 — st.session_state로 상태 보존, time.sleep + st.rerun으로 재생.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import streamlit as st

STATE_INDEX = "stream_idx"
STATE_RUNNING = "stream_running"
STATE_SEQUENCE = "stream_sequence"


@dataclass(frozen=True)
class StreamFrame:
    """한 시점의 프레임."""

    tick: int  # 시뮬레이션 인덱스 (0..N-1)
    sample_id: str  # 실제 샘플 ID (DataFrame index)
    label: str  # "정상 라인" | "이상 주입" | "복귀 중"
    proba: float  # 이상 확률 (사전 결과 또는 모델 호출)


# -----------------------------------------------------------------------------
# 시퀀스 빌더 — 데모 모드용 사전 스크립트
# -----------------------------------------------------------------------------

DEMO_SCRIPT_LABELS = {
    # 페르소나 시나리오 정렬: 정상 4 → 이상 주입 2 → 복귀 4
    0: "정상 라인",
    1: "정상 라인",
    2: "정상 라인",
    3: "정상 라인",
    4: "이상 주입",
    5: "이상 주입",
    6: "복귀 중",
    7: "복귀 중",
    8: "정상 라인",
    9: "정상 라인",
}


def build_demo_sequence(
    demo_sample: pd.DataFrame,
    demo_result: pd.DataFrame,
) -> list[StreamFrame]:
    """데모 4건을 'PASS PASS FAIL FAIL PASS PASS PASS PASS' 식으로 재배열.

    페르소나 시나리오와 일치: 정상 4 → FAIL 2 → 정상 복귀 4 (총 10 tick).
    demo_result에서 label 0(PASS), 1(FAIL) 샘플을 골라 시퀀스 구성.
    """
    pass_ids = demo_result[demo_result["pred_label"] == 0]["sample_id"].tolist()
    fail_ids = demo_result[demo_result["pred_label"] == 1]["sample_id"].tolist()

    # 부족하면 wrap around
    def pick(ids: list, i: int):
        return ids[i % len(ids)] if ids else None

    sequence: list[StreamFrame] = []
    for tick in range(10):
        label = DEMO_SCRIPT_LABELS[tick]
        if label == "이상 주입":
            sid = pick(fail_ids, tick - 4)
        elif label == "복귀 중":
            # 복귀 중은 위험도 중간(경고) — FAIL 샘플을 한 번 더 보여주되 라벨만 다르게
            sid = pick(fail_ids if fail_ids else pass_ids, tick - 6)
        else:
            sid = pick(pass_ids, tick)

        if sid is None or sid not in demo_sample.index:
            # 안전 폴백 — 첫 행
            sid = demo_sample.index[0]

        row = demo_result[demo_result["sample_id"] == sid]
        proba = float(row["pred_proba"].iloc[0]) if len(row) else 0.0
        # 복귀 중에는 proba를 절반으로 — 경고 등급으로 떨어뜨림
        if label == "복귀 중":
            proba = min(proba * 0.6, 0.45)

        sequence.append(
            StreamFrame(tick=tick, sample_id=str(sid), label=label, proba=proba)
        )
    return sequence


# -----------------------------------------------------------------------------
# State 헬퍼
# -----------------------------------------------------------------------------


def init_state() -> None:
    if STATE_INDEX not in st.session_state:
        st.session_state[STATE_INDEX] = 0
    if STATE_RUNNING not in st.session_state:
        st.session_state[STATE_RUNNING] = False
    if STATE_SEQUENCE not in st.session_state:
        st.session_state[STATE_SEQUENCE] = []


def reset() -> None:
    st.session_state[STATE_INDEX] = 0
    st.session_state[STATE_RUNNING] = False


def start(sequence: list[StreamFrame]) -> None:
    st.session_state[STATE_SEQUENCE] = sequence
    st.session_state[STATE_RUNNING] = True


def pause() -> None:
    st.session_state[STATE_RUNNING] = False


def is_running() -> bool:
    return bool(st.session_state.get(STATE_RUNNING, False))


def current_frame() -> StreamFrame | None:
    seq = st.session_state.get(STATE_SEQUENCE, [])
    idx = st.session_state.get(STATE_INDEX, 0)
    if not seq or idx >= len(seq):
        return None
    return seq[idx]


def advance() -> bool:
    """다음 tick으로. 끝까지 갔으면 False 반환 + running 자동 종료."""
    idx = st.session_state.get(STATE_INDEX, 0)
    seq_len = len(st.session_state.get(STATE_SEQUENCE, []))
    next_idx = idx + 1
    if next_idx >= seq_len:
        st.session_state[STATE_RUNNING] = False
        return False
    st.session_state[STATE_INDEX] = next_idx
    return True
