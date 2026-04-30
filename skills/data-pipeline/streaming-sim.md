# Streaming Simulator

## 목적
실시간 공장 센서 데이터 스트리밍을 시뮬레이션하여 대시보드 데모에 활용.
실제 IoT 수신 없이 UCI SECOM 데이터를 샘플링하여 "실시간" 처리 흐름을 재현.

---

## 1. 시나리오 종류

| 시나리오 | 설명 | 데이터 소스 |
|----------|------|-------------|
| Normal | 정상 제품 랜덤 샘플링 | SECOM Pass 샘플 (label=0) |
| Abnormal | 불량 패턴 주입 | SECOM Fail 샘플 (label=1) |
| Mixed | 정상 중 불량 간헐적 삽입 | 비율 조절 가능 (기본 10%) |

---

## 2. 핵심 구현

### 스트림 초기화
```python
import streamlit as st
import time
import pandas as pd
import numpy as np

def init_stream(df_pass, df_fail):
    """st.session_state에 스트림 상태 초기화"""
    if 'stream_active' not in st.session_state:
        st.session_state.stream_active = False
        st.session_state.stream_buffer = []   # 수신된 샘플 이력
        st.session_state.stream_step   = 0    # 현재 스텝
        st.session_state.df_pass = df_pass
        st.session_state.df_fail = df_fail
```

### 샘플 생성기
```python
def generate_sample(scenario: str, fail_ratio: float = 0.10) -> dict:
    """
    scenario: 'normal' | 'abnormal' | 'mixed'
    Returns: {'data': Series, 'true_label': int, 'timestamp': datetime}
    """
    df_pass = st.session_state.df_pass
    df_fail = st.session_state.df_fail

    if scenario == 'normal':
        row = df_pass.sample(1).iloc[0]
        label = 0
    elif scenario == 'abnormal':
        row = df_fail.sample(1).iloc[0]
        label = 1
    else:  # mixed
        label = 1 if np.random.random() < fail_ratio else 0
        row = df_fail.sample(1).iloc[0] if label == 1 else df_pass.sample(1).iloc[0]

    return {
        'data':       row,
        'true_label': label,
        'timestamp':  pd.Timestamp.now(),
    }
```

### 스트림 루프 (Streamlit)
```python
BATCH_INTERVAL = 3  # 초 단위

def run_stream(scenario: str, model, preprocessor):
    """Streamlit 메인 루프에서 호출"""
    placeholder = st.empty()

    while st.session_state.stream_active:
        sample = generate_sample(scenario)

        # 전처리 → 예측
        X = preprocessor.transform(sample['data'].values.reshape(1, -1))
        pred_proba = model.predict_proba(X)[0][1]
        pred_label = int(pred_proba >= 0.5)

        # 버퍼에 추가
        st.session_state.stream_buffer.append({
            'step':       st.session_state.stream_step,
            'timestamp':  sample['timestamp'],
            'pred_proba': pred_proba,
            'pred_label': pred_label,
            'true_label': sample['true_label'],
        })
        st.session_state.stream_step += 1

        # 실시간 디스플레이 갱신
        with placeholder.container():
            _render_stream_ui()

        time.sleep(BATCH_INTERVAL)
```

---

## 3. 스트림 UI 컴포넌트

```python
def _render_stream_ui():
    """스트림 현황 실시간 표시"""
    buf = pd.DataFrame(st.session_state.stream_buffer[-20:])  # 최근 20개

    col1, col2, col3 = st.columns(3)
    col1.metric("총 검사 수",  len(st.session_state.stream_buffer))
    col2.metric("불량 탐지 수", int(buf['pred_label'].sum()))
    col3.metric("최근 불량 확률", f"{buf['pred_proba'].iloc[-1]:.2%}")

    # 불량 확률 추이 차트
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=buf['step'], y=buf['pred_proba'],
        mode='lines+markers',
        line=dict(color='red' if buf['pred_proba'].iloc[-1] > 0.5 else 'green'),
    ))
    fig.add_hline(y=0.5, line_dash='dash', line_color='orange',
                  annotation_text='판정 임계값')
    st.plotly_chart(fig, use_container_width=True)
```

---

## 4. Streamlit 제어 버튼

```python
# 메인 페이지에서 사용
scenario = st.selectbox("시나리오", ['normal', 'abnormal', 'mixed'])

col_start, col_stop = st.columns(2)
with col_start:
    if st.button("스트림 시작"):
        st.session_state.stream_active = True
        run_stream(scenario, model, preprocessor)
with col_stop:
    if st.button("스트림 중지"):
        st.session_state.stream_active = False
```

---

## 5. 불량 패턴 주입 (Advanced)

```python
def inject_failure_pattern(base_sample: pd.Series, intensity: float = 1.5) -> pd.Series:
    """
    정상 샘플에 불량 패턴을 인위적으로 주입
    intensity: 주입 강도 (1.0=원본, 2.0=2배 편차)
    """
    noisy = base_sample.copy()
    # 분산이 큰 상위 20개 센서에 노이즈 추가
    top_var_cols = base_sample.nlargest(20).index
    noisy[top_var_cols] *= intensity
    return noisy
```

---

## 주의사항
- `time.sleep()` → Streamlit에서 UI 블로킹 가능 → `st.spinner` 또는 `st.empty` 활용
- 버퍼 크기 제한: 최대 500개 유지 (메모리 관리)
- 실제 배포 시 `asyncio` 또는 별도 스레드로 교체 고려
