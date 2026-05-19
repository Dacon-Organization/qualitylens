# Models

학습된 모델·threshold·model card 보관 위치.

## 파일

| 파일 | 출처 | git |
|---|---|---|
| `xgb_secom.joblib` | `scripts/02_train.py` | 제외 (큰 바이너리) |
| `threshold_table.csv` | `scripts/02_train.py` | 포함 |
| `model_card.md` | `scripts/02_train.py` | 포함 |
| `shap_explainer.pkl` | `scripts/03_shap.py` | 제외 |
| `shap_top20.csv` | `scripts/03_shap.py` | 포함 |

`.joblib` / `.pkl` 큰 산출물은 `.gitignore` 로 제외. 본선장 노트북에 직접 생성하거나
별도 채널로 전달.

## 운영 규칙

- 본선장에서 **재학습 절대 금지** → 사전 직렬화본만 로드
- joblib 버전 충돌 방지 위해 `requirements.txt` 버전 고정 유지
- 모델 로드 실패 시 `skills/codex-bridge/fallback-playbook.md` 시나리오 2 참조
