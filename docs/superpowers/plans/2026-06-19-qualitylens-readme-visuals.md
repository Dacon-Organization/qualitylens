# QualityLens README Visuals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 실제 배포 앱과 일치하는 QualityLens 썸네일, 시스템 구성도, 화면 캡처와 본선 참가 증빙을 추가하고 기존 README를 실무 포트폴리오 형태로 개편한다.

**Architecture:** GPT Image 2.0은 텍스트가 없는 산업 배경 두 장만 생성한다. 실제 앱 캡처와 모든 제목, 레이블, 연결선은 HTML/CSS 레이어로 합성해 생성형 UI 왜곡을 차단하고, 최종 16:9 PNG를 README에서 참조한다.

**Tech Stack:** GPT Image 2.0 built-in image generation, Codex in-app Browser, HTML/CSS, Streamlit deployed app, PowerShell, Git

---

## File Map

- Create: `smart-factory-hackathon/assets/readme/qualitylens-hero.png` - README 대표 이미지
- Create: `smart-factory-hackathon/assets/readme/qualitylens-architecture.png` - 구현 기준 시스템 구성도
- Create: `smart-factory-hackathon/assets/readme/qualitylens-hero-background.png` - GPT 생성 썸네일 배경
- Create: `smart-factory-hackathon/assets/readme/qualitylens-architecture-background.png` - GPT 생성 구성도 배경
- Create: `smart-factory-hackathon/assets/readme/screens/main-dashboard.png` - 실제 메인 화면
- Create: `smart-factory-hackathon/assets/readme/screens/root-cause-analysis.png` - 실제 원인 분석 화면
- Create: `smart-factory-hackathon/assets/readme/screens/action-guide.png` - 실제 조치 가이드 화면
- Create: `smart-factory-hackathon/assets/readme/screens/spc-pareto.png` - 실제 SPC/Pareto 화면
- Create: `smart-factory-hackathon/assets/readme/sources/qualitylens-hero.html` - 썸네일 합성 원본
- Create: `smart-factory-hackathon/assets/readme/sources/qualitylens-architecture.html` - 구성도 합성 원본
- Create: `smart-factory-hackathon/docs/certificates/2026-smart-factory-finals-participation.pdf` - 본선 참가 인증서 원본
- Create: `smart-factory-hackathon/docs/presentation/final/qualitylens-finals-presentation.pdf` - 본선 최종 발표 PDF 원본
- Modify: `smart-factory-hackathon/README.md` - 이미지, 대회 결과, 실제 페이지 구조 반영

### Task 1: Capture the deployed application

**Files:**
- Create: `smart-factory-hackathon/assets/readme/screens/main-dashboard.png`
- Create: `smart-factory-hackathon/assets/readme/screens/root-cause-analysis.png`
- Create: `smart-factory-hackathon/assets/readme/screens/action-guide.png`
- Create: `smart-factory-hackathon/assets/readme/screens/spc-pareto.png`

- [ ] **Step 1: Create the asset directories**

Use `apply_patch` for source files and PowerShell only to create directories needed for browser outputs.

```powershell
New-Item -ItemType Directory -Force smart-factory-hackathon/assets/readme/screens
New-Item -ItemType Directory -Force smart-factory-hackathon/assets/readme/sources
New-Item -ItemType Directory -Force smart-factory-hackathon/docs/certificates
```

- [ ] **Step 2: Capture four deployed pages**

Open each URL in the Codex in-app Browser at a 1600x900 viewport, dismiss onboarding, wait for visible headings, then save a viewport screenshot without generative editing.

```text
https://qualitylens-smart-factory.streamlit.app/?mode=dummy
https://qualitylens-smart-factory.streamlit.app/원인_분석?mode=dummy
https://qualitylens-smart-factory.streamlit.app/조치_가이드?mode=dummy
https://qualitylens-smart-factory.streamlit.app/SPC_Pareto?mode=dummy
```

Expected headings: `QualityLens`, `P3 — 원인 분석`, `P4 — 조치 가이드`, `SPC + Pareto — 제조 실무 표준 분석`.

- [ ] **Step 3: Verify screenshot dimensions and visible content**

```powershell
Add-Type -AssemblyName System.Drawing
Get-ChildItem smart-factory-hackathon/assets/readme/screens/*.png | ForEach-Object {
  $image = [System.Drawing.Image]::FromFile($_.FullName)
  [pscustomobject]@{ Name = $_.Name; Width = $image.Width; Height = $image.Height }
  $image.Dispose()
}
```

