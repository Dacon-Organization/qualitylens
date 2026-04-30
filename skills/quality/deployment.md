# Deployment

## requirements.txt 관리

```
# requirements.txt — 버전 고정 필수 (재현성)
streamlit==1.35.0
xgboost==2.0.3
shap==0.45.1
pandas==2.2.2
numpy==1.26.4
plotly==5.22.0
scikit-learn==1.4.2
matplotlib==3.9.0
```

버전 고정 이유: 해커톤 당일 환경 변수 방지. `pip freeze > requirements.txt`로 최종 고정.

설치: `pip install -r requirements.txt`

## 환경 변수

`.env` 파일 (git에 포함하지 말 것, `.gitignore`에 추가):
```
MODEL_PATH=models/xgboost_final.pkl
DATA_PATH=data/processed/
THRESHOLD=0.5
REFRESH_INTERVAL=30
LOG_LEVEL=INFO
```

로드 방법:
```python
from dotenv import load_dotenv
import os
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "models/xgboost_final.pkl")
```

해커톤 오프라인 환경: `.env` 파일 직접 준비. python-dotenv 패키지 requirements에 포함.

## Streamlit 설정 (`.streamlit/config.toml`)

```toml
[server]
port = 8501
headless = true
runOnSave = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#1565C0"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#212121"
font = "sans serif"

[runner]
fastReruns = true
```

## 성능 최적화: 캐싱

```python
# utils/state.py — 캐싱 패턴

@st.cache_resource  # 앱 생명주기 동안 1회만 로드
def load_model(path: str):
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)

@st.cache_data(ttl=300)  # 5분 캐시
def load_batch_data(batch_id: str) -> pd.DataFrame:
    return pd.read_csv(f"data/batches/{batch_id}.csv")

@st.cache_data(ttl=60)   # 1분 캐시
def compute_shap_cached(model_hash: str, data_hash: str):
    # 해시로 캐시 키 관리 — 같은 데이터면 재계산 안 함
    return compute_shap(model, data)
```

캐시 무효화: `st.cache_data.clear()` 또는 앱 재시작.

## 로컬 배포 체크리스트

```
배포 전 확인 항목:
[ ] requirements.txt 최신 상태
[ ] 모델 파일 존재 확인: models/xgboost_final.pkl
[ ] 데이터 파일 존재 확인: data/processed/
[ ] .env 파일 존재 (또는 환경변수 직접 설정)
[ ] .streamlit/config.toml 적용 확인
[ ] 테스트 통과: pytest tests/ -v
[ ] 포트 8501 사용 가능 확인

실행:
streamlit run app.py
```

접속: `http://localhost:8501`

## 네트워크 고려사항 (오프라인 해커톤)

- CDN 의존 제거: Plotly 등 외부 JS 로드 안 하도록 `plotly` 패키지 로컬 설치로 처리됨 (Streamlit이 자동 번들)
- Google Fonts 등 외부 폰트 사용 금지 → `config.toml`에서 `font = "sans serif"` 고정
- 인터넷 없는 환경 사전 테스트: Wi-Fi 끊고 `streamlit run app.py` 정상 동작 확인
- 모델/데이터 파일은 모두 로컬 경로 사용 (S3, GCS 등 원격 저장소 의존 없음)

## 디렉토리 최종 구조 확인

```
smart-factory-hackathon/
├── app.py
├── pages/
├── utils/
├── models/
│   └── xgboost_final.pkl
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── .streamlit/
│   └── config.toml
├── .env              (git 제외)
├── .gitignore
└── requirements.txt
```
