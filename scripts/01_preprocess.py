"""T1 — 데이터 파이프라인.

UCI SECOM 원본을 로드해 결측치/스케일링/분산-상관 필터링/SMOTE/Stratified Split을
거쳐 X_train, X_test, y_train, y_test를 ``.pkl`` 로 저장한다.

원본이 없으면 더미 데이터를 생성해 파이프라인이 끝까지 동작하도록 폴백한다.

Jupyter/VS Code 셀(`# %%`) 단위 실행 가능. CLI에서는::

    python scripts/01_preprocess.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 경로 — 스크립트 위치를 기준으로 프로젝트 루트 추정
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.2

# %% [markdown]
# ## 1. 원본 로드 (없으면 더미)


def load_secom() -> tuple[pd.DataFrame, pd.Series, bool]:
    """SECOM 원본을 로드. 없으면 더미 데이터 반환."""
    data_path = RAW_DIR / "secom.data"
    labels_path = RAW_DIR / "secom_labels.data"

    if data_path.exists() and labels_path.exists():
        X = pd.read_csv(data_path, sep=r"\s+", header=None)
        labels = pd.read_csv(labels_path, sep=r"\s+", header=None)
        # 첫 컬럼: -1(PASS) / 1(FAIL) → 0/1 로 변환
        y = (labels.iloc[:, 0] == 1).astype(int)
        X.columns = [f"sensor_{i:03d}" for i in range(X.shape[1])]
        return X, y, False

    # 더미 폴백: 1567 × 591 정규분포 + 6.6% 불량
    print("[WARN] 원본 SECOM 없음 → 더미 데이터 생성 (1567 × 591, fail 6.6%)")
    rng = np.random.default_rng(RANDOM_STATE)
    n, p = 1567, 591
    X = pd.DataFrame(
        rng.normal(size=(n, p)),
        columns=[f"sensor_{i:03d}" for i in range(p)],
    )
    # 일부 컬럼에 결측치 주입 (10~30%)
    for i in rng.choice(p, size=80, replace=False):
        mask = rng.random(n) < rng.uniform(0.1, 0.3)
        X.iloc[mask, i] = np.nan
    # 불량 라벨 — 일부 센서 강한 신호로 만들기
    score = X.iloc[:, [3, 17, 42]].fillna(0).sum(axis=1)
    threshold = score.quantile(0.934)  # 상위 6.6%
    y = (score > threshold).astype(int)
    return X, y, True


X_raw, y_raw, is_dummy = load_secom()
print(f"원본: {X_raw.shape} / 불량 비율 {y_raw.mean()*100:.2f}%")

# %% [markdown]
# ## 2. 결측치 처리 — 50% 이상 결측 컬럼 제거, 나머지 median


def handle_missing(X: pd.DataFrame) -> pd.DataFrame:
    miss_rate = X.isna().mean()
    keep = miss_rate[miss_rate < 0.5].index
    dropped = X.shape[1] - len(keep)
    X = X[keep].copy()
    X = X.fillna(X.median(numeric_only=True))
    print(f"결측치 컬럼 제거: {dropped} / 남은 컬럼: {X.shape[1]}")
    return X


X_clean = handle_missing(X_raw)

# %% [markdown]
# ## 3. 저분산 컬럼 제거 (var < 1e-4)


def drop_low_variance(X: pd.DataFrame, threshold: float = 1e-4) -> pd.DataFrame:
    variances = X.var()
    keep = variances[variances > threshold].index
    dropped = X.shape[1] - len(keep)
    print(f"저분산 제거: {dropped} / 남은 컬럼: {len(keep)}")
    return X[keep].copy()


X_lv = drop_low_variance(X_clean)

# %% [markdown]
# ## 4. 상관 0.95 이상 쌍에서 한쪽 제거


def drop_high_corr(X: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
    corr = X.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1))
    to_drop = [c for c in upper.columns if any(upper[c] > threshold)]
    print(f"고상관 제거: {len(to_drop)} / 남은 컬럼: {X.shape[1] - len(to_drop)}")
    return X.drop(columns=to_drop)


X_uncorr = drop_high_corr(X_lv)

# %% [markdown]
# ## 5. 스케일링 (StandardScaler)


scaler = StandardScaler()
X_scaled = pd.DataFrame(
    scaler.fit_transform(X_uncorr),
    columns=X_uncorr.columns,
    index=X_uncorr.index,
)

# %% [markdown]
# ## 6. Stratified Split — train/test 분리 후 train에만 SMOTE
# Data Leakage 방지: SMOTE는 split 이후 train fold에만 적용


X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y_raw,
    test_size=TEST_SIZE,
    stratify=y_raw,
    random_state=RANDOM_STATE,
)
print(f"Split — train {len(y_train)} / test {len(y_test)}")
print(
    f"train fail: {y_train.mean()*100:.2f}% / test fail: {y_test.mean()*100:.2f}%"
)

# %% [markdown]
# ## 7. SMOTE — train fold만


smote = SMOTE(random_state=RANDOM_STATE)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(
    f"SMOTE 후 train — {len(y_train_sm)} samples / fail {y_train_sm.mean()*100:.2f}%"
)

# %% [markdown]
# ## 8. .pkl 저장


def save_processed() -> None:
    pd.to_pickle(X_train_sm, PROC_DIR / "secom_X_train.pkl")
    pd.to_pickle(y_train_sm, PROC_DIR / "secom_y_train.pkl")
    pd.to_pickle(X_test, PROC_DIR / "secom_X_test.pkl")
    pd.to_pickle(y_test, PROC_DIR / "secom_y_test.pkl")
    # 데모 샘플 — 시연용 4건 (PASS 2 + FAIL 2)
    fail_idx = y_test[y_test == 1].index[:2]
    pass_idx = y_test[y_test == 0].index[:2]
    demo_idx = list(fail_idx) + list(pass_idx)
    demo_sample = X_test.loc[demo_idx]
    demo_sample.to_pickle(PROC_DIR / "demo_sample.pkl")
    print(f"저장 완료 → {PROC_DIR}")


save_processed()

print("\n=== T1 완료 ===")
print(f"더미 모드: {is_dummy}")
print(f"피처 수: {X_train_sm.shape[1]}")
print(f"train: {len(y_train_sm)} (SMOTE 적용)")
print(f"test:  {len(y_test)}")
print("다음: scripts/02_train.py")
