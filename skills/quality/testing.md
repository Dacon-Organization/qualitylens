# Testing

## 단위 테스트 (Unit Tests)

테스트 파일: `tests/` 디렉토리, pytest 사용.

### 데이터 파이프라인
```python
# tests/test_data_pipeline.py
def test_sensor_normalization():
    raw = pd.DataFrame({"temp": [100, 200, 300], "pressure": [1.0, 2.0, 3.0]})
    normalized = normalize_sensors(raw)
    assert normalized["temp"].between(0, 1).all()

def test_missing_sensor_handling():
    df_with_nan = pd.DataFrame({"temp": [100, None, 300]})
    result = handle_missing(df_with_nan)
    assert result.isnull().sum().sum() == 0  # NaN 제거/대체 확인
```

### 모델 예측
```python
# tests/test_model.py
def test_prediction_output_range():
    model = load_model("models/xgboost_final.pkl")
    sample = get_sample_batch()
    prob = model.predict_proba(sample)[:, 1]
    assert prob.between(0, 1).all()

def test_prediction_speed():
    import time
    model = load_model("models/xgboost_final.pkl")
    sample = get_sample_batch()
    start = time.time()
    model.predict(sample)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"예측 시간 초과: {elapsed:.2f}s"
```

### SHAP 계산
```python
def test_shap_output_shape():
    shap_values = compute_shap(model, sample)
    assert shap_values.shape == sample.shape  # (n_samples, n_features)

def test_shap_speed():
    start = time.time()
    compute_shap(model, sample)
    assert time.time() - start < 3.0
```

## 통합 테스트 (Integration Tests)

```python
# tests/test_integration.py
def test_full_pipeline():
    """raw CSV → 예측 → SHAP → 알림 생성 전체 흐름"""
    raw_path = "tests/fixtures/sample_batch.csv"
    df = load_raw_data(raw_path)
    df_processed = preprocess(df)
    prediction = predict(model, df_processed)
    shap_vals = compute_shap(model, df_processed)
    alerts = generate_alerts(prediction, threshold=0.5)

    assert prediction["probability"] is not None
    assert shap_vals is not None
    assert isinstance(alerts, list)

def test_dashboard_render():
    """Streamlit 페이지 렌더링 오류 없음 확인"""
    # streamlit test runner 또는 subprocess로 실행
    result = subprocess.run(["streamlit", "run", "app.py", "--headless"], timeout=10)
    assert result.returncode == 0
```

## 데모 시나리오 검증

각 P4 시나리오가 예상 출력을 내는지 확인:

| 시나리오 | 입력 | 기대 출력 |
|---------|------|----------|
| 온도 이상 | temp > 95°C | 경고 알림, SHAP top1 = "temp" |
| 압력 급등 | pressure > 150 | 위험 알림, 즉시 점검 액션 |
| 정상 배치 | 모든 센서 정상 | 알림 없음, 불량확률 < 10% |
| 복합 이상 | temp+pressure 동시 이상 | 위험 알림, 다중 조치 가이드 |

```python
def test_anomaly_scenario_temp():
    df = inject_anomaly(base_df, sensor="temp", value=98)
    prob = predict(model, df)["probability"]
    shap_top = get_top_shap_feature(model, df)
    assert prob > 0.5
    assert shap_top == "temp"
```

## 엣지 케이스

| 케이스 | 처리 방법 | 테스트 |
|--------|----------|--------|
| 빈 데이터 | 에러 메시지 + 예측 건너뜀 | `test_empty_dataframe` |
| 전체 합격 배치 | 불량확률 < 5%, 알림 없음 | `test_all_pass_batch` |
| 전체 불량 배치 | 불량확률 > 95%, 다중 알림 | `test_all_fail_batch` |
| 센서 누락 | imputation 후 예측 진행 | `test_missing_sensors` |

## 성능 벤치마크

| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| 모델 추론 | < 1초 | `time.time()` 래핑 |
| SHAP 계산 | < 3초 | `time.time()` 래핑 |
| 페이지 로드 | < 2초 | 브라우저 Network 탭 |
| 데이터 전처리 | < 0.5초 | 100행 기준 |

벤치마크 실패 시: 모델 캐싱 (`@st.cache_resource`), 데이터 캐싱 (`@st.cache_data`) 확인 → `deployment.md` 참조.
