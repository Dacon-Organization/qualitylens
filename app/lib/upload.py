"""사용자 CSV 업로드 → 검증 → 모델 추론 → 결과 패키지.

QualityLens의 MVP 핵심 갭 해결 — 실무자가 자기 공장 데이터를 즉시 시연 가능.

설계 원칙:
- 591개 sensor_NNN 컬럼이 모두 있을 필요 없음. 누락은 0으로 채움 (z-score 정규화 가정).
- sample_id 컬럼은 선택(없으면 행 번호 사용).
- 결과는 pred_proba/pred_label + 상위 SHAP 변수까지 함께 반환.
- 결정성 보장: 같은 입력 → 같은 출력 (모델 재학습 X).
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

EXPECTED_N_FEATURES = 591
SENSOR_PREFIX = "sensor_"
SAMPLE_TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "processed"
)


@dataclass
class UploadValidationReport:
    """업로드 CSV 검증 결과."""

    n_rows: int
    n_cols_present: int  # 입력 CSV가 가진 sensor_NNN 컬럼 수
    n_cols_filled: int  # 누락되어 0으로 채운 컬럼 수
    has_sample_id: bool
    warnings: list[str]


def expected_columns() -> list[str]:
    """모델이 기대하는 591개 컬럼명 (sensor_000 ~ sensor_590)."""
    return [f"{SENSOR_PREFIX}{i:03d}" for i in range(EXPECTED_N_FEATURES)]


def parse_uploaded_csv(
    file_obj: "io.IOBase | bytes", encoding: str = "utf-8"
) -> pd.DataFrame:
    """업로드된 파일 객체에서 DataFrame 파싱.

    UTF-8 / UTF-8-sig / CP949 자동 시도.
    """
    if isinstance(file_obj, (bytes, bytearray)):
        raw = bytes(file_obj)
    else:
        raw = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

    for enc in (encoding, "utf-8-sig", "cp949"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 인코딩을 인식할 수 없습니다 (utf-8/utf-8-sig/cp949 모두 실패)")


def validate_and_align(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, UploadValidationReport]:
    """업로드 DataFrame을 모델 입력 스키마(591컬럼)에 맞춰 정렬.

    Returns
    -------
    X_aligned : pd.DataFrame (n_rows × 591)
    sample_ids : pd.Series
    report : UploadValidationReport
    """
    if df.empty:
        raise ValueError("업로드 CSV가 비어 있습니다.")

    warnings: list[str] = []
    cols = list(df.columns)

    # sample_id 컬럼 추출 (있으면 사용, 없으면 행 번호)
    sample_id_col = next(
        (c for c in cols if c.lower() in {"sample_id", "id", "sampleid"}), None
    )
    if sample_id_col:
        sample_ids = df[sample_id_col].copy()
        sample_ids.name = "sample_id"
    else:
        sample_ids = pd.Series(range(1, len(df) + 1), name="sample_id")
        warnings.append("sample_id 컬럼이 없어 행 번호로 자동 할당했습니다.")

    # sensor_NNN 컬럼만 추출
    expected = expected_columns()
    present_sensors = [c for c in cols if c in expected]
    missing_sensors = [c for c in expected if c not in cols]

    if not present_sensors:
        raise ValueError(
            "sensor_000 ~ sensor_590 형식의 컬럼이 하나도 없습니다. "
            "샘플 템플릿 (`📥 샘플 CSV 다운로드`)을 받아 형식을 확인하세요."
        )

    # 정렬된 DataFrame 구성 (591 컬럼 모두, 누락은 0)
    X_aligned = pd.DataFrame(0.0, index=df.index, columns=expected)
    for c in present_sensors:
        X_aligned[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    if missing_sensors:
        warnings.append(
            f"{len(missing_sensors)}개 sensor 컬럼이 누락되어 0으로 채웠습니다 "
            f"(z-score 정규화 가정 — 평균값과 동일)."
        )

    if len(present_sensors) < 30:
        warnings.append(
            f"유효 sensor 컬럼이 {len(present_sensors)}개로 매우 적습니다. "
            "예측 정확도가 떨어질 수 있습니다."
        )

    report = UploadValidationReport(
        n_rows=len(df),
        n_cols_present=len(present_sensors),
        n_cols_filled=len(missing_sensors),
        has_sample_id=sample_id_col is not None,
        warnings=warnings,
    )

    return X_aligned, sample_ids, report


def predict_uploaded(
    X_aligned: pd.DataFrame, sample_ids: pd.Series, model, threshold: float = 0.5
) -> pd.DataFrame:
    """모델 추론 결과를 DataFrame으로 반환.

    Columns: sample_id, pred_proba, pred_label, risk_tier
    """
    proba = model.predict_proba(X_aligned)[:, 1]
    label = (proba >= threshold).astype(int)
    risk = pd.cut(
        proba,
        bins=[-0.001, 0.30, 0.50, 1.001],
        labels=["🟢 정상", "🟡 주의", "🔴 위험"],
    )

    return pd.DataFrame(
        {
            "sample_id": sample_ids.values,
            "pred_proba": proba.round(4),
            "pred_label": label,
            "risk_tier": risk,
        }
    )


def build_sample_template() -> bytes:
    """다운로드용 샘플 CSV 템플릿 (3행 × 591컬럼) 생성."""
    cols = ["sample_id"] + expected_columns()
    rows = [
        [1] + [0.0] * EXPECTED_N_FEATURES,
        [2] + [0.5] * EXPECTED_N_FEATURES,
        [3] + [-0.5] * EXPECTED_N_FEATURES,
    ]
    df = pd.DataFrame(rows, columns=cols)
    return df.to_csv(index=False).encode("utf-8-sig")
