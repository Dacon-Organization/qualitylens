# Chart Style

## 제조 도메인 컬러 팔레트

| 상태 | 색상 코드 | 용도 |
|------|----------|------|
| Normal (정상) | `#2E7D32` | 정상 범위, 성공 지표, 합격 배치 |
| Warning (경고) | `#F57F17` | 주의 필요, 임계값 근접, 경고 알림 |
| Danger (위험) | `#C62828` | 불량 예측, 위험 상태, 즉시 조치 필요 |
| Neutral (중립) | `#1565C0` | 일반 정보, 선택된 항목, 추세선 |
| Background | `#F5F5F5` | 카드 배경, 섹션 구분 |
| Text Primary | `#212121` | 제목, 중요 수치 |
| Text Secondary | `#757575` | 부제목, 메타데이터 |

배경은 흰색 또는 연회색으로 유지. 어두운 테마 사용 금지 (공장 밝은 조명 환경).

## 페이지별 Plotly 차트 타입

### P1 Dashboard — 추세선 (Line Chart)
```python
# 센서값 시계열
fig = px.line(df, x="timestamp", y=sensor_cols,
              color_discrete_sequence=["#1565C0", "#2E7D32", "#F57F17"])
fig.update_layout(
    height=300,
    margin=dict(t=30, b=40, l=50, r=20),
    legend=dict(orientation="h", y=-0.2),
    paper_bgcolor="white",
    plot_bgcolor="#FAFAFA",
)
fig.update_xaxes(showgrid=True, gridcolor="#EEEEEE")
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")
```

### P2 Predict — Gauge + 확률 Bar
```python
# 불량 확률 게이지
# → dashboard-components.md의 sensor_gauge() 참조

# 피처별 기여 바 차트
fig = px.bar(feature_df, x="contribution", y="feature", orientation="h",
             color="direction",
             color_discrete_map={"증가": "#C62828", "감소": "#2E7D32"})
```

### P3 Explain — SHAP Waterfall + Beeswarm
```python
# SHAP waterfall (단일 예측 설명)
import shap
shap.plots.waterfall(shap_values[0], max_display=10, show=False)
fig = plt.gcf()
st.pyplot(fig)

# 전역 중요도 — horizontal bar
fig = px.bar(shap_summary_df, x="mean_abs_shap", y="feature",
             orientation="h", color_discrete_sequence=["#1565C0"])
```

### P4 Act — 액션 카드 (st.metric + HTML)
차트 없음. 텍스트 카드와 버튼 중심 레이아웃.

## 숫자 포맷 규칙

```python
def format_number(value, fmt_type: str) -> str:
    if fmt_type == "percentage":
        return f"{value:.1f}%"           # 소수점 1자리
    elif fmt_type == "sensor":
        return f"{value:.2f}"            # 소수점 2자리
    elif fmt_type == "count":
        return f"{int(value):,}"         # 천 단위 콤마
    elif fmt_type == "probability":
        return f"{value:.1%}"            # 확률 → 퍼센트
```

- 불량률: `12.3%`
- 센서값: `98.76`
- 생산량: `1,234`
- 예측 확률: `87.5%`

## 차트 크기 기준

| 위치 | 최소 높이 | 권장 높이 |
|------|----------|----------|
| KPI 카드 행 | — | st.metric 기본 |
| 센서 게이지 | 180px | 200px |
| 메인 추세 차트 | 250px | 300px |
| SHAP 바 차트 | 300px | 400px |
| 히스토리 테이블 | 200px | 350px |

반응형: `use_container_width=True` 항상 적용.
모바일 대응: `st.columns([1])` 단일 컬럼으로 폴백 (태블릿 세로 방향 가정).
