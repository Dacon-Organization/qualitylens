# Dashboard Components

## KPI Card

Streamlit `st.metric` 래퍼. 색상 오버라이드는 CSS injection으로 처리.

```python
def kpi_card(label: str, value: str, delta: str = None, status: str = "normal"):
    """
    status: "normal" | "warning" | "danger"
    """
    color_map = {"normal": "#2E7D32", "warning": "#F57F17", "danger": "#C62828"}
    st.metric(label=label, value=value, delta=delta)
    # CSS로 delta 색상 덮어쓰기
    inject_status_color(status, color_map[status])
```

사용처: P1 상단 KPI 행 (불량률, 가동률, 오늘 생산량, 활성 알림 수)

## Sensor Gauge

Plotly `go.Indicator` (gauge 모드). 3-zone 색상 고정.

```python
def sensor_gauge(name: str, value: float, ranges: dict) -> go.Figure:
    """
    ranges: {"normal": (0, 80), "warning": (80, 90), "danger": (90, 100)}
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": name, "font": {"size": 16}},
        gauge={
            "axis": {"range": [ranges["normal"][0], ranges["danger"][1]]},
            "bar": {"color": get_zone_color(value, ranges)},
            "steps": [
                {"range": list(ranges["normal"]), "color": "#E8F5E9"},
                {"range": list(ranges["warning"]), "color": "#FFF8E1"},
                {"range": list(ranges["danger"]), "color": "#FFEBEE"},
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(t=40, b=10, l=20, r=20))
    return fig
```

사용처: P1 센서 현황 그리드, P2 입력값 확인

## Alert Panel

스크롤 가능한 알림 목록. severity별 아이콘과 배경색.

```python
SEVERITY_CONFIG = {
    "danger":  {"icon": "🔴", "bg": "#FFEBEE", "label": "위험"},
    "warning": {"icon": "🟡", "bg": "#FFF8E1", "label": "경고"},
    "info":    {"icon": "🔵", "bg": "#E3F2FD", "label": "정보"},
}

def alert_panel(alerts: list, max_height: int = 300):
    with st.container():
        st.markdown(f'<div style="max-height:{max_height}px;overflow-y:auto">', unsafe_allow_html=True)
        for alert in sorted(alerts, key=lambda x: x["severity"]):
            cfg = SEVERITY_CONFIG[alert["severity"]]
            st.markdown(
                f'<div style="background:{cfg["bg"]};padding:8px 12px;margin:4px 0;border-radius:6px">'
                f'{cfg["icon"]} <b>{cfg["label"]}</b> — {alert["msg"]}'
                f'<br><small>{alert["ts"]}</small></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
```

사용처: P1 우측 패널, P4 액션 목록 상단

## History Table

```python
def history_table(df: pd.DataFrame, filters: dict = None):
    """
    filters: {"date_range": (start, end), "batch_id": str, "severity": str}
    """
    if filters:
        df = apply_filters(df, filters)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("시각", format="YYYY-MM-DD HH:mm"),
            "probability": st.column_config.ProgressColumn("불량 확률", min_value=0, max_value=1),
            "severity": st.column_config.TextColumn("등급"),
        },
        hide_index=True,
    )
```

사용처: P5 이력 조회

## Batch Selector

```python
def batch_selector(batch_ids: list) -> str:
    """배치 ID 드롭다운. 최신 배치 기본 선택."""
    return st.selectbox(
        "배치 선택",
        options=batch_ids,
        index=0,
        key="selected_batch",
        help="분석할 생산 배치를 선택하세요"
    )
```

슬라이더 대안: 배치가 시계열 순서일 때 `st.slider` 사용.

## 공통 유틸리티 (`utils/components.py`)

- `inject_css(css: str)` — `st.markdown(..., unsafe_allow_html=True)` 래퍼
- `status_badge(label, status)` — 색상 뱃지 HTML 반환
- `get_zone_color(value, ranges)` — 값→ 색상 매핑
- `apply_filters(df, filters)` — DataFrame 필터 적용
- `format_number(value, fmt)` — 한국어 로케일 숫자 포맷
