# 2026 스마트 공장 운영 시스템 MVP 개발 해커톤

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 주제 | AI 기반 스마트 공장 운영 시스템 MVP 개발 |
| 프로젝트명 | QualityLens |
| 핵심 방향 | 공정 이상 예측, 원인 분석, 조치 가이드를 하나의 플랫폼으로 연결 |
| 제출 기한 | 예선 ~ 2026.05.13(월) 10:00 |
| 본선 | 2026.05.22(금) 오프라인 구현 및 발표 |

## 한 줄 소개

**QualityLens는 공정 센서 데이터를 기반으로 이상 징후를 미리 예측하고, 원인을 설명하고, 바로 실행할 조치까지 제안하는 AI 스마트 공장 운영 플랫폼입니다.**

## 핵심 문제 정의

- 제조 현장에서는 이상 징후를 늦게 발견하거나, 발견해도 원인을 바로 파악하지 못해 손실이 커집니다.
- 단순 예측 모델만으로는 현장 의사결정에 바로 연결되기 어렵습니다.
- 따라서 예측, 설명, 조치를 하나로 묶은 운영형 MVP가 필요합니다.

## 핵심 해결 방식

QualityLens는 `Predict → Explain → Act` 구조로 동작합니다.

- `Predict`: XGBoost로 공정 이상 여부를 예측합니다.
- `Explain`: SHAP으로 어떤 센서와 공정 변수가 이상에 영향을 주었는지 설명합니다.
- `Act`: Threshold Engine과 조치 가이드를 결합해 현장 작업자가 바로 실행할 수 있는 권고안을 제시합니다.

## 평가 기준 대응

| 평가 항목 | 대응 포인트 |
|------|------|
| 문제 정의 | 이상 발견 지연과 원인 파악 지연으로 생기는 현장 손실을 구체적으로 정의 |
| AI 활용 | XGBoost, SHAP, Threshold Engine을 결합해 AI가 실제 의사결정에 기여하도록 설계 |
| 플랫폼 기획 | 예측, 설명, 조치가 이어지는 사용자 흐름과 데이터 흐름을 함께 구성 |
| MVP 구현 완성도 | Streamlit 기반 5개 화면으로 실제 시연 가능한 범위를 정의 |
| 발표/전달력 | 5분 내 설명 가능한 흐름과 데모 시나리오를 사전 설계 |

## MVP 구성

| 페이지 | 역할 | 상태 |
|------|------|------|
| P1 | 통합 대시보드 | 핵심 |
| P2 | 실시간 예측 | 핵심 |
| P3 | 원인 분석 | 핵심 |
| P4 | 조치 가이드 | 핵심 |
| P5 | 이력 조회 | 선택 |

## 관련 문서

- [프로젝트 Summary 초안](docs/project_summary.md)
- [PPT 시각화 가이드](docs/ppt_visual_guide.md)
- [본선 준비 Spec](docs/spec_finals_prep.md) ⭐ 본선 D-3 작성
- [본선 준비 로드맵 HTML](docs/roadmap.html) ⭐ 진행 추적용

### 스킬 카테고리

| 카테고리 | 역할 |
|------|------|
| [data-pipeline](skills/data-pipeline/INDEX.md) | Stage 1 — 데이터 전처리 |
| [modeling](skills/modeling/INDEX.md) | Stage 2 — XGBoost 학습/평가 |
| [xai](skills/xai/INDEX.md) | Stage 3 — SHAP 원인 분석 |
| [ui](skills/ui/INDEX.md) | Stage 4 — UI 구조 |
| [quality](skills/quality/INDEX.md) | Stage 5 — 완성도/발표 전략 |
| [codex-bridge](skills/codex-bridge/INDEX.md) ⭐ | 본선 — Claude↔Codex 라우팅 |
| [streamlit-build](skills/streamlit-build/INDEX.md) ⭐ | 본선 — Streamlit 5페이지 구현 |
| [demo-script](skills/demo-script/INDEX.md) ⭐ | 본선 — 5분 발표·시연 설계 |

## 구현/제작 파일

- `QualityLens_기획서.pptx`: 예선 제출용 발표 자료
- `QualityLens_기획서.pdf`: 제출용 PDF
- `build_pptx_v4.py`: PPT 자동 생성 스크립트
- `diagrams/`: 아키텍처 및 흐름도 이미지

## 권장 진행 순서

1. `docs/project_summary.md`를 먼저 확정
2. `docs/ppt_visual_guide.md` 기준으로 슬라이드 메시지 정리
3. PPTX에 필요한 시각화만 추가
4. PDF로 변환 후 제출
