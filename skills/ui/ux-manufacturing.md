# UX: Manufacturing Floor

## 핵심 원칙

QC 매니저는 데이터 분석 비전문가다. 대시보드는 "이 배치 괜찮나?" 한 가지 질문에 5초 안에 답해야 한다.

## 1. 터치 타깃 크기

- **최소 44×44px** (Apple HIG / WCAG 2.5.5 기준)
- 버튼 padding: 최소 `12px 20px`
- 버튼 간 간격: 최소 8px (실수로 인접 버튼 누르지 않도록)
- 드롭다운, 슬라이더: Streamlit 기본보다 크게 → CSS로 height 증가

```python
# CSS 오버라이드 예시
st.markdown("""
<style>
.stButton > button {
    min-height: 48px;
    font-size: 16px;
    padding: 12px 24px;
}
.stSelectbox > div {
    min-height: 48px;
}
</style>
""", unsafe_allow_html=True)
```

## 2. 고대비 시인성

공장 현장: 밝은 형광등 + 반사, 먼지, 안전장비 착용 상태에서 사용.

- **배경**: 흰색 (`#FFFFFF`) 또는 연회색 (`#F5F5F5`) — 어두운 테마 금지
- **텍스트 대비비**: 최소 4.5:1 (WCAG AA)
  - 주요 수치: `#212121` on white → 대비비 16:1 ✓
  - 경고 텍스트: `#E65100` (진한 오렌지) on white → 대비비 5:1 ✓
- **색상만으로 정보 전달 금지**: 아이콘 또는 텍스트 레이블 항상 병기
  - 나쁜 예: 빨간 숫자만
  - 좋은 예: 🔴 `위험` + 빨간 숫자

## 3. 3-레벨 색상 코딩 일관성

모든 화면에서 동일한 색상 의미 유지. 예외 없음.

| 상태 | 색상 | 텍스트 레이블 | 아이콘 |
|------|------|-------------|--------|
| 정상 | `#2E7D32` (녹색) | "정상" | ● 또는 ✓ |
| 경고 | `#F57F17` (황색) | "경고" | ⚠ |
| 위험 | `#C62828` (적색) | "위험" | 🔴 또는 ✕ |

혼용 금지: 중간 단계(주황, 노랑-초록 등) 추가하지 않음. 3단계 고정.

## 4. 최소 텍스트, 최대 시각 지표

- KPI 레이블: 최대 6자 (한글 기준)
  - 나쁜 예: "금일 총 생산 완료 수량"
  - 좋은 예: "생산량"
- 설명 텍스트는 접기(expander)로 숨김: `st.expander("상세 설명")`
- 숫자 글자 크기: KPI는 최소 32px, 센서값은 최소 20px

## 5. 2m 거리 가독성 (Status-at-a-Glance)

P1 Dashboard는 벽면 모니터에 항상 켜져 있다고 가정.

- 전체 상태를 나타내는 **대형 상태 배너** (화면 상단 1/4):
  ```python
  def overall_status_banner(status: str):
      colors = {"정상": "#2E7D32", "경고": "#F57F17", "위험": "#C62828"}
      labels = {"정상": "✓ 정상 운영", "경고": "⚠ 주의 필요", "위험": "✕ 즉시 조치"}
      st.markdown(
          f'<div style="background:{colors[status]};color:white;'
          f'text-align:center;padding:20px;font-size:32px;font-weight:bold;'
          f'border-radius:8px">{labels[status]}</div>',
          unsafe_allow_html=True
      )
  ```
- KPI 숫자: `font-size: 40px` 이상 (st.metric CSS override)
- 색상 구역이 2m에서 구분 가능해야 함 → 게이지 zone 폭 최소 20% 이상

## 6. 글러브 친화적 인터페이스

- 드래그 인터랙션 최소화 (슬라이더 주의 — 날짜는 date_input 선호)
- 탭 선택: `st.tabs()` 보다 `st.radio(horizontal=True)` 선호 (터치 영역 큼)
- 스크롤: 페이지 스크롤은 허용, 내부 스크롤 컨테이너는 충분한 높이 확보

## 7. 시각적 알림 우선 (청각적 알림 없음)

공장 소음 환경 → 오디오 알림은 들리지 않음.

- 위험 알림: 빨간 배너 + 깜빡임 효과
  ```python
  # CSS 애니메이션 (위험 상태)
  if status == "위험":
      st.markdown("""
      <style>
      @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
      .danger-banner { animation: blink 1.5s infinite; }
      </style>
      """, unsafe_allow_html=True)
  ```
- 알림 패널: 항상 사이드바 상단에 고정 노출
- 새 알림 발생 시 `st.rerun()` 즉시 호출

## 체크리스트 (UX 검토 시 사용)

- [ ] 모든 버튼 최소 44×44px
- [ ] 색상+텍스트 병기 (색상만 단독 사용 없음)
- [ ] 3-레벨 색상 코딩 일관성 확인
- [ ] P1 배너 2m에서 식별 가능
- [ ] KPI 숫자 32px 이상
- [ ] 드래그 없는 원클릭 조작 가능
- [ ] 알림 시각적으로 즉시 인지 가능
