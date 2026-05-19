# assets/ — 시각 자산 통합 보관

> 정책: **루트나 docs/ 에 이미지·캡처를 두지 않는다.** 모두 이 폴더로 모은다.

## 하위 폴더 구조

```
assets/
├── screenshots/   ← 시연·발표용 화면 캡처 (사용자가 보관)
├── diagrams/      ← 아키텍처·플로우 다이어그램 (build_pptx 생성물 포함)
├── icons/         ← 페이지·KPI 아이콘 (사용 시)
└── exports/       ← 한글 폰트 적용된 차트 export
```

## 한글 깨짐 방지

기존 캡처·생성 이미지에 한글 깨짐이 발생했음. 향후 다음 규칙을 따른다.

1. **matplotlib** 사용 시 — 진입점에서 `setup_korean_font()` 호출
   - Windows: Malgun Gothic
   - macOS: AppleGothic
   - Linux (Streamlit Cloud): NanumGothic — `packages.txt` 의 `fonts-nanum` 설치 필요
2. **Streamlit screenshot** 캡처 시 — 브라우저 폰트가 한글 지원하는지 확인
3. **PPTX 슬라이드** 캡처 시 — 한국어 글꼴이 시스템에 설치돼 있는지 확인 (맑은 고딕 권장)

## 명명 규칙

- 페이지 캡처: `screenshots/p1_dashboard_20260521.png` (페이지 + 일자)
- 다이어그램: `diagrams/arch_v2.svg` (의미명 + 버전)
- 차트 export: `exports/shap_top15_demo.png` (출처 + 용도)

## .gitignore 정책

이 폴더 안의 `.png/.jpg/.svg` 는 git에 포함 (작은 파일들).
영상(`.mp4` 등)은 `.gitignore` 처리 (USB 별도 보관).
