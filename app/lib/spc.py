"""SPC (Statistical Process Control) — Western Electric Rules 4종 검출.

PR-14: 제조 현장 표준 관리도 패턴.

Western Electric Rules:
    Rule 1: 1개 점이 3σ 초과
    Rule 2: 연속 3점 중 2점이 2σ 초과 (같은 방향)
    Rule 3: 연속 5점 중 4점이 1σ 초과 (같은 방향)
    Rule 4: 연속 8점이 중심선 한 쪽 (양/음)

참고:
    https://lab-wizard.com/en/resources/knowledge/spc-western-electric-rules
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SPCLimits:
    """관리도 한계선."""

    center: float
    ucl: float  # Upper Control Limit (+3σ)
    lcl: float  # Lower Control Limit (-3σ)
    sigma: float  # 표준편차


def compute_limits(values: pd.Series) -> SPCLimits:
    """평균 ± 3σ 관리한계 계산 (Shewhart 차트 표준)."""
    mu = float(values.mean())
    sigma = float(values.std(ddof=1))
    return SPCLimits(
        center=mu,
        ucl=mu + 3 * sigma,
        lcl=max(0.0, mu - 3 * sigma),  # 확률은 음수 불가
        sigma=sigma,
    )


def detect_western_electric(
    values: pd.Series, limits: SPCLimits
) -> pd.DataFrame:
    """Western Electric Rules 4종 적용 → 위반 점 마킹.

    Returns
    -------
    DataFrame with columns: [rule1, rule2, rule3, rule4, any_violation]
    각 행: bool. 해당 위치 점이 룰을 위반하면 True.
    """
    n = len(values)
    arr = values.to_numpy(dtype=float)
    mu = limits.center
    sigma = limits.sigma

    # 정규화 (z-score)
    z = (arr - mu) / sigma if sigma > 0 else np.zeros_like(arr)

    r1 = np.abs(z) > 3.0  # Rule 1
    r2 = np.zeros(n, dtype=bool)
    r3 = np.zeros(n, dtype=bool)
    r4 = np.zeros(n, dtype=bool)

    # Rule 2: 연속 3점 중 2점이 2σ 초과 (같은 부호)
    for i in range(2, n):
        window = z[i - 2 : i + 1]
        pos = np.sum(window > 2.0)
        neg = np.sum(window < -2.0)
        if pos >= 2 or neg >= 2:
            r2[i] = True

    # Rule 3: 연속 5점 중 4점이 1σ 초과 (같은 부호)
    for i in range(4, n):
        window = z[i - 4 : i + 1]
        pos = np.sum(window > 1.0)
        neg = np.sum(window < -1.0)
        if pos >= 4 or neg >= 4:
            r3[i] = True

    # Rule 4: 연속 8점이 중심선 한 쪽 (양 또는 음)
    for i in range(7, n):
        window = z[i - 7 : i + 1]
        if np.all(window > 0) or np.all(window < 0):
            r4[i] = True

    return pd.DataFrame(
        {
            "rule1": r1,
            "rule2": r2,
            "rule3": r3,
            "rule4": r4,
            "any_violation": r1 | r2 | r3 | r4,
        }
    )


def violation_summary(violations: pd.DataFrame) -> dict[str, int]:
    """룰별 위반 횟수 요약."""
    return {
        "Rule 1 (3σ 초과)": int(violations["rule1"].sum()),
        "Rule 2 (3점 중 2점 2σ)": int(violations["rule2"].sum()),
        "Rule 3 (5점 중 4점 1σ)": int(violations["rule3"].sum()),
        "Rule 4 (연속 8점 한쪽)": int(violations["rule4"].sum()),
    }