Expected: four PNG files, each 1600x900, with no onboarding modal.

### Task 2: Generate text-free GPT backgrounds

**Files:**
- Create: `smart-factory-hackathon/assets/readme/qualitylens-hero-background.png`
- Create: `smart-factory-hackathon/assets/readme/qualitylens-architecture-background.png`

- [ ] **Step 1: Generate the hero background with built-in GPT Image 2.0**

Use this prompt exactly, with no reference image:

```text
Use case: ads-marketing
Asset type: GitHub README hero background
Primary request: create a premium wide background for an AI smart-factory operations portfolio named QualityLens
Scene/backdrop: bright modern semiconductor manufacturing floor with clean automated equipment, subtle sensor data light trails, realistic but understated
Style/medium: polished editorial industrial photography with restrained technology overlays
Composition/framing: 16:9 landscape, darker navy and teal area on the left for title copy, brighter factory depth on the right, generous negative space, no central subject
Lighting/mood: clean cool daylight, credible engineering environment, professional and practical
Color palette: deep navy, cobalt blue, cyan, teal, white
Constraints: background only; no people; no app screen; no device frame; no logo; no readable symbols
Avoid: all text, letters, numbers, UI panels, dashboards, watermarks, badges, awards, trophies
```

- [ ] **Step 2: Generate the architecture background with built-in GPT Image 2.0**

Use this prompt exactly, with no reference image:

```text
Use case: productivity-visual
Asset type: system architecture infographic background
Primary request: create a very subtle wide industrial technology canvas for a smart-factory software architecture diagram
Scene/backdrop: near-white technical paper with faint blue grid lines, abstract factory geometry and understated circuit paths around the outer edges
Style/medium: clean enterprise infographic background, minimal and flat, extremely low visual noise
Composition/framing: 16:9 landscape, empty central 85 percent reserved for deterministic diagram boxes and labels
Lighting/mood: bright, precise, trustworthy
Color palette: white, very pale blue, faint cyan, tiny navy accents
Constraints: background decoration only; keep center empty; no icons that imply specific software
Avoid: all text, letters, numbers, arrows, boxes, UI panels, logos, watermarks, awards, gradients that reduce readability
```

- [ ] **Step 3: Inspect generated outputs**

Use `view_image` on both files. Reject and regenerate once if either contains readable text, a fabricated dashboard, a logo, an award, or a central object that blocks overlay content.

### Task 3: Build deterministic HTML composites

**Files:**
- Create: `smart-factory-hackathon/assets/readme/sources/qualitylens-hero.html`
- Create: `smart-factory-hackathon/assets/readme/sources/qualitylens-architecture.html`
- Create: `smart-factory-hackathon/assets/readme/qualitylens-hero.png`
- Create: `smart-factory-hackathon/assets/readme/qualitylens-architecture.png`

- [ ] **Step 1: Create the hero source**

Create a 1600x900 fixed canvas that uses `../qualitylens-hero-background.png` as a cover background. Place the exact strings below on the left and `../screens/main-dashboard.png` on the right inside a rounded browser frame.

```text
QualityLens
AI 기반 스마트 공장 운영 시스템
Predict → Explain → Act
XGBoost · SHAP · Threshold Engine · SPC/Pareto
```

Use `Noto Sans KR`, `Pretendard`, or `Malgun Gothic`; use white text; do not add generated logos or metrics.

- [ ] **Step 2: Create the architecture source**

Create a 1600x900 fixed canvas over `../qualitylens-architecture-background.png`. Use five left-to-right groups with these exact labels:

```text
1 DATA SOURCES
UCI SECOM · 사용자 CSV · 결정론 데모

2 OFFLINE ML PIPELINE
01_preprocess.py · 02_train.py · 03_shap.py · Threshold Engine

3 MODEL & ARTIFACTS
전처리 데이터 · XGBoost 모델 · Thresholds · SHAP 결과 · Demo Result · Action Log

4 STREAMLIT APPLICATION
Home · P0 업로드 · P1 실시간 예측 · P2 원인 분석 · P3 조치 가이드 · P4 이력 조회 · P5 SPC/Pareto · P6 종합 대시보드

5 USERS & DEPLOYMENT
현장 작업자 · 공정팀/QC · 생산관리자 · 경영진 · Streamlit Community Cloud

CSV 업로드 → Predict → Explain → Act → 이력 · SPC 개선
```

