# Interaction

## 실시간 갱신 (Auto-refresh)

```python
# P1 Dashboard 상단 — 갱신 설정 UI
col1, col2 = st.columns([3, 1])
with col2:
    interval = st.selectbox("갱신 주기", [10, 30, 60, 0], index=1,
                            format_func=lambda x: "수동" if x == 0 else f"{x}초")
    st.session_state['refresh_interval'] = interval

# 자동 갱신 루프
if interval > 0:
    time.sleep(interval)
    st.rerun()
```

수동 갱신 버튼도 항상 노출: `st.button("새로고침 🔄")` → `st.rerun()`

## 드릴다운: KPI → 상세 페이지

Streamlit에서 페이지 간 직접 이동은 `st.switch_page()` (1.28+) 사용.

```python
# P1 — 불량률 KPI 카드 클릭 → P2로 이동
if st.button("불량률 상세 →", key="drilldown_defect"):
    st.switch_page("pages/2_Predict.py")

# P2 — 예측 결과 클릭 → P3 설명으로 이동
if st.button("AI 설명 보기 →", key="drilldown_explain"):
    st.switch_page("pages/3_Explain.py")
```

드릴다운 연결:
- P1 불량률 → P2 Predict
- P1 알림 클릭 → P4 Act
- P2 예측 결과 → P3 Explain
- P3 설명 → P4 Act (권고 액션)

## 원클릭 액션 수락

```python
# P4 Act — 액션 카드
def action_card(action: dict):
    with st.container():
        st.markdown(f"### {action['title']}")
        st.markdown(action['description'])
        st.caption(f"예상 효과: {action['expected_impact']}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("수락", key=f"accept_{action['id']}", type="primary"):
                record = {
                    "action_id": action['id'],
                    "title": action['title'],
                    "ts": datetime.now().isoformat(),
                    "user": "QC Manager",
                }
                st.session_state['action_history'].append(record)
                st.success(f"✓ 조치 수락됨: {action['title']}")
                st.rerun()
        with col2:
            if st.button("건너뜀", key=f"skip_{action['id']}"):
                st.info("이 조치를 건너뜁니다.")
```

수락 후 확인 메시지는 3초 후 자동으로 사라지지 않음 — `st.success` 유지로 명확한 피드백.

## 필터

### 날짜 범위
```python
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", value=datetime.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("종료일", value=datetime.today())
```

### 배치 ID
```python
batch_id = st.text_input("배치 ID 검색", placeholder="예: BATCH-2024-001")
```

### 센서 그룹
```python
sensor_group = st.multiselect("센서 그룹", ["온도", "압력", "습도", "진동"],
                               default=["온도", "압력"])
```

### 심각도 레벨
```python
severity = st.radio("심각도", ["전체", "위험", "경고", "정상"],
                    horizontal=True, index=0)
```

필터는 P5 History에서 전부 노출. P1은 날짜 범위만.

## 반응형 레이아웃 고려사항

- 기본 레이아웃: `st.set_page_config(layout="wide")`
- KPI 카드: `st.columns(4)` → 태블릿에서 자동 축소됨 (Streamlit 내장)
- 센서 게이지 그리드: `st.columns(3)` 최대
- 사이드바 기본 상태: 접힘 가능하나 데스크탑에서는 펼쳐두기
- 최소 해상도 가정: 1280×768 (공장용 터치 모니터 기준)
