> **Pipeline Position**: Stage 4 — Act (UI Layer)
> **Input**: 모든 Stage의 결과물 (데이터, 모델, SHAP, 알림)
> **Output**: Streamlit 멀티페이지 대시보드
> **Downstream**: quality/ (Stage 5)
> **Recommended model**: `sonnet` — 컴포넌트 조합, 레이아웃은 규칙 기반

## 파일 목록

| 파일 | 역할 |
|------|------|
| `page-structure.md` | 5페이지 아키텍처, 세션 상태, 페이지 간 데이터 흐름 |
| `dashboard-components.md` | KPI 카드, 센서 게이지, 알림 패널 등 재사용 컴포넌트 |
| `chart-style.md` | 컬러 팔레트, Plotly 차트 타입, 숫자 포맷 규칙 |
| `interaction.md` | 실시간 갱신, 드릴다운, 원클릭 액션, 필터 |
| `ux-manufacturing.md` | 제조 현장 UX 원칙, 터치 타깃, 가독성 기준 |

## 빌드 순서

1. `page-structure.md` — 페이지/세션 설계 확정
2. `dashboard-components.md` — 공통 컴포넌트 구현
3. `chart-style.md` — 스타일 적용
4. `interaction.md` — 인터랙션 레이어 추가
5. `ux-manufacturing.md` — UX 검토 체크리스트

## 의존성

- **Upstream**: modeling/ (XGBoost 모델), xai/ (SHAP 값), data-pipeline/ (센서 데이터)
- **Downstream**: quality/ (테스트, 배포, 데모)
