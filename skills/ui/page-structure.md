# Page Structure

## 5-Page Architecture

| ID | 파일명 | 제목 | 목적 |
|----|--------|------|------|
| P1 | `pages/1_Dashboard.py` | 실시간 대시보드 | 전체 공정 상태 한눈에 파악, KPI + 센서 현황 |
| P2 | `pages/2_Predict.py` | 불량 예측 | 배치/센서 입력 → 실시간 예측 결과 |
| P3 | `pages/3_Explain.py` | AI 설명 | SHAP 분석, 주요 원인 피처 시각화 |
| P4 | `pages/4_Act.py` | 조치 가이드 | 시나리오별 권고 액션, 원클릭 수락 |
| P5 | `pages/5_History.py` | 이력 조회 | 예측/조치 기록 테이블, 필터 검색 |

진입점: `app.py` (sidebar 네비게이션 렌더링)

## Streamlit Multi-page 설정

```
smart-factory-hackathon/
├── app.py              # 메인 진입점, 공통 설정
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Predict.py
│   ├── 3_Explain.py
│   ├── 4_Act.py
│   └── 5_History.py
└── utils/
    ├── components.py   # 재사용 컴포넌트
    ├── styles.py       # CSS 변수/색상
    └── state.py        # session_state 헬퍼
```

## Session State Keys

| 키 | 타입 | 설명 | 초기값 |
|----|------|------|--------|
| `model` | XGBoost object | 로드된 예측 모델 | None (lazy load) |
| `data` | pd.DataFrame | 현재 활성 배치 데이터 | None |
| `shap_values` | np.ndarray | 최근 예측의 SHAP 값 | None |
| `alerts` | List[dict] | 활성 알림 목록 `{id, severity, msg, ts}` | [] |
| `action_history` | List[dict] | 수락된 조치 기록 `{action_id, ts, user}` | [] |
| `selected_batch` | str | 현재 선택된 배치 ID | None |
| `last_prediction` | dict | 최근 예측 결과 `{prob, label, ts}` | None |
| `refresh_interval` | int | 자동 갱신 주기 (초) | 30 |

초기화: `app.py`에서 `if 'model' not in st.session_state:` 패턴으로 한 번만 설정

## 페이지 간 데이터 흐름

```
P2 Predict
  → session_state['data'] 업데이트
  → session_state['last_prediction'] 저장
  → session_state['shap_values'] 계산 후 저장
  → alerts에 위험 예측 시 알림 추가

P3 Explain
  ← session_state['shap_values'] 읽기
  ← session_state['last_prediction'] 읽기

P4 Act
  ← session_state['alerts'] 읽기
  → session_state['action_history'] 추가

P5 History
  ← session_state['action_history'] 읽기
  (선택) 외부 로그 파일 읽기
```

## Sidebar 네비게이션

```python
# app.py 패턴
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.markdown("## QualityLens")

    # 상태 인디케이터
    alert_count = len(st.session_state.get('alerts', []))
    if alert_count > 0:
        st.error(f"⚠ 알림 {alert_count}건")
    else:
        st.success("● 정상 운영 중")

    # 마지막 갱신 시각
    st.caption(f"갱신: {last_update_str}")
```

페이지 링크는 Streamlit이 `pages/` 디렉토리를 자동으로 사이드바에 등록함.
파일명 숫자 prefix로 순서 고정.
