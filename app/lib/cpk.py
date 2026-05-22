"""PR-17 — Cp/Cpk 공정 능력 지수 계산.

제조 현장 표준 통계: 공정이 규격(USL/LSL) 안에 얼마나 안정적으로 들어가는지 정량화.

- Cp = (USL - LSL) / (6σ) — 공정의 잠재 능력 (편향 무시)
- Cpk = min[(USL - μ) / (3σ), (μ - LSL) / (3σ)] — 실제 능력 (편향 반영)

해석 (제조 표준 — Automotive AIAG SPC 매뉴얼):
    Cpk < 1.00  → 🔴 부적합 (불량률 ↑)
    1.00 ≤ Cpk < 1.33 → 🟡 개선 필요 (불량률 0.3% 이하 목표)
    1.33 ≤ Cpk < 1.67 → 🟢 양호 (표준)
    Cpk ≥ 1.67 → 🌟 우수 (Six Sigma)

설계 결정:
- numpy만 사용 (scipy 의존 회피 — Streamlit Cloud 패키지 최소화)
- USL/LSL은 mean ± k·σ 자동 추정 가능 (단순화) 또는 사용자 지정
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CpkResult:
    """Cp/Cpk 계산 결과."""

    cp: float          # 잠재 능력
    cpk: float         # 실제 능력 (편향 반영)
    mean: float        # 평균 μ
    sigma: float       # 표준편차 σ
    usl: float         # 상한 규격
    lsl: float         # 하한 규격
    tier: str          # "poor" | "marginal" | "good" | "excellent"
    interpretation: str  # 한글 해석

    @property
    def emoji(self) -> str:
        return {
            "poor": "🔴",
            "marginal": "🟡",
            "good": "🟢",
            "excellent": "🌟",
        }.get(self.tier, "⚪")

    @property
    def color(self) -> str:
        return {
            "poor": "#f85149",
            "marginal": "#d29922",
            "good": "#3fb950",
            "excellent": "#1f6feb",
        }.get(self.tier, "#6e7681")


def _classify(cpk: float) -> tuple[str, str]:
    """Cpk 값 → tier + 한글 해석."""
    if cpk < 1.0:
        return ("poor", "🔴 부적합 — 공정 능력 부족, 즉각 개선 필요")
    if cpk < 1.33:
        return ("marginal", "🟡 개선 필요 — 표준 미달, 모니터링 강화")
    if cpk < 1.67:
        return ("good", "🟢 양호 — 자동차 업계 표준 수준")
    return ("excellent", "🌟 우수 — Six Sigma 수준")


def compute_cpk(
    values: pd.Series | np.ndarray,
    usl: float | None = None,
    lsl: float | None = None,
    auto_spec_k: float = 3.0,
) -> CpkResult:
    """Cp/Cpk 공정 능력 지수 계산.

    Parameters
    ----------
    values : 측정값 시퀀스
    usl : 상한 규격. None이면 mean + k·σ로 자동 추정.
    lsl : 하한 규격. None이면 mean - k·σ로 자동 추정.
    auto_spec_k : USL/LSL 자동 추정 시 사용할 σ 배수 (기본 3.0).

    Returns
    -------
    CpkResult — cp, cpk, 해석 포함
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 2:
        return CpkResult(
            cp=float("nan"), cpk=float("nan"),
            mean=0.0, sigma=0.0,
            usl=0.0, lsl=0.0,
            tier="poor",
            interpretation="데이터 부족 (n < 2)",
        )

    mu = float(arr.mean())
    sigma = float(arr.std(ddof=1))

    # σ가 0이면 (모든 값이 동일) Cp/Cpk 무한대 → 임시로 매우 큰 값 처리
    if sigma <= 1e-9:
        return CpkResult(
            cp=99.0, cpk=99.0,
            mean=mu, sigma=0.0,
            usl=mu, lsl=mu,
            tier="excellent",
            interpretation="🌟 변동 없음 (σ ≈ 0) — 완벽한 안정",
        )

    # USL/LSL 자동 추정 (사용자 미지정 시)
    if usl is None:
        usl = mu + auto_spec_k * sigma
    if lsl is None:
        lsl = mu - auto_spec_k * sigma

    cp = (usl - lsl) / (6 * sigma)
    cpu = (usl - mu) / (3 * sigma)
    cpl = (mu - lsl) / (3 * sigma)
    cpk = min(cpu, cpl)

    tier, interp = _classify(cpk)
    return CpkResult(
        cp=cp, cpk=cpk,
        mean=mu, sigma=sigma,
        usl=usl, lsl=lsl,
        tier=tier,
        interpretation=interp,
    )


def cpk_tier_label(cpk: float) -> str:
    """Cpk → 한글 라벨 (간략)."""
    if cpk < 1.0:
        return "부적합"
    if cpk < 1.33:
        return "개선 필요"
    if cpk < 1.67:
        return "양호"
    return "우수"
