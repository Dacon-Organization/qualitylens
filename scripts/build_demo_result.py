"""build_demo_result — demo_result_{real,dummy}.csv 재생성.

PR-10: demo 데이터 풍부화 (옵션 A+B 함께)
- timestamp (5분 간격) — 시계열 차트가 의미 가짐
- state (NORMAL/WARNING/ANOMALY) — 3단계 신호등 일관 데이터 소스

설계 원칙:
- 결정성 (RANDOM_STATE=42): Codex로 이관해도 같은 결과
- 60샘플 × 5시간 (5분 간격) — SPC/Pareto 차트가 의미 있도록
- 스토리텔링: 정상 다수 → 점진적 상승 → 위험 피크 → 복귀
- 기존 컬럼(sample_id, pred_proba, pred_label) 보존 — 호출처 무변경

CLI::

    python scripts/build_demo_result.py --source dummy
    python scripts/build_demo_result.py --source real
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

# 한국 표준시
KST = timezone(timedelta(hours=9))
RANDOM_STATE = 42
N_SAMPLES = 60  # 5시간 분량 (5분 간격)
START_KST = datetime(2026, 5, 22, 9, 0, 0, tzinfo=KST)

# 임계값 (state 분류)
THRESH_WARNING = 0.30
THRESH_ANOMALY = 0.50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="demo_result 재생성 (timestamp + state)")
    parser.add_argument(
        "--source",
        choices=["real", "dummy"],
        default="dummy",
        help="real: secom_X_test_real / dummy: secom_X_test_dummy",
    )
    return parser.parse_args()


def classify_state(proba: float) -> str:
    if proba >= THRESH_ANOMALY:
        return "ANOMALY"
    if proba >= THRESH_WARNING:
        return "WARNING"
    return "NORMAL"


def select_storyline_samples(
    X_test: pd.DataFrame, proba: np.ndarray, n: int = N_SAMPLES
) -> np.ndarray:
    """스토리텔링 시계열을 위한 샘플 인덱스 선택.

    구간 ① 정상 ~40% → ② 상승 ~25% → ③ 위험 피크 ~15% → ④ 복귀 ~20%
    각 구간에서 pred_proba 분포에 맞는 샘플 무작위 선택 (결정성 유지).
    """
    rng = np.random.default_rng(RANDOM_STATE)
    proba_series = pd.Series(proba)

    n1 = int(n * 0.40)
    n2 = int(n * 0.25)
    n3 = int(n * 0.15)
    n4 = n - n1 - n2 - n3

    normal = proba_series[proba_series < THRESH_WARNING].index.tolist()
    warn = proba_series[
        (proba_series >= THRESH_WARNING) & (proba_series < THRESH_ANOMALY)
    ].index.tolist()
    anom = proba_series[proba_series >= THRESH_ANOMALY].index.tolist()

    def pick(pool, k):
        if not pool:
            return []
        return rng.choice(pool, size=min(k, len(pool)), replace=len(pool) < k).tolist()

    seq = (
        pick(normal, n1)
        + pick(warn, n2)
        + pick(anom, n3)
        + pick(normal, n4)  # 복귀 = 정상으로 회귀
    )
    return np.array(seq[:n])


def build_demo_result(source: str) -> pd.DataFrame:
    """demo_result DataFrame 생성."""
    model_path = MODEL_DIR / f"xgb_secom_{source}.joblib"
    x_path = PROC_DIR / f"secom_X_test_{source}.pkl"

    if not (model_path.exists() and x_path.exists()):
        raise FileNotFoundError(
            f"필수 산출물 부재 ({source}): {model_path.name} 또는 {x_path.name}. "
            f"scripts/01_preprocess + 02_train 먼저 실행."
        )

    model = joblib.load(model_path)
    X_test = pd.read_pickle(x_path)
    proba_all = model.predict_proba(X_test)[:, 1]

    # 스토리텔링 샘플 인덱스 선택
    selected_idx = select_storyline_samples(X_test, proba_all, n=N_SAMPLES)
    selected_proba = proba_all[selected_idx]
    selected_sample_ids = X_test.index[selected_idx].to_numpy()

    # timestamp (5분 간격, 한국시간)
    timestamps = [
        (START_KST + timedelta(minutes=5 * i)).isoformat()
        for i in range(len(selected_idx))
    ]

    result = pd.DataFrame(
        {
            "sample_id": selected_sample_ids,
            "timestamp": timestamps,
            "pred_proba": selected_proba.round(4),
            "pred_label": (selected_proba >= 0.5).astype(int),
            "state": [classify_state(p) for p in selected_proba],
        }
    )

    return result


def main() -> None:
    args = parse_args()
    out_path = PROC_DIR / f"demo_result_{args.source}.csv"

    df = build_demo_result(args.source)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    counts = df["state"].value_counts().to_dict()
    print(f"[{args.source}] 재생성 완료 → {out_path.name}")
    print(f"  - 총 {len(df)} 샘플, {df['timestamp'].iloc[0]} ~ {df['timestamp'].iloc[-1]}")
    print(
        f"  - 상태 분포: NORMAL={counts.get('NORMAL', 0)} / "
        f"WARNING={counts.get('WARNING', 0)} / ANOMALY={counts.get('ANOMALY', 0)}"
    )
    print(f"  - 평균 이상 확률: {df['pred_proba'].mean():.3f}")


if __name__ == "__main__":
    main()
