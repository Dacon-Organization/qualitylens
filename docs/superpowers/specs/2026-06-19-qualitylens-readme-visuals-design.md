# QualityLens README 시각 자료 개편 디자인

## 배경

현재 `smart-factory-hackathon/README.md`는 프로젝트의 문제 정의와 기술 설명을
충분히 담고 있지만, 첫 화면에 프로젝트를 대표하는 이미지가 없고 일부 페이지
구성이 본선 당시 최종 앱과 다르다. 기존 GPT 생성 시안은 시각적 완성도는 높지만
실제 Streamlit 앱에 없는 화면과 지표를 포함해 포트폴리오 신뢰도를 떨어뜨릴 수
있다.

본선 참가 인증서는 예선 통과와 2026년 5월 22일 본선 참가를 증명한다. 수상
증빙은 아니므로 README에는 `예선 통과 · 본선 참가 · 수상 없음`을 명시한다.

## 목표

- 기존 README의 프로젝트 설명, 기술 근거, 실행 방법을 유지한다.
- README 첫 화면에 실무 포트폴리오 수준의 썸네일을 배치한다.
- 실제 코드와 배포 앱에 일치하는 시스템 구성도를 추가한다.
- AI가 다시 그린 UI 대신 실제 배포 앱 캡처를 사용한다.
- 본선 참가와 미수상 사실을 과장 없이 기록한다.
- 본선 참가 인증서 원본을 별도 폴더에 보관한다.
- 본선에서 실제 사용한 최종 발표 PDF를 원본 그대로 보관하고 README에 연결한다.

## 비목표

- Streamlit 앱 기능이나 UI를 변경하지 않는다.
- 모델을 재학습하거나 SHAP 값을 다시 계산하지 않는다.
- 수상, 입상, 우수작 선정과 같은 확인되지 않은 표현을 사용하지 않는다.
- 인증서 이미지를 README 본문에 직접 표시하지 않는다.

## 선택한 시각 전략

사용자는 썸네일과 시스템 구성도 모두 C 하이브리드 방식을 승인했다.

### 썸네일

GPT Image 2.0은 스마트 공장 분위기의 배경만 생성한다. 실제 QualityLens 화면은
배포 앱에서 새로 캡처하고, 생성 배경 위에 브라우저 프레임 형태로 합성한다.
앱 캡처의 메뉴, 텍스트, 수치, 차트는 변형하지 않는다.

썸네일 고정 문구는 다음과 같다.

- `QualityLens`
- `AI 기반 스마트 공장 운영 시스템`
- `Predict → Explain → Act`
- `XGBoost · SHAP · Threshold Engine · SPC/Pareto`

### 시스템 구성도

GPT Image 2.0은 밝은 청색 계열의 산업 기술 배경과 비언어적 장식 요소만
생성한다. 구성 요소 이름, 연결선, 설명 텍스트는 HTML/CSS 또는 SVG로 그린 뒤
PNG로 렌더링한다. 이 방식으로 한글 오류와 존재하지 않는 구성 요소 생성을
방지한다.

구성도는 다음 흐름을 표현한다.

1. 데이터: UCI SECOM, 사용자 CSV, 결정론 데모
2. 오프라인 파이프라인: 전처리, XGBoost K-Fold 학습, SHAP 사전 계산,
   Threshold Engine
3. 아티팩트: 전처리 데이터, XGBoost 모델, threshold 표, SHAP 결과,
   데모 결과, 조치 이력
4. Streamlit 앱: Home, P0 데이터 업로드, P1 실시간 예측, P2 원인 분석,
   P3 조치 가이드, P4 이력 조회, P5 SPC/Pareto, P6 종합 대시보드
5. 사용자와 배포: 현장 작업자, 공정팀/QC, 생산관리자, 경영진,
   Streamlit Community Cloud

하단 핵심 흐름은 `CSV 업로드 → Predict → Explain → Act → 이력 · SPC 개선`으로
고정한다.

## 실제 화면 캡처

배포 주소 `https://qualitylens-smart-factory.streamlit.app/`에서 데모 모드 기준으로
다음 화면을 캡처한다.

- 메인 대시보드
- 원인 분석
- 조치 가이드
- SPC/Pareto

