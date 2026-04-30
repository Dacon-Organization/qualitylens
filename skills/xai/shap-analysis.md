# SHAP Analysis

## 역할
XGBoost 모델의 예측 결과를 SHAP TreeExplainer로 해석한다.
글로벌 분석(전체 피처 중요도)과 로컬 분석(배치별 원인 분해)을 모두 제공한다.

---

## TreeExplainer 초기화

```python
import shap
import joblib

model = joblib.load("models/xgboost_model.joblib")
explainer = shap.TreeExplainer(model)

# 테스트셋 전체에 대해 사전 계산 후 캐싱
shap_values = explainer.shap_values(X_test)          # shape: (n_samples, n_features)
expected_value = explainer.expected_value             # base value (log-odds)

joblib.dump(shap_values, "cache/shap_values.joblib")
joblib.dump(expected_value, "cache/shap_expected.joblib")
```

- `check_additivity=False`: 속도 최적화 (검증 단계 생략)
- TreeExplainer는 tree path 기반 exact SHAP → O(TLD), 단일 배치 < 50ms
- 캐시 miss 시에만 재계산, hit 시 즉시 반환

---

## 글로벌 분석 (전체 테스트셋 기준)

### Summary Plot (Beeswarm)
```python
shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
# 색상: 피처값 높음 → 빨간색, 낮음 → 파란색
# X축: SHAP value (양수 = fail 확률 증가)
```

### Feature Importance Bar Chart
```python
shap.summary_plot(shap_values, X_test, plot_type="bar",
                  feature_names=feature_names, show=False)
# |SHAP| 평균으로 정렬, 상위 20개 표시
```

- 두 플롯 모두 `plt.savefig()` → Streamlit `st.image()`로 렌더링
- 업데이트 빈도: 모델 재학습 시 1회 (정적 캐시)

---

## 로컬 분석 (배치별)

### Waterfall Plot
```python
idx = batch_index   # 대상 배치의 X_test 인덱스
shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[idx],
        base_values=expected_value,
        data=X_test.iloc[idx],
        feature_names=feature_names
    ),
    show=False
)
# 상위 10개 피처만 표시 (max_display=10)
# 빨간 bar = fail 방향 기여, 파란 bar = pass 방향 기여
```

### Force Plot (인터랙티브)
```python
shap.force_plot(
    expected_value,
    shap_values[idx],
    X_test.iloc[idx],
    feature_names=feature_names,
    matplotlib=False   # HTML 반환 → st.components.html()
)
```

---

## Dependence Plot (Top-3 피처)

```python
top3 = np.argsort(np.abs(shap_values).mean(0))[-3:][::-1]
for feat_idx in top3:
    shap.dependence_plot(
        feat_idx, shap_values, X_test,
        feature_names=feature_names,
        interaction_index="auto",   # 자동 상호작용 피처 탐지
        show=False
    )
```

- `interaction_index="auto"`: SHAP이 가장 강한 상호작용 피처를 자동 선택
- 점 색상 = 상호작용 피처 값 (높음=빨강, 낮음=파랑)
- 공정 엔지니어에게 "온도와 압력이 동시에 높을 때 fail"과 같은 인사이트 제공

---

## 시각화 색상 규칙

| 색상 | 의미 |
|------|------|
| 빨간색 (red) | fail 확률 증가 방향 기여 |
| 파란색 (blue) | fail 확률 감소(pass 방향) 기여 |
| 색 농도 | 기여 크기 비례 |

- `ui/chart-style.md`의 색상 팔레트와 통일 (primary red: `#E53E3E`, primary blue: `#3182CE`)
- 배경: 흰색 (`#FFFFFF`), 그리드 없음 (공장 현장 가독성 우선)

---

## 캐싱 전략

```
cache/
├── shap_values.joblib       # (n_test, n_features) float32
├── shap_expected.joblib     # scalar base value
└── shap_top_features.json   # [{feature, mean_abs_shap}, ...] 상위 20개
```

- 캐시 유효성: `models/xgboost_model.joblib` mtime과 비교 → 모델 갱신 시 자동 무효화
- `shap_top_features.json`: action-guide.md에서 피처 선택 시 참조

---

## 성능 참고

| 항목 | 수치 |
|------|------|
| TreeExplainer 초기화 | ~200ms (1회) |
| 전체 테스트셋 shap_values | ~2~5초 (1567 샘플) |
| 단일 배치 로컬 설명 (캐시 hit) | < 5ms |
| 단일 배치 로컬 설명 (캐시 miss) | < 50ms |
