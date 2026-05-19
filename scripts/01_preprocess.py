"""T1 — 데이터 파이프라인.

UCI SECOM 원본을 로드해 결측치/스케일링/분산-상관 필터링/SMOTE/Stratified Split을
거쳐 X_train, X_test, y_train, y_test를 ``.pkl`` 로 저장한다.

원본이 없으면 더미 데이터를 생성해 파이프라인이 끝까지 동작하도록 폴백한다.

Jupyter/VS Code 셀(`# %%`) 단위 실행 가능. CLI에서는::

    python scripts/01_preprocess.py
"""

from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="T1 전처리 — UCI SECOM 실데이터 또는 더미")
    parser.add_argument(
        "--source",
        choices=["real", "dummy"],
        default="real",
        help="real: data/raw 의 UCI 원본 사용 / dummy: 합성 더미 생성",
    )
    return parser.parse_args()


ARGS = parse_args() if __name__ == "__main__" else argparse.Namespace(source="real")
SOURCE = ARGS.source  # "real" or "dummy"
SUFFIX = f"_{SOURCE}"  # "_real" or "_dummy"

RANDOM_STATE = 42
TEST_SIZE = 0.2

# %% [markdown]
# ## 1. 원본 로드 (없으면 더미)


def load_secom(source: str) -> tuple[pd.DataFrame, pd.Series, bool]:
    """source 에 따라 실데이터 또는 더미를 반환.

    Returns
    -------
    X, y, is_dummy_actually
        is_dummy_actually 는 source='dummy' 일 때만 True.
        source='real' 인데 파일 없으면 FileNotFoundError 발생.
    """
    data_path = RAW_DIR / "secom.data"
    labels_path = RAW_DIR / "secom_labels.data"

    if source == "real":
        if not (data_path.exists() and labels_path.exists()):
            raise FileNotFoundError(
                f"실데이터 모드인데 원본 부재: {data_path}. "
                "scripts/00_download_secom.py 를 먼저 실행하거나 --source dummy 사용."
            )
        X = pd.read_csv(data_path, sep=r"\s+", header=None)
        labels = pd.read_csv(labels_path, sep=r"\s+", header=None)
        y = (labels.iloc[:, 0] == 1).astype(int)
        X.columns = [f"sensor_{i:03d}" for i in range(X.shape[1])]
        return X, y, False

    # source == "dummy"
    print("[INFO] 더미 모드 — 1567 × 591 합성 데이터 생성 (fail 6.6%)")
    rng = np.random.default_rng(RANDOM_STATE)
    n, p = 1567, 591
    X = pd.DataFrame(
        rng.normal(size=(n, p)),
        columns=[f"sensor_{i:03d}" for i in range(p)],
    )
    for i in rng.choice(p, size=80, replace=False):
        mask = rng.random(n) < rng.uniform(0.1, 0.3)
        X.iloc[mask, i] = np.nan
    score = X.iloc[:, [3, 17, 42]].fillna(0).sum(axis=1)
    threshold = score.quantile(0.934)
    y = (score > threshold).astype(int)
    return X, y, True


X_raw, y_raw, is_dummy = load_secom(SOURCE)
print(f"[{SOURCE}] 원본: {X_raw.shape} / 불량 비율 {y_raw.mean()*100:.2f}%")

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
    pd.to_pickle(X_train_sm, PROC_DIR / f"secom_X_train{SUFFIX}.pkl")
    pd.to_pickle(y_train_sm, PROC_DIR / f"secom_y_train{SUFFIX}.pkl")
    pd.to_pickle(X_test, PROC_DIR / f"secom_X_test{SUFFIX}.pkl")
    pd.to_pickle(y_test, PROC_DIR / f"secom_y_test{SUFFIX}.pkl")
    fail_idx = y_test[y_test == 1].index[:2]
    pass_idx = y_test[y_test == 0].index[:2]
    demo_idx = list(fail_idx) + list(pass_idx)
    demo_sample = X_test.loc[demo_idx]
    demo_sample.to_pickle(PROC_DIR / f"demo_sample{SUFFIX}.pkl")
    print(f"[{SOURCE}] 저장 완료 → {PROC_DIR}")


save_processed()

print(f"\n=== T1 완료 ({SOURCE}) ===")
print(f"실제 더미 폴백: {is_dummy}")
print(f"피처 수: {X_train_sm.shape[1]}")
print(f"train: {len(y_train_sm)} (SMOTE 적용)")
print(f"test:  {len(y_test)}")
print("다음: scripts/02_train.py")

# %% [markdown]
# ## 9. HTML 보고서 출력 (P-A G3)

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.lib.report_render import write as write_report

_sections = [
    {
        "title": "1. 데이터 형상",
        "body_html": (
            f"<table><tr><th>속성</th><th>값</th></tr>"
            f"<tr><td>소스</td><td>{SOURCE}</td></tr>"
            f"<tr><td>원본 shape</td><td>{X_raw.shape}</td></tr>"
            f"<tr><td>결측치 컬럼 제거 후</td><td>{X_clean.shape}</td></tr>"
            f"<tr><td>저분산·고상관 제거 후</td><td>{X_uncorr.shape}</td></tr>"
            f"<tr><td>train (SMOTE 후)</td><td>{X_train_sm.shape}</td></tr>"
            f"<tr><td>test</td><td>{X_test.shape}</td></tr>"
            f"<tr><td>불량 비율 (원본)</td><td>{y_raw.mean()*100:.2f}%</td></tr>"
            f"</table>"
        ),
    },
    {
        "title": "2. 결측치 분포 (상위 20)",
        "body_html": (
            "<table><tr><th>sensor</th><th>missing_rate</th></tr>"
            + "".join(
                f"<tr><td>{s}</td><td>{r*100:.2f}%</td></tr>"
                for s, r in X_raw.isna().mean().sort_values(ascending=False).head(20).items()
            )
            + "</table>"
        ),
    },
]
write_report("preprocessing", source=SOURCE, sections=_sections)
