"""센서 ID → 한글 표시명 매핑 (PR-26 Step 8 — 도메인 언어 번역).

사용자 처방: "Feature 59, Feature 102 등 알 수 없는 변수명이 나옵니다.
→ 데이터 딕셔너리를 만들어 Feature 59 → [식각 공정] 챔버 온도 처럼
   작업자가 아는 언어로 매핑해서 화면에 뿌려주세요."

- `data/sensor_dictionary.csv` 로드
- 매핑 없는 센서는 graceful — 원본 ID 반환
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd


_DICT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sensor_dictionary.csv"


@lru_cache(maxsize=1)
def _load_dict() -> dict[str, dict]:
    """sensor_dictionary.csv 로드 (1회만, lru_cache로 메모리)."""
    if not _DICT_PATH.exists():
        return {}
    try:
        df = pd.read_csv(_DICT_PATH)
        return {
            row["feature_id"]: {
                "display_name": row["display_name"],
                "unit": row.get("unit", ""),
                "process": row.get("process", ""),
                "description": row.get("description", ""),
            }
            for _, row in df.iterrows()
        }
    except (pd.errors.EmptyDataError, FileNotFoundError, KeyError):
        return {}


def get_display_name(feature_id: str) -> str:
    """Feature ID → 한글 표시명. 매핑 없으면 원본 ID 반환 (graceful).

    예: 'sensor_003' → '식각 챔버 온도' (매핑 있는 경우)
        'sensor_999' → 'sensor_999' (매핑 없는 경우)
    """
    d = _load_dict()
    if feature_id in d:
        return d[feature_id]["display_name"]
    return feature_id


def get_full_label(feature_id: str) -> str:
    """확장 라벨 — 한글명 + 원본 ID + 단위 (차트 라벨용).

    예: 'sensor_003' → '식각 챔버 온도 (sensor_003, °C)'
    """
    d = _load_dict()
    if feature_id not in d:
        return feature_id
    info = d[feature_id]
    parts = [info["display_name"], f"({feature_id}"]
    if info.get("unit"):
        parts.append(f", {info['unit']}")
    parts.append(")")
    return " ".join(parts)


def get_process(feature_id: str) -> str:
    """센서가 속한 공정 영역 (식각/증착/에칭/공통 등). 없으면 빈 문자열."""
    d = _load_dict()
    return d.get(feature_id, {}).get("process", "")


def get_description(feature_id: str) -> str:
    """센서 설명. 없으면 빈 문자열."""
    d = _load_dict()
    return d.get(feature_id, {}).get("description", "")


def has_mapping(feature_id: str) -> bool:
    """딕셔너리에 매핑이 있는지 확인."""
    return feature_id in _load_dict()


def map_series(series: pd.Series) -> pd.Series:
    """pandas Series (센서 ID들) → 한글명 Series (매핑 없으면 원본 유지)."""
    return series.map(get_display_name)