온보딩 모달과 Streamlit 관리 메뉴는 닫고, 각 화면의 핵심 콘텐츠가 보이는
일관된 16:9 뷰포트로 캡처한다. 썸네일에는 메인 대시보드 캡처를 사용한다.

## README 정보 구조

1. 하이브리드 썸네일
2. 라이브 앱 링크와 기술 스택 배지
3. 대회 결과: 예선 통과, 본선 참가, 수상 없음
4. 기존 프로젝트 개요와 한 줄 소개
5. Predict → Explain → Act 핵심 가치
6. 시스템 구성도
7. 실제 화면 미리보기
8. 기존 문제 정의, 차별화, 페르소나, 4영역 통합, 평가 기준 대응
9. 실제 Home + P0~P6 페이지 구성
10. 실행 방법, 실데이터, 검증 산출물, 관련 문서
11. 본선 참가 증빙 파일을 여는 텍스트 링크

현재 설명은 삭제하지 않는다. 다만 다음 사실 오류는 교정한다.

- `2026.05.13(월)`을 실제 요일인 `2026.05.13(수)`로 수정
- `5개 화면`을 실제 `Home + P0~P6` 구조로 수정
- 존재하지 않는 `build_pptx_v4.py`와 `diagrams/` 설명을 실제 파일 및
  새 README 자산 경로로 수정
- 근거가 없는 `1/100 가격` 표현은 저비용 Streamlit MVP 배포라는 같은 취지의
  검증 가능한 문장으로 완화

## 파일 구조

```text
smart-factory-hackathon/
├── README.md
├── assets/readme/
│   ├── qualitylens-hero.png
│   ├── qualitylens-architecture.png
│   ├── qualitylens-hero-background.png
│   ├── qualitylens-architecture-background.png
│   ├── screens/
│   │   ├── main-dashboard.png
│   │   ├── root-cause-analysis.png
│   │   ├── action-guide.png
│   │   └── spc-pareto.png
│   └── sources/
│       ├── qualitylens-hero.html
│       └── qualitylens-architecture.html
├── docs/certificates/
│   └── 2026-smart-factory-finals-participation.pdf
└── docs/presentation/final/
    └── qualitylens-finals-presentation.pdf
```

## 생성 및 합성 규칙

- 새 이미지는 기존 두 시안을 덮어쓰지 않고 새 파일명으로 저장한다.
- GPT Image 2.0 출력에는 한글 문구, 앱 UI, 수치, 로고를 생성시키지 않는다.
- 실제 앱 캡처와 모든 텍스트는 결정론적 합성 단계에서 추가한다.
- 썸네일과 구성도는 16:9 PNG로 출력한다.
- README에는 상대 경로를 사용하고 이미지 대체 텍스트를 제공한다.
- 원본 인증서는 파일명을 ASCII로 정규화하되 내용을 수정하지 않는다.
- 인증서는 README에 이미지로 삽입하지 않고 `본선 참가 증빙` 텍스트 링크로만
  연결한다.

## 검증

- 실제 앱 캡처는 생성형 편집 없이 직접 래스터 레이어로 축소·배치하고,
  합성 결과에서 메뉴·텍스트·수치를 원본과 대조한다.
- 구성도 레이블을 코드와 배포 앱의 페이지 목록에 대조한다.
- README의 모든 상대 링크와 이미지 경로가 존재하는지 확인한다.
- Markdown 렌더링을 확인해 이미지 비율, 표, 코드 블록이 깨지지 않는지 검사한다.
- 인증서 PDF의 체크섬을 복사 전후로 비교한다.
- 최종 발표 PDF의 17개 페이지를 렌더링하고 복사 전후 체크섬을 비교한다.
- `git diff --check`로 공백 오류를 확인하고 변경 파일만 선별해 스테이징한다.

## 오류 처리

- GPT 배경이 텍스트나 가상 UI를 포함하면 한 번의 타깃 수정으로 재생성한다.
- 실제 앱이 일시적으로 열리지 않으면 레포의 Playwright QA 캡처를 사용하되,
  README에 배포 앱 실시간 캡처라고 표기하지 않는다.
- 한글 렌더링이 깨지면 시스템의 한국어 지원 폰트를 확인하고 다시 렌더링한다.
- 인증서 또는 사용자 기존 변경 사항은 덮어쓰거나 되돌리지 않는다.
