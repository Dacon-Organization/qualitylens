"""PR-17 단위 테스트 — Cp/Cpk 공정 능력 지수.

검증 6건:
1. 기본 계산 — 정규분포 데이터 → Cp ≈ 1.0 (USL/LSL = ±3σ)
2. 편향 (mean shift) — Cpk < Cp
3. tier 4단계 분류 (poor / marginal / good / excellent)
4. 사용자 USL/LSL 명시 우선
5. σ = 0 (모든 값 동일) edge case
6. n < 2 edge case
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.lib.cpk import compute_cpk, cpk_tier_label  # noqa: E402


# -----------------------------------------------------------------------------
# Test 1 — 기본 계산
# -----------------------------------------------------------------------------


def test_compute_cpk_normal_distribution():
    """정규분포(mean=0, sigma=1)에 USL/LSL = ±3σ → Cp ≈ 1.0."""
    rng = np.random.default_rng(42)
    values = pd.Series(rng.normal(0.0, 1.0, size=1000))
    result = compute_cpk(values, usl=3.0, lsl=-3.0)
    assert 0.9 <= result.cp <= 1.1, f"Cp should be ~1.0, got {result.cp}"
    assert 0.8 <= result.cpk <= 1.1, f"Cpk should be ~1.0, got {result.cpk}"


# -----------------------------------------------------------------------------
# Test 2 — 편향 (mean shift)
# -----------------------------------------------------------------------------


def test_compute_cpk_biased_mean():
    """평균이 USL 쪽으로 치우치면 Cpk < Cp."""
    rng = np.random.default_rng(42)
    values = pd.Series(rng.normal(loc=2.0, scale=1.0, size=1000))  # mean=2.0
    result = compute_cpk(values, usl=3.0, lsl=-3.0)
    # Cp = 6/6 = 1.0 (편향 무시), Cpk는 (3-2)/3 = 0.33 근처 (편향 반영)
    assert result.cpk < result.cp, "Cpk must be < Cp when mean shifts"
    assert result.cpk < 0.5, f"Cpk should be small with bias, got {result.cpk}"


# -----------------------------------------------------------------------------
# Test 3 — 4단계 tier 분류
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cpk_value,expected_tier",
    [
        (0.5, "poor"),       # < 1.00
        (1.0, "marginal"),   # 1.00 ~ 1.33
        (1.5, "good"),       # 1.33 ~ 1.67
        (2.0, "excellent"),  # ≥ 1.67
    ],
)
def test_tier_classification(cpk_value, expected_tier):
    """Cpk 값 → 4단계 tier 매핑."""
    # USL/LSL을 조작하여 정확한 cpk 값 만들기
    # Cpk = (USL - mu) / (3σ) — mu=0, σ=1, USL=cpk*3 → Cpk = cpk
    values = pd.Series(np.random.default_rng(0).normal(0.0, 1.0, size=1000))
    sigma = float(values.std(ddof=1))
    mu = float(values.mean())
    # Cpk = min(cpu, cpl) → USL=LSL의 거리 동일하게
    usl = mu + cpk_value * 3 * sigma
    lsl = mu - cpk_value * 3 * sigma
    result = compute_cpk(values, usl=usl, lsl=lsl)
    assert result.tier == expected_tier, (
        f"Cpk={result.cpk:.2f}, expected tier={expected_tier}, got {result.tier}"
    )


# -----------------------------------------------------------------------------
# Test 4 — USL/LSL 명시 vs 자동 추정
# -----------------------------------------------------------------------------


def test_user_specified_spec_overrides_auto():
    """사용자 USL/LSL 명시 시 자동 추정 비활성."""
    values = pd.Series(np.linspace(0.0, 10.0, 100))
    result_user = compute_cpk(values, usl=10.0, lsl=0.0)
    result_auto = compute_cpk(values, auto_spec_k=3.0)
    assert result_user.usl == 10.0
    assert result_user.lsl == 0.0
    # 자동 추정은 mean ± 3σ
    assert result_user.usl != result_auto.usl


def test_auto_spec_k_affects_limits():
    """auto_spec_k가 USL/LSL을 조정."""
    values = pd.Series(np.random.default_rng(0).normal(0.0, 1.0, size=500))
    r3 = compute_cpk(values, auto_spec_k=3.0)
    r2 = compute_cpk(values, auto_spec_k=2.0)
    # k=3 → 더 넓은 범위 → 더 큰 Cp
    assert r3.cp > r2.cp


# -----------------------------------------------------------------------------
# Test 5 — Edge: σ = 0
# -----------------------------------------------------------------------------


def test_zero_sigma():
    """모든 값이 동일 → σ=0 → excellent 처리."""
    values = pd.Series([5.0] * 100)
    result = compute_cpk(values)
    assert result.tier == "excellent"
    assert result.sigma == 0.0
    assert result.cpk == 99.0  # 무한대 대용


# -----------------------------------------------------------------------------
# Test 6 — Edge: n < 2
# -----------------------------------------------------------------------------


def test_insufficient_data():
    """샘플 수 < 2 → 부적합 처리, NaN 반환."""
    values = pd.Series([1.0])
    result = compute_cpk(values)
    assert result.tier == "poor"
    assert np.isnan(result.cp)
    assert np.isnan(result.cpk)


def test_empty_series():
    """빈 Series → 부적합."""
    values = pd.Series([], dtype=float)
    result = compute_cpk(values)
    assert result.tier == "poor"


# -----------------------------------------------------------------------------
# Test 7 — cpk_tier_label 간략 한글 라벨
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cpk,expected_label",
    [
        (0.5, "부적합"),
        (1.0, "개선 필요"),
        (1.33, "양호"),
        (1.5, "양호"),
        (1.67, "우수"),
        (2.0, "우수"),
    ],
)
def test_cpk_tier_label_korean(cpk, expected_label):
    assert cpk_tier_label(cpk) == expected_label
