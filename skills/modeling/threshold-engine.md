# threshold-engine — 센서 정상범위 계산 엔진

## 핵심 개념

FAIL 제품의 이상 센서를 식별하기 위해 **PASS 제품만의 통계**로 정상범위를 정의한다.
FAIL 데이터로 범위를 계산하면 이상 자체가 기준에 포함되므로 반드시 PASS 전용으로 계산.

## threshold_table 생성

```python
import pandas as pd
import numpy as np

def build_threshold_table(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """
    PASS 제품(label=0)의 센서 통계로 정상범위 계산.
    Returns: threshold_table with columns [sensor_id, mean, std, lower, upper]
    """
    X_pass = X_train[y_train == 0]   # PASS 제품만 필터

    stats = pd.DataFrame({
        "sensor_id": X_pass.columns,
        "mean": X_pass.mean().values,
        "std": X_pass.std().values,
    })

    sigma = 2.0   # 2σ = 95.4% 커버리지 (3σ는 너무 넓어 sensitivity 저하)
    stats["lower"] = stats["mean"] - sigma * stats["std"]
    stats["upper"] = stats["mean"] + sigma * stats["std"]

    # std=0 센서 (상수 피처) 처리: range를 NaN으로 마킹 → 이상 감지 제외
    stats.loc[stats["std"] == 0, ["lower", "upper"]] = np.nan

    return stats.reset_index(drop=True)
```

## 이상 센서 플래그 로직

```python
def flag_anomalous_sensors(
    sample: pd.Series,
    threshold_table: pd.DataFrame,
    shap_values: pd.Series,
    shap_threshold: float = 0.01
) -> pd.DataFrame:
    """
    단일 샘플에서 이상 센서 목록 반환.
    조건: 정상범위 이탈 AND SHAP contribution > shap_threshold (둘 다 만족 시 플래그)
    """
    tt = threshold_table.set_index("sensor_id")
    results = []

    for sensor in sample.index:
        if sensor not in tt.index:
            continue
        lower, upper = tt.loc[sensor, "lower"], tt.loc[sensor, "upper"]
        if pd.isna(lower):   # 상수 피처 건너뜀
            continue

        value = sample[sensor]
        out_of_range = (value < lower) or (value > upper)
        shap_contrib = abs(shap_values.get(sensor, 0))
        high_shap = shap_contrib > shap_threshold

        if out_of_range and high_shap:
            results.append({
                "sensor_id": sensor,
                "value": value,
                "lower": lower,
                "upper": upper,
                "deviation": (value - tt.loc[sensor, "mean"]) / tt.loc[sensor, "std"],
                "shap_contribution": shap_contrib,
                "flag": True,
            })

    return pd.DataFrame(results).sort_values("shap_contribution", ascending=False)
```

## threshold_table 저장/로드

```python
# 저장 (학습 후 1회)
threshold_table.to_csv("outputs/threshold_table.csv", index=False)

# 로드 (추론 시)
threshold_table = pd.read_csv("outputs/threshold_table.csv")
```

## sigma 선택 기준

| sigma | 커버리지 | 특징 |
|-------|----------|------|
| 2.0 | 95.4% | 기본값. 민감도/특이도 균형 |
| 2.5 | 98.8% | 오경보 감소, 민감도 소폭 저하 |
| 3.0 | 99.7% | 오경보 최소화 (극단 이상만 감지) |

> 반도체 공정: 2σ 권장. FAIL 누락 최소화 우선 시 1.5σ 고려.

## Integration Point

- `xai/action-guide.md`와 연동: flagged sensors → 조치 권고 생성
- `ui/`에서 threshold_table을 시각화: 게이지 차트, 범위 오버레이
- 출력 컬럼 `deviation` = 표준편차 단위 이탈 → 심각도 순위 정렬에 사용
