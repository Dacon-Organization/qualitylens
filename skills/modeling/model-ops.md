# model-ops — 모델 저장/로드/관리

## 파일 명명 규칙

```
qualitylens_xgb_v{version}_{YYYYMMDD}.joblib

예시:
  qualitylens_xgb_v1_20260430.joblib
  qualitylens_xgb_v2_20260515.joblib   ← 재학습 후 버전 증가
```

저장 위치: `models/` 디렉토리 (git 추적 제외, `.gitignore`에 등록)

## 저장 / 로드

```python
import joblib
from datetime import date

def save_model(model, version: int, output_dir: str = "models/"):
    today = date.today().strftime("%Y%m%d")
    filename = f"qualitylens_xgb_v{version}_{today}.joblib"
    path = f"{output_dir}{filename}"
    joblib.dump(model, path, compress=3)   # compress=3: 속도/크기 균형
    print(f"Model saved: {path}")
    return path

def load_model(path: str):
    return joblib.load(path)
```

## SHAP Explainer 캐싱

SHAP TreeExplainer 생성 비용이 크므로 사전 계산 후 저장.

```python
import shap

def cache_shap_explainer(model, X_background: pd.DataFrame, output_dir: str = "models/"):
    """
    X_background: 대표 샘플 (예: X_train의 10% 랜덤 샘플 또는 PASS 전체)
    """
    explainer = shap.TreeExplainer(model, X_background)
    path = output_dir + "shap_explainer.joblib"
    joblib.dump(explainer, path, compress=3)
    print(f"SHAP explainer cached: {path}")
    return explainer

def load_shap_explainer(path: str = "models/shap_explainer.joblib"):
    return joblib.load(path)

# 추론 시 단일 샘플 SHAP
def get_shap_values(explainer, sample: pd.DataFrame) -> pd.Series:
    shap_vals = explainer.shap_values(sample)
    return pd.Series(shap_vals[0], index=sample.columns)
```

## Model Card (메타데이터)

학습 완료 후 `models/model_card.json`에 저장:

```python
import json

model_card = {
    "model_name": f"qualitylens_xgb_v{version}_{today}",
    "training_date": today,
    "framework": "XGBoost",
    "objective": "binary:logistic",
    "dataset": {
        "total_samples": len(X_train),
        "pass_count": int((y_train == 0).sum()),
        "fail_count": int((y_train == 1).sum()),
        "feature_count": X_train.shape[1],
    },
    "cv_results": {
        "mean_mcc": float(metrics_df["val_mcc"].mean()),
        "std_mcc": float(metrics_df["val_mcc"].std()),
        "best_fold_mcc": float(metrics_df["val_mcc"].max()),
    },
    "best_threshold": best_threshold,
    "scale_pos_weight": scale_pos_weight,
    "notes": "",   # 실험 메모
}

with open("models/model_card.json", "w") as f:
    json.dump(model_card, f, indent=2, ensure_ascii=False)
```

## 재학습 트리거 조건

현재는 수동 트리거 기준. 향후 자동화 시 참조:

| 조건 | 임계값 | 조치 |
|------|--------|------|
| 프로덕션 MCC 저하 | 학습 MCC 대비 -0.05 초과 | 즉시 재학습 |
| 새 데이터 누적 | 기존 학습 데이터의 20% 이상 | 주기적 재학습 검토 |
| 센서 분포 변화 | KS-test p < 0.05인 센서 > 10% | 데이터 드리프트 알림 |
| 모델 파일 부재 | `models/` 디렉토리 비어 있음 | 최초 학습 실행 |

## 버전 관리 요약

```
models/
├── qualitylens_xgb_v1_20260430.joblib   ← 현재 production
├── qualitylens_xgb_v2_20260515.joblib   ← 최신 실험
├── shap_explainer.joblib
├── model_card.json
└── threshold_table.csv                  ← threshold-engine.md 출력
```

- 이전 버전은 30일 보관 후 삭제
- `model_card.json`은 최신 버전 메타데이터만 유지