- [ ] **Step 3: Render both sources**

Serve `smart-factory-hackathon/assets/readme/` on localhost, set the in-app Browser viewport to 1600x900, navigate to each source HTML, and save an exact viewport screenshot to the final PNG path.

- [ ] **Step 4: Verify deterministic layers**

Open the final PNGs with `view_image` and compare the embedded main dashboard against `screens/main-dashboard.png`. Expected: no altered menu labels, values, or chart text; all architecture labels listed in Step 2 are legible.

### Task 4: Store the participation certificate and final presentation

**Files:**
- Create: `smart-factory-hackathon/docs/certificates/2026-smart-factory-finals-participation.pdf`
- Create: `smart-factory-hackathon/docs/presentation/final/qualitylens-finals-presentation.pdf`

- [ ] **Step 1: Record the source checksum and copy the PDF**

```powershell
$source = 'C:\Users\kik32\Downloads\2026 스마트 공장 운영 시스템 MVP 개발 해커톤 본선 인증서.pdf'
$target = 'smart-factory-hackathon\docs\certificates\2026-smart-factory-finals-participation.pdf'
$sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash
Copy-Item -LiteralPath $source -Destination $target
$targetHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
if ($sourceHash -ne $targetHash) { throw 'Certificate checksum mismatch' }
```

Expected: hashes match exactly.

- [ ] **Step 2: Copy and verify the final presentation PDF**

Copy `QualityLens — 2026 스마트 공장 운영 시스템 MVP 해커톤 본선 발표.pdf` from
Downloads to `docs/presentation/final/qualitylens-finals-presentation.pdf`, compare SHA256
checksums, and render all 17 pages for a visual integrity check.

### Task 5: Update the README

**Files:**
- Modify: `smart-factory-hackathon/README.md`

- [ ] **Step 1: Add the portfolio header**

Insert the hero, live demo link, concise stack line, and this exact result statement before the existing project overview:

```markdown
![QualityLens - AI 기반 스마트 공장 운영 시스템](assets/readme/qualitylens-hero.png)

> **대회 결과:** 예선을 통과해 2026년 5월 22일 본선에 참가했으며, 최종 수상에는 이르지 못했습니다.
```

- [ ] **Step 2: Add architecture and actual-screen sections**

Embed `assets/readme/qualitylens-architecture.png`, then add a four-image table using the files under `assets/readme/screens/` with captions `메인 대시보드`, `원인 분석`, `조치 가이드`, `SPC/Pareto`.

- [ ] **Step 3: Correct stale facts without deleting the existing explanation**

Apply these exact corrections:

```text
2026.05.13(월) → 2026.05.13(수)
Streamlit 기반 5개 화면 → Streamlit 기반 Home + P0~P6 화면
MVP 구성 표 → Home, P0, P1, P2, P3, P4, P5, P6
1/100 가격 → Streamlit Cloud 기반 저비용 MVP 배포
build_pptx_v4.py → build_pptx.py, build_pptx_v2.py
diagrams/ → assets/readme/
```

- [ ] **Step 4: Add certificate as a text link only**

```markdown
- [본선 참가 증빙](docs/certificates/2026-smart-factory-finals-participation.pdf) - 인증서 원본 PDF
```

- [ ] **Step 5: Link the final presentation artifacts**

Add links to the copied final PDF and the existing `docs/presentation/slides.html` source.

### Task 6: Verify and commit the implementation

**Files:**
- Verify all files listed in the File Map

- [ ] **Step 1: Validate referenced paths**

Extract local Markdown image and link targets from `smart-factory-hackathon/README.md` and assert that each file exists relative to the README directory. Expected: zero missing local targets.

- [ ] **Step 2: Run repository checks**

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; `.superpowers/` and the pre-existing `.worktrees/kik32-alphafolio-demo-dashboard` change remain unstaged.

- [ ] **Step 3: Visually inspect final assets**

Use `view_image` for the hero, architecture, and four screenshots. Confirm 16:9 dimensions, readable Korean, no fabricated UI, and no certificate image in the README.

- [ ] **Step 4: Commit only project deliverables**

```powershell
git add -- smart-factory-hackathon/README.md smart-factory-hackathon/assets/readme smart-factory-hackathon/docs/certificates
git commit -m "📝 Docs: QualityLens README 시각 자료 추가"
```

Expected: the implementation commit contains README, generated assets, source HTML, screenshots, and certificate only.
