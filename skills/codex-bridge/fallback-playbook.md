# fallback-playbook — 본선장 비상 대응

## 시나리오 1: Streamlit 앱 실행 실패

```
1. streamlit run app/app.py --logger.level=debug
2. 에러 메시지 첫 줄 식별
3. roadmap.html 작업 노트에 마지막 동작 시점 확인
4. git stash → 마지막 동작 commit 으로 hard reset
5. 그래도 안되면 → 백업 슬라이드 PDF 발표
```

## 시나리오 2: 모델 로드 실패 (joblib 버전 충돌)

```python
# 사전 작업 시 numpy/sklearn 버전 requirements.txt 고정
# 본선장에서는 절대 pip upgrade 금지

# 폴백: 더미 예측 결과 사용
DEMO_RESULT = pd.read_csv("data/processed/demo_result_backup.csv")
```

## 시나리오 3: 인터넷 끊김

- 모든 모델·데이터는 로컬에 있어야 함 (사전 점검 필수)
- Codex/Claude 모두 불가 → roadmap.html + 기존 코드로만 시연
- 발표 스크립트는 외워둘 것

## 시나리오 4: SHAP 시각화 깨짐

```python
# matplotlib 백엔드 명시
import matplotlib
matplotlib.use("Agg")

# 폴백: 사전 캐싱된 PNG 이미지 표시
st.image("data/processed/shap_demo.png")
```

## 시나리오 5: 발표 5분 초과 위험

- 4분 시점에 시연 중단 + 마무리 슬라이드로 이동
- 미리 4:30 알람 설정 (스마트워치)
