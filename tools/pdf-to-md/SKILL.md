---
name: pdf-to-md
description: Zero-choice automatic PDF/PPTX to Markdown converter. Detects file type, layout, and language automatically, then selects the best tool (ODL, MinerU, docling, fitz, pptx-direct) and returns the highest-quality result. No user tool selection required.
---

# pdf-to-md: 자동 PDF/PPTX → Markdown 변환기

이 스킬은 **파일을 던지면 자동으로 최선의 도구를 선택해 변환**합니다. 사용자가 도구를 선택할 필요 없습니다.

## 사용 방법 (Claude용)

### Step 1: config 확인

```bash
cat ~/.pdf_to_md_config.json
```

없으면 → `python setup.py` 실행 안내 후 중단.

### Step 2: 변환 실행

```bash
python /path/to/pdf-to-md/convert.py "<파일경로>"
```

- PDF와 PPTX 모두 동일한 명령어
- 결과는 항상 원본 PDF/PPTX가 있는 폴더 아래 `markdown/`에 저장
- 변환 기록은 원본 PDF/PPTX가 있는 폴더 아래 `.reports/`에 저장
- `--output`을 지정하면 해당 폴더에 Markdown과 report를 함께 저장
- `--dry-run`: 변환 없이 어떤 도구가 선택될지만 확인

### Step 3: 결과 보고

변환 완료 후 한 줄 요약:

```
완료: <파일명>.md → <도구명> 선택 (신뢰도: normal | low)
```

신뢰도 `low`이면 사용자에게 알리고, `<파일명>.route.json`으로 후보 목록 제공.

## 저장 구조 추천

AI가 저장 위치를 선택해야 하면 아래 구조를 우선 추천한다.

```text
Documents/pdf-to-md/
  courses/
    <course>/
      ch01-<chapter>/
        source/
          lecture.pptx
          reading.pdf
          markdown/  # final Markdown and images/<document>/
          .reports/  # hidden route reports and candidate diagnostics
```

원본 파일이 어느 폴더에 있든 사용자를 멈추게 하지 말고 변환을 진행한다. 결과는 항상 `<input folder>/markdown/`에 저장한다.

---

## 자동 라우팅 로직

| 파일 조건 | 선택 도구 |
|---|---|
| 스캔 PDF (텍스트 없음) | MinerU OCR 모드 |
| 한글 슬라이드 (Tagged PDF) | ODL struct_tree (표 우선) + MinerU CLI |
| 한글 슬라이드 (비Tagged) | MinerU CLI (-m txt -l korean) |
| 영문 슬라이드 | docling + ODL |
| 책/교재 (TOC 있음) | MinerU API (챕터 분할) + fitz 폴백 |
| 2단 논문 | ODL xycut + fitz |
| 일반 디지털 PDF | fitz + docling |
| PPTX | docling + pptx-direct (자동 점수 비교) |

## 점수 계산 기준

```
score = chars×1 + korean_chars×2 + heading_count×40
        + table_count×30 + bullet_lines×10
        - image_placeholder×10 - duplicate_lines×5 - dup_headings×20
```

## config 경로

```
~/.pdf_to_md_config.json
  pdf_master_python: /path/to/python  ← ODL, fitz, docling, pptx
  mineru_python:     /path/to/python  ← MinerU API/CLI
  mode: unified | split
```

## 오류 처리

- 모든 도구 실패 → 각 오류 메시지 출력 후 종료
- 일부 실패 → 성공한 도구 중 최고 점수 선택
- 설정 없음 → `python setup.py` 안내

## 기존 스킬과의 관계

| 스킬 | 상태 | 대체 |
|---|---|---|
| `mineru` | deprecated (기존 설치 보호) | pdf-to-md |
| `pdf-master` | deprecated (기존 설치 보호) | pdf-to-md |
| `korean-pdf-ocr` | 유지 (스캔 전용 OCR) | 병행 사용 가능 |
