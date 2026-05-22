# v1 — 첫 정상 배포 캡처 (대기 중)

> **발행 트리거**: P-B/PR-1 hotfix 머지 후 Streamlit Cloud 재배포 정상 진입
> **담당**: Claude 또는 Codex (단순 캡처는 Codex 5.4 적합)
> **상태**: ⏳ 대기

## 채워야 할 캡처 (5종)

| # | 파일명 | 페이지 | 검증 포인트 |
|---|---|---|---|
| 01 | `01_main_dummy.png` | `app/app.py` (메인) | 사이드바 🟡 dummy 배지, KPI 4종 정상 |
| 02 | `02_p1_realtime.png` | `pages/1_📊_실시간_예측.py` | 센서 슬라이더 + 즉시 판정 |
| 03 | `03_p2_shap.png` | `pages/2_🔍_원인_분석.py` | SHAP Waterfall + Top 5 센서 |
| 04 | `04_p3_action.png` | `pages/3_🛠_조치_가이드.py` | 원클릭 수용 + 액션 카드 |
| 05 | `05_p4_history.png` | `pages/4_📜_이력_조회.py` | 시계열 + 필터 |

## 캡처 방법 (둘 중 택1)

### A. 로컬 (빠름)
```powershell
cd smart-factory-hackathon
$env:PYTHONIOENCODING="utf-8"
streamlit run app/app.py
# 브라우저에서 5페이지 순회, 각 페이지 캡처
```

### B. Streamlit Cloud (실배포 검증)
- 배포 URL 접속
- 5페이지 순회 캡처
- 콘솔 에러도 같이 캡처 (있다면)

## 캡처 후 체크리스트

- [ ] 파일명 규칙 준수 (`{NN}_{page-slug}.png`)
- [ ] 1920×1080 또는 1440×900 (Retina 가능)
- [ ] 한글 깨짐 없음 (있다면 P-C 폰트 점검 필수)
- [ ] `notes.md` 작성 (캡처 시각·환경·관찰점)
- [ ] `../INDEX.md` 의 v1 행 "_대기_" → 실제 발행일로 갱신
- [ ] (PR-4 머지 후) `../../dashboard/data.json` 자동 갱신

## v0와의 차이

- v0: 발표 슬라이드용 PPTX export + P-A QA
- v1: **첫 정상 배포 화면** — 실제 라이브 시스템 상태 보존
