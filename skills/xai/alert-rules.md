# Alert Rules

## 역할
XGBoost 예측 결과의 fail_probability를 기반으로 3단계 알림 레벨을 정의하고,
공장 현장에서 즉시 인지 가능한 시각적/청각적 알림 규칙을 명세한다.

---

## 트리거 조건 (3단계)

| 레벨 | 이름 | fail_probability | 아이콘 | 색상 |
|------|------|-----------------|--------|------|
| Level 1 | Info | 30% ~ 50% | ℹ️ | 초록 `#38A169` |
| Level 2 | Warning | 50% ~ 70% | ⚠️ | 노랑 `#D69E2E` |
| Level 3 | Danger | 70%+ | 🚨 | 빨강 `#E53E3E` |

- 30% 미만: 정상 → 알림 미생성
- 색상은 `ui/chart-style.md`의 신호등 팔레트와 동일

---

## 알림 메시지 포맷

```
{severity_icon} [{timestamp}] 배치 {batch_id} — {message}
```

예시:
```
⚠️ [2026-04-30 14:23:11] 배치 #B-0042 — 불량 확률 63% 감지, 압력 불안정 주의
🚨 [2026-04-30 14:31:05] 배치 #B-0051 — 불량 확률 91% 감지, 다중 센서 이상 (즉시 조치 필요)
ℹ️ [2026-04-30 14:35:48] 배치 #B-0055 — 불량 확률 38%, 모니터링 강화 권고
```

### 메시지 생성 규칙

```python
SEVERITY_ICONS = {
    "info":    "ℹ️",
    "warning": "⚠️",
    "danger":  "🚨"
}

def classify_alert(fail_prob):
    if fail_prob >= 0.70:
        return "danger",  "즉시 조치 필요"
    elif fail_prob >= 0.50:
        return "warning", "주의 요망"
    elif fail_prob >= 0.30:
        return "info",    "모니터링 강화 권고"
    return None, None

def build_alert(batch_id, fail_prob, action_summary=""):
    severity, suffix = classify_alert(fail_prob)
    if severity is None:
        return None
    icon = SEVERITY_ICONS[severity]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"불량 확률 {fail_prob*100:.0f}% 감지"
    if action_summary:
        msg += f", {action_summary}"
    msg += f" ({suffix})"
    return {
        "severity": severity,
        "icon": icon,
        "timestamp": ts,
        "batch_id": batch_id,
        "message": msg,
        "fail_probability": fail_prob
    }
```

---

## 알림 패널 규칙

```python
# st.session_state["alert_log"]: list[dict], 시간 내림차순 유지
MAX_ALERTS = 20

def add_alert(alert_obj):
    log = st.session_state.setdefault("alert_log", [])
    log.insert(0, alert_obj)              # 최신 항목을 앞에 추가
    st.session_state["alert_log"] = log[:MAX_ALERTS]   # 최대 20건 유지
```

### 패널 렌더링 (Streamlit)
```python
def render_alert_panel():
    st.subheader("알림 로그")
    for alert in st.session_state.get("alert_log", []):
        color_map = {"danger": "error", "warning": "warning", "info": "info"}
        fn = getattr(st, color_map[alert["severity"]])
        fn(f"{alert['icon']} [{alert['timestamp']}] 배치 {alert['batch_id']} — {alert['message']}")
```

- 패널 위치: ui 사이드바 또는 메인 하단 고정 영역 (`ui/layout.md` 참조)
- 정렬: 시간 내림차순 (최신 알림 상단)
- 패널 높이: 고정 스크롤 영역 (`height=400px`)

---

## 시각적 강조 규칙

| 레벨 | 배경 강조 | 테두리 | 텍스트 굵기 |
|------|-----------|--------|-------------|
| Info | 연초록 배경 | 없음 | 보통 |
| Warning | 연노랑 배경 | 노랑 좌측 바 | 보통 |
| Danger | 연빨강 배경 | 빨강 좌측 바 | **굵게** |

- Danger 레벨: 배치 카드 전체 테두리 빨강 강조 (`ui/chart-style.md`의 `.card-danger` 클래스)
- 실시간 스트리밍 시뮬레이터 작동 중 Danger 발생 시: 화면 상단 배너 (`st.error()`) 추가 표시

---

## 공장 현장 알림 규칙

| 조건 | 동작 |
|------|------|
| Danger 신규 발생 | Streamlit `st.toast()` 팝업 (3초) + 알림 패널 자동 스크롤 최상단 |
| Warning 누적 3건+ | 사이드바 배지 카운터 증가 (빨강) |
| 조치 수락 시 | 해당 알림에 ✅ 마크 추가, `accepted_at` 타임스탬프 기록 |
| Info | 자동 팝업 없음 (패널 내 조용히 추가) |

### 사운드 알림 (선택적, 브라우저 지원 시)
```python
# Danger 발생 시 브라우저 알림음 (HTML Audio API)
DANGER_SOUND_JS = """
<script>
  const ctx = new AudioContext();
  const osc = ctx.createOscillator();
  osc.connect(ctx.destination);
  osc.frequency.setValueAtTime(880, ctx.currentTime);
  osc.start(); osc.stop(ctx.currentTime + 0.3);
</script>
"""
# st.components.html(DANGER_SOUND_JS) — 데모 환경에서 사용자 동의 후 활성화
```

- 공장 소음 환경 고려 → 시각 알림 우선, 사운드는 옵션
- 데모 발표 시: 사운드 비활성화 기본값 (`SOUND_ENABLED = False`)

---

## 알림 초기화

```python
# 세션 리셋 또는 새 시뮬레이션 시작 시
if st.button("알림 초기화"):
    st.session_state["alert_log"] = []
    st.session_state["action_history"] = []
    st.rerun()
```
