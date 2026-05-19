# demo-toggle — 데모 ↔ 실데이터 전환

## 동기

- 본선 시연 중 네트워크·데이터 이슈에도 안정적 결과 보장
- 발표용 골든 패스 시나리오는 사전 결정론적으로 캐싱
- 심사위원이 직접 만져볼 때는 실데이터로 전환

## 사이드바 UI

```python
def demo_sidebar() -> bool:
    st.sidebar.title("🎬 운영 모드")
    mode = st.sidebar.radio(
        "데이터 소스",
        options=["데모 (결정론)", "실데이터 (UCI SECOM)"],
        index=0,
    )
    st.sidebar.caption(
        "데모 모드는 사전 캐싱된 샘플로 결정론적 결과를 보장합니다."
    )
    return mode.startswith("데모")
```

## 데모 샘플 사전 준비

```python
# 사전 작업 (D-1)
demo_sample = X_test.iloc[[10, 42, 100, 200]]  # 4건 (PASS 2 + FAIL 2)
demo_result = pd.DataFrame({
    "sample_id": demo_sample.index,
    "pred_proba": model.predict_proba(demo_sample)[:, 1],
    "label": ["PASS", "PASS", "FAIL", "FAIL"],
})
demo_sample.to_pickle("data/processed/demo_sample.pkl")
demo_result.to_csv("data/processed/demo_result.csv", index=False)
```

## 발표 골든 패스

1. 사이드바 → "데모 (결정론)" 선택
2. P2 → 4번째 샘플 (FAIL) 선택 → 이상 확률 0.78 표시
3. P3 → 동일 샘플 SHAP → "공정 8단계 온도 센서"가 최대 기여
4. P4 → "공정 8단계 냉각수 점검" 권고 카드 표시
5. P5 → 최근 4건 이력 표시

이 흐름은 모델 호출 없이 사전 결과 로드만으로 동작.
