# token-saving — 본선장 토큰 절약 5대 원칙

## 1. 모델 재학습 금지

```python
# OK — 직렬화 로드만
import joblib
model = joblib.load("models/xgb_secom.joblib")

# NG — 본선장에서 재학습 절대 금지
model.fit(X_train, y_train)
```

학습은 D-3 ~ D-1에 Claude Opus로 완료. 본선장에서는 추론만.

## 2. SHAP 재계산 금지

```python
# OK — 사전 계산본 로드
shap_values = joblib.load("models/shap_explainer.pkl")
top20 = pd.read_csv("models/shap_top20.csv")

# NG — TreeExplainer 본선장 호출
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)  # 비용 폭증
```

## 3. 채팅 컨텍스트 의존 최소화

- 작업 결정·결과는 `docs/roadmap.html` 작업 노트 영역에 누적
- Codex 세션 시작 시 노트 발췌만 붙여넣기 (전체 대화 재구성 X)

## 4. 단일 파일 단위 호출

```
NG: "app/pages/P1.py, P2.py, P3.py 동시에 수정해줘"
OK: "app/pages/P1.py 의 KPI 카드만 수정해줘"
```

멀티 파일 호출은 토큰 5~10배 폭증.

## 5. 결정론적 데모

데모 시연 중 모델 호출 X. 사전 준비된 샘플 데이터·결과만 표시.

```python
# OK — 사전 결과 로드
DEMO_SAMPLE = joblib.load("data/processed/demo_sample.pkl")
DEMO_RESULT = pd.read_csv("data/processed/demo_result.csv")
```
