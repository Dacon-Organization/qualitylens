# page-specs — P1~P5 페이지별 명세

## P1 — 통합 대시보드 (`app.py`)

| 영역 | 위젯 | 데이터 소스 |
|---|---|---|
| KPI 4카드 | st.metric ×4 | 총 샘플 / 이상 비율 / MCC / 응답 시간 |
| 시계열 차트 | st.line_chart | 시간별 예측 확률 |
| 최근 이상 테이블 | st.dataframe | 최근 10건 이상 판정 |
| 알림 배너 | st.warning | 임계치 위반 센서 수 |

## P2 — 실시간 예측 (`1_📊_실시간_예측.py`)

| 영역 | 위젯 | 동작 |
|---|---|---|
| 입력 폼 | st.form + sliders ×N | 주요 센서값 입력 |
| 예측 버튼 | st.form_submit_button | `model.predict_proba()` 호출 |
| 결과 카드 | st.metric (이상 확률) | PASS / FAIL 라벨 |
| 게이지 차트 | plotly indicator | 이상 확률 시각화 |

## P3 — 원인 분석 (`2_🔍_원인_분석.py`)

| 영역 | 위젯 | 데이터 소스 |
|---|---|---|
| 샘플 선택 | st.selectbox | 분석할 샘플 ID |
| SHAP Top 10 | bar chart | `shap_top20.csv` 사전 계산본 로드 |
| Force Plot | st.image / st.components.v1.html | 사전 저장된 force plot |
| 센서 그룹 기여도 | radar chart | 그룹별 평균 SHAP |

**중요**: SHAP 재계산 절대 금지 → 사전 캐싱된 결과 로드

## P4 — 조치 가이드 (`3_🛠_조치_가이드.py`)

| 영역 | 위젯 | 동작 |
|---|---|---|
| 위반 센서 리스트 | st.dataframe | threshold_table 비교 |
| 권고 카드 | st.info / st.error | 센서별 조치 텍스트 (skills/xai/action-guide.md) |
| 우선순위 정렬 | radio | 위반 정도 / 비용 / 시간 기준 |

## P5 — 이력 조회 (`4_📜_이력_조회.py`)

| 영역 | 위젯 | 데이터 소스 |
|---|---|---|
| 날짜 필터 | st.date_input | 기간 선택 |
| 결과 필터 | st.multiselect | PASS / FAIL / 전체 |
| 결과 테이블 | st.dataframe | 정렬·검색 가능 |
| CSV 다운로드 | st.download_button | 필터 결과 export |
