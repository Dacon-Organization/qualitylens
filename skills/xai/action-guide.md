# Action Guide

## 역할
SHAP attribution + Threshold Engine 결과를 결합하여 공장 작업자가 즉시 실행 가능한
조치 가이드 메시지를 생성한다. "이 배치가 실패할 것이다" → "이 센서를 이렇게 조정하라"
의 간극을 채우는 QualityLens의 핵심 차별화 로직이다.

---

## 핵심 로직 (3단계)

### Step 1: 이상 피처 추출
```python
def get_flagged_features(batch_idx, shap_values, X_test, top_n=5):
    """실패 예측 배치에서 |SHAP| 상위 N개 피처 반환"""
    sv = shap_values[batch_idx]                       # (n_features,)
    ranked = np.argsort(np.abs(sv))[::-1][:top_n]
    return [
        {"feature": feature_names[i], "shap_value": sv[i], "current_value": X_test.iloc[batch_idx, i]}
        for i in ranked
        if sv[i] > 0   # fail 방향 기여 피처만 (양수 SHAP = fail 확률 증가)
    ]
```

### Step 2: Threshold 조회
```python
def check_threshold(feature, current_value, threshold_table):
    """현재값이 정상범위를 벗어났는지 확인"""
    row = threshold_table[threshold_table["feature"] == feature].iloc[0]
    lower, upper = row["lower"], row["upper"]
    is_abnormal = not (lower <= current_value <= upper)
    return {"lower": lower, "upper": upper, "is_abnormal": is_abnormal}
```

- `threshold_table`: `modeling/threshold-engine.md`에서 생성 (PASS 샘플 mean±2σ)
- 정상범위 벗어남 = SHAP 양수 + 범위 이탈의 교집합 → 신뢰도 높은 조치 타겟

### Step 3: 조치 메시지 생성
```python
MESSAGE_TEMPLATE = (
    "센서 {sensor_name} 비정상 감지 "
    "(현재: {current_value:.2f}) "
    "→ 정상 권장 범위: {lower:.2f} ~ {upper:.2f}"
)

def build_action_message(feature, current_value, lower, upper):
    return MESSAGE_TEMPLATE.format(
        sensor_name=SENSOR_DISPLAY_NAMES.get(feature, feature),
        current_value=current_value,
        lower=lower,
        upper=upper
    )
```

---

## 시나리오 카탈로그 (P4 데모용)

MVP에서는 3개 시나리오를 하드코딩하여 안정적인 데모를 보장한다.
SHAP 값은 사전 계산된 캐시에서 로드한다.

### Scenario A: 식각 온도 이상 (Temperature Spike)
```python
SCENARIO_A = {
    "id": "scenario_a",
    "name": "식각 온도 이상",
    "trigger_feature": "etch_temperature",
    "fail_probability": 0.83,
    "shap_top": [
        {"feature": "etch_temperature", "shap_value": 0.62, "current": 185.3},
        {"feature": "process_time",     "shap_value": 0.18, "current": 142.0},
    ],
    "action": "센서 etch_temperature 비정상 감지 (현재: 185.3°C) → 정상 권장 범위: 160.0 ~ 175.0°C",
    "severity": "danger"
}
```

### Scenario B: 압력 불안정 (Pressure Fluctuation)
```python
SCENARIO_B = {
    "id": "scenario_b",
    "name": "압력 불안정",
    "trigger_feature": "chamber_pressure",
    "fail_probability": 0.61,
    "shap_top": [
        {"feature": "chamber_pressure", "shap_value": 0.41, "current": 0.023},
        {"feature": "gas_flow_rate",    "shap_value": 0.22, "current": 48.7},
    ],
    "action": "센서 chamber_pressure 비정상 감지 (현재: 0.023 Pa) → 정상 권장 범위: 0.030 ~ 0.045 Pa",
    "severity": "warning"
}
```

### Scenario C: 다중 센서 이상 (Multi-Sensor Failure)
```python
SCENARIO_C = {
    "id": "scenario_c",
    "name": "다중 센서 이상",
    "trigger_feature": "multiple",
    "fail_probability": 0.91,
    "shap_top": [
        {"feature": "etch_temperature", "shap_value": 0.55, "current": 183.1},
        {"feature": "chamber_pressure", "shap_value": 0.38, "current": 0.021},
        {"feature": "rf_power",         "shap_value": 0.27, "current": 312.0},
    ],
    "actions": [
        "센서 etch_temperature 비정상 감지 (현재: 183.1°C) → 정상 권장 범위: 160.0 ~ 175.0°C",
        "센서 chamber_pressure 비정상 감지 (현재: 0.021 Pa) → 정상 권장 범위: 0.030 ~ 0.045 Pa",
        "센서 rf_power 비정상 감지 (현재: 312.0 W) → 정상 권장 범위: 250.0 ~ 290.0 W",
    ],
    "severity": "danger"
}
```

---

## Streamlit UI 연동 (원클릭 수락)

```python
def render_action_card(scenario):
    with st.expander(f"[{scenario['severity'].upper()}] {scenario['name']}", expanded=True):
        for msg in scenario.get("actions", [scenario.get("action")]):
            st.warning(msg)

        if st.button("조치 완료 기록", key=f"accept_{scenario['id']}"):
            record = {
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario["id"],
                "scenario_name": scenario["name"],
                "batch_id": st.session_state.get("selected_batch_id"),
                "accepted_by": "operator"
            }
            st.session_state.setdefault("action_history", []).append(record)
            st.success("조치 이력이 기록되었습니다.")
```

- `st.session_state["action_history"]`: 세션 내 조치 이력 누적
- ui/ 단계에서 이력 테이블로 렌더링 (`ui/layout.md` 참조)

---

## 우선순위 규칙

1. |SHAP value| 내림차순 정렬
2. Threshold 이탈 피처 우선 표시 (이탈 없으면 "범위 내 미세 변동" 안내)
3. 다중 이상 시 최대 3개 메시지만 표시 (현장 가독성)
4. fail_probability < 0.5인 배치에는 조치 가이드 미표시 (오탐 억제)
