# Model Card — QualityLens XGBoost

## 학습 환경
- 알고리즘: XGBoost (binary:logistic, eval_metric=aucpr)
- 데이터 소스: **DUMMY** (UCI SECOM 실데이터 / 더미 합성)
- Split: Stratified, test_size=0.2, random_state=42
- 검증: Stratified K-Fold (k=5)
- 클래스 불균형: SMOTE 적용 + scale_pos_weight=1.00

## 하이퍼파라미터
{'n_estimators': 400, 'max_depth': 6, 'learning_rate': 0.05, 'subsample': 0.9, 'colsample_bytree': 0.7, 'reg_lambda': 1.0, 'scale_pos_weight': 1.0, 'objective': 'binary:logistic', 'eval_metric': 'aucpr', 'tree_method': 'hist', 'random_state': 42}

## 성능
- CV  MCC  : 0.9864 ± 0.0073
- CV  PRAUC: 0.9999 ± 0.0001
- Test MCC (@0.5)             : 0.6834
- Test MCC (@0.0308, Youden's J): 0.6302
- Test PR-AUC                 : 0.8229

## 운영 threshold
- 추론 시 사용: **0.0308**
- 평가 지표: MCC (불균형 6.6% fail rate에 최적)

## 산출물
- `models/xgb_secom.joblib`     — 직렬화 모델
- `models/threshold_table.csv`  — sensor별 mean±2σ 정상 범위

## 운영 규칙 (codex-bridge/token-saving.md)
- 본선장에서 재학습 금지 — 직렬화 로드만
- 단일 샘플 추론 < 10ms (라인 모니터링 요건)
