# P-A 실데이터 통합·검증 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** UCI SECOM 실데이터(1567 × 591) 로 T1→T2→T3 파이프라인을 무에러 완주하고, 더미 대비 비교 보고서 + 단계별 HTML 보고서 5종 + Playwright E2E 검증까지 완성해 본선 발표 신뢰성 근거 확보.

**Architecture:** 기존 `scripts/0{1,2,3}.py` 에 `--source {real,dummy}` 플래그 추가, 산출물은 `_real`/`_dummy` 접미사로 분리. `app/lib/data_loader.py` 가 real 우선 → dummy 폴백을 단일화. 각 스크립트 끝에 `app/lib/report_render.py` 헬퍼로 단계별 HTML 보고서 자동 출력. 6개 sub-PR(PR-1~PR-6) 단위로 분할 머지, 각 PR마다 GitHub MCP 경로(create_pull_request → merge_pull_request).

**Tech Stack:** Python 3.11 / pandas / numpy / scikit-learn / xgboost / shap / SMOTE / Streamlit / plotly / matplotlib / pytest / Playwright MCP / GitHub MCP

**Spec 출처:** [smart-factory-hackathon/docs/spec_p_a_real_data_integration.md](smart-factory-hackathon/docs/spec_p_a_real_data_integration.md) (커밋 `984d173` on main)

---

## File Structure — 변경 대상 매핑

### 신규 파일
```
smart-factory-hackathon/
├── data/raw/
│   ├── secom.data                              # UCI 원본 (PR-1)
│   ├── secom_labels.data                       # UCI 원본 (PR-1)
│   └── LICENSE.md                              # UCI 라이선스·인용 (PR-1)
├── scripts/
│   ├── 00_download_secom.py                    # 자동 다운로드 (PR-1)
│   └── 04_compare_real_vs_dummy.py             # 비교 보고서 (PR-3)
├── app/lib/
│   ├── data_loader.py                          # real 우선 → dummy 폴백 (PR-2)
│   ├── fonts.py                                # matplotlib + plotly + HTML CSS 3중 폰트 (PR-2)
│   └── report_render.py                        # 단계별 HTML 헬퍼 + build_index (PR-4)
├── assets/vendor/
│   └── plotly.min.js                           # 오프라인 폴백 (PR-4)
├── docs/
│   ├── validation/
│   │   └── real_vs_dummy_report.md             # 자동 생성 (PR-3)
│   └── reports/
│       ├── 01_preprocessing.html               # 자동 생성 (PR-4)
│       ├── 02_training.html                    # 자동 생성 (PR-4)
│       ├── 03_shap.html                        # 자동 생성 (PR-4)
│       ├── 04_real_vs_dummy.html               # 자동 생성 (PR-4)
│       ├── 05_playwright_qa.html               # 자동 생성 (PR-5)
│       └── index.html                          # 자동 생성 (PR-4)
├── assets/qa/playwright/
│   ├── real/{P1..P5}.png                       # 트랙 ① (PR-5)
│   ├── dummy/{P1..P5}.png                      # 트랙 ① (PR-5)
│   └── golden_path/{step1..step5}.png          # 트랙 ② (PR-5)
└── tests/
    ├── unit/
    │   ├── test_data_loader.py                 # PR-2
    │   ├── test_compare_report.py              # PR-3
    │   └── test_report_render.py               # PR-4
    └── e2e/
        ├── playwright_scenarios.md             # PR-5
        └── run_playwright_qa.py                # PR-5
```

### 수정 파일
| 파일 | PR | 변경 내용 |
|---|---|---|
| `smart-factory-hackathon/.gitignore` | PR-1 | `!data/raw/secom.data` + `!data/raw/secom_labels.data` 예외 추가, real/dummy 산출물 예외 |
| `scripts/01_preprocess.py` | PR-2, PR-4 | argparse `--source` + 파일명 분기 (PR-2), 끝부분 `report_render.write` 호출 추가 (PR-4) |
| `scripts/02_train.py` | PR-2, PR-4 | 동일 |
| `scripts/03_shap.py` | PR-2, PR-4 | 동일 |
| `app/lib/load.py` | PR-2 | `data_loader` 위임 — 기존 함수 시그니처 유지하면서 내부 분기 위임 |
| `app/app.py` | PR-2 | 사이드바 배지 추가 |
| `app/pages/1~4*.py` | PR-2 | 사이드바 배지 import |
| `README.md` | PR-6 | "데이터" 섹션 + 본선 메시지 |
| `docs/slides_outline.md` | PR-6 | Slide 4 + Slide 7 메시지 |
| `docs/demo_script.md` | PR-6 | Q&A 노트 보강 |

### 산출물 명명 규칙 (기존 + `_real`/`_dummy` 접미사)

```
data/processed/
├── secom_X_train_{real,dummy}.pkl
├── secom_y_train_{real,dummy}.pkl
├── secom_X_test_{real,dummy}.pkl
├── secom_y_test_{real,dummy}.pkl
├── demo_sample_{real,dummy}.pkl
├── demo_result_{real,dummy}.csv
└── shap_demo_{real,dummy}.png

models/
├── xgb_secom_{real,dummy}.joblib
├── threshold_table_{real,dummy}.csv
├── shap_explainer_{real,dummy}.pkl
├── shap_values_test_{real,dummy}.pkl
├── shap_top20_{real,dummy}.csv
├── shap_per_sample_{real,dummy}.pkl
├── shap_waterfall_demo_{real,dummy}.pkl
├── shap_group_{real,dummy}.csv
└── model_card_{real,dummy}.md
```

---

## PR-1 — UCI 데이터 + 다운로드 스크립트 + LICENSE

**Branch:** `feat/p-a-1-uci-data`
**Base:** `main`
**LOC 예상:** ~80
**모델 라우팅:** Sonnet (반복 작업, 단순 다운로드·문서)

### Task 1.1: 작업 브랜치 생성 + main 동기화

**Files:** (git 상태만)

- [ ] **Step 1: 워크트리에서 main 동기화**

```powershell
git fetch origin main
git switch main 2>$null; if (-not $?) { git checkout main }
git pull --rebase origin main
```

Expected: `Already up to date.` 또는 fast-forward.

- [ ] **Step 2: 새 브랜치 생성**

```powershell
git switch -c feat/p-a-1-uci-data
```

Expected: `Switched to a new branch 'feat/p-a-1-uci-data'`

### Task 1.2: UCI 원본 다운로드 스크립트

**Files:**
- Create: `smart-factory-hackathon/scripts/00_download_secom.py`

- [ ] **Step 1: 작성**

```python
"""UCI SECOM 원본을 data/raw/ 로 다운로드.

본선장 오프라인 대비로 원본을 git에 직접 커밋하므로, 이 스크립트는
재현·신규 개발자·CI 용도. 본선장에서는 실행 불필요.

CLI::

    python scripts/00_download_secom.py
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

UCI_BASE = "https://archive.ics.uci.edu/static/public/179/secom.zip"
FILES = {
    "secom.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data",
    "secom_labels.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data",
}

EXPECTED_SHAPES = {
    "secom.data": (1567, 590),     # 공백 구분 591개 토큰, 끝 공백 1개 처리는 pandas에 위임
    "secom_labels.data": (1567, 2),
}


def download(name: str, url: str) -> Path:
    dest = RAW_DIR / name
    if dest.exists():
        print(f"[skip] {name} 존재 — {dest.stat().st_size:,} bytes")
        return dest
    print(f"[download] {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"  → {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def verify(name: str, path: Path) -> None:
    """파일을 줄 단위로 세서 shape 어설션."""
    rows = path.read_text().strip().splitlines()
    expected_rows, _ = EXPECTED_SHAPES[name]
    assert len(rows) == expected_rows, f"{name}: rows {len(rows)} != {expected_rows}"
    print(f"[verify] {name} rows={len(rows)} OK")


def main() -> int:
    for name, url in FILES.items():
        path = download(name, url)
        verify(name, path)
    print("\n=== UCI SECOM 다운로드 완료 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 다운로드 실행**

```powershell
python smart-factory-hackathon/scripts/00_download_secom.py
```

Expected:
```
[download] .../secom.data
  → ...secom.data (~1,500,000 bytes)
[verify] secom.data rows=1567 OK
[download] .../secom_labels.data
  → ...secom_labels.data (~50,000 bytes)
[verify] secom_labels.data rows=1567 OK
=== UCI SECOM 다운로드 완료 ===
```

- [ ] **Step 3: 다운로드 실패 시 폴백** — UCI 사이트가 응답하지 않으면, 수동으로 `https://archive.ics.uci.edu/dataset/179/secom` 에서 받아 `smart-factory-hackathon/data/raw/` 에 배치 후 다음 step 진행.

### Task 1.3: .gitignore 예외 추가

**Files:**
- Modify: `smart-factory-hackathon/.gitignore`

- [ ] **Step 1: 예외 라인 추가**

기존:
```
data/raw/*
!data/raw/.gitkeep
!data/raw/README.md
data/processed/*
!data/processed/.gitkeep
!data/processed/demo_sample.pkl
!data/processed/demo_result.csv
!data/processed/shap_demo.png

# Models
models/*.joblib
models/*.pkl
!models/.gitkeep
!models/README.md
!models/threshold_table.csv
!models/shap_top20.csv
!models/model_card.md
```

수정 후:
```
data/raw/*
!data/raw/.gitkeep
!data/raw/README.md
!data/raw/LICENSE.md
!data/raw/secom.data
!data/raw/secom_labels.data
data/processed/*
!data/processed/.gitkeep
!data/processed/demo_sample_real.pkl
!data/processed/demo_sample_dummy.pkl
!data/processed/demo_result_real.csv
!data/processed/demo_result_dummy.csv
!data/processed/shap_demo_real.png
!data/processed/shap_demo_dummy.png

# Models
models/*.joblib
models/*.pkl
!models/.gitkeep
!models/README.md
!models/threshold_table_real.csv
!models/threshold_table_dummy.csv
!models/shap_top20_real.csv
!models/shap_top20_dummy.csv
!models/shap_group_real.csv
!models/shap_group_dummy.csv
!models/model_card_real.md
!models/model_card_dummy.md
```

- [ ] **Step 2: 변경 확인**

```powershell
git diff smart-factory-hackathon/.gitignore
```

Expected: 위 예외 라인들이 `+` 로, 기존 `demo_sample.pkl` 등 단수형이 `-` 로 표시.

### Task 1.4: LICENSE 작성

**Files:**
- Create: `smart-factory-hackathon/data/raw/LICENSE.md`

- [ ] **Step 1: 작성**

```markdown
# UCI SECOM Dataset — 출처 및 인용

본 디렉터리의 `secom.data`, `secom_labels.data` 는 UCI Machine Learning
Repository 의 SECOM Manufacturing Data 입니다.

## 출처

- 데이터셋 페이지: <https://archive.ics.uci.edu/dataset/179/secom>
- 기증자: Michael McCann, Adrian Johnston (2008)
- DOI: https://doi.org/10.24432/C54305

## 라이선스

UCI Machine Learning Repository 는 학술·연구 목적 자유 사용을 허용합니다.
상업적 이용 시 원 데이터 소유자(반도체 제조사)와 별도 합의가 필요합니다.

본 해커톤 프로젝트는 **2026 스마트 공장 운영 시스템 MVP 개발 해커톤** 의
학술적 시연을 위해 사용합니다 — 비영리·교육 목적.

## 인용

논문이나 보고서 인용 시:

> McCann, M. & Johnston, A. (2008). SECOM [Dataset]. UCI Machine Learning
> Repository. https://doi.org/10.24432/C54305

## 본선 발표 시 안내 문구

"본 데이터는 UCI Machine Learning Repository 의 SECOM (반도체 제조 공정)
공개 데이터셋으로, 591개 익명화 센서 신호와 PASS/FAIL 라벨 1567건을 포함합니다.
센서 의미 라벨은 익명화되어 있어 본 프로젝트에서는 기획 가정으로 매핑합니다."
```

- [ ] **Step 2: 파일 확인**

```powershell
Get-Content smart-factory-hackathon/data/raw/LICENSE.md -TotalCount 5
```

Expected: 위 헤더 5줄.

### Task 1.5: 데이터 무결성 검증 + 커밋

**Files:** (git 단계)

- [ ] **Step 1: 파일 존재 + 크기 확인**

```powershell
Get-ChildItem smart-factory-hackathon/data/raw/secom*.data | Format-Table Name, Length
```

Expected:
```
Name              Length
----              ------
secom.data        ~1500000
secom_labels.data ~50000
```

- [ ] **Step 2: pandas 로드 무결성 어설션 (간단 스크립트)**

```powershell
python -c "import pandas as pd; df = pd.read_csv('smart-factory-hackathon/data/raw/secom.data', sep=r'\s+', header=None); lb = pd.read_csv('smart-factory-hackathon/data/raw/secom_labels.data', sep=r'\s+', header=None); assert df.shape == (1567, 591), df.shape; assert lb.shape == (1567, 2), lb.shape; print('OK', df.shape, lb.shape)"
```

Expected: `OK (1567, 591) (1567, 2)`

- [ ] **Step 3: git add + status**

```powershell
git add smart-factory-hackathon/.gitignore smart-factory-hackathon/data/raw/LICENSE.md smart-factory-hackathon/data/raw/secom.data smart-factory-hackathon/data/raw/secom_labels.data smart-factory-hackathon/scripts/00_download_secom.py
git status --short
```

Expected: 위 5개 파일이 `A` (added) 로 표시.

- [ ] **Step 4: 커밋**

```powershell
git commit -m "feat(p-a/PR-1): UCI SECOM 원본 데이터 + 다운로드 스크립트 [Sonnet]

- data/raw/secom.data, secom_labels.data 원본 직접 커밋 (~1.5MB)
- LICENSE.md 로 UCI 출처·인용 표기
- scripts/00_download_secom.py 재현·CI 용도
- .gitignore 예외 추가 (real/dummy 산출물)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

- [ ] **Step 5: push**

```powershell
git push -u origin feat/p-a-1-uci-data
```

Expected: `* [new branch] feat/p-a-1-uci-data -> feat/p-a-1-uci-data`

### Task 1.6: PR-1 생성·머지 (GitHub MCP)

- [ ] **Step 1: GitHub MCP `create_pull_request` 호출**

```jsonc
{
  "owner": "mygithub05253",
  "repo": "Dacon",
  "head": "feat/p-a-1-uci-data",
  "base": "main",
  "title": "feat(p-a/PR-1): UCI SECOM 원본 + 다운로드 스크립트 + LICENSE",
  "body": "## 요약\n\nP-A 1단계 — UCI SECOM 실데이터를 git에 직접 커밋(~1.5MB, LFS 불필요).\n\n## 변경\n- `data/raw/secom.data`, `secom_labels.data` 원본 커밋\n- `data/raw/LICENSE.md` 출처·인용 표기\n- `scripts/00_download_secom.py` 재현용 다운로더 + shape 어설션\n- `.gitignore` 예외 추가\n\n## 검증\n- [x] pandas 로드 1567×591 어설션 통과\n- [x] 라이선스 문서 정확\n\n다음: PR-2 (`--source` 플래그 + data_loader.py)"
}
```

- [ ] **Step 2: 머지 (squash)**

CI 통과 또는 status 0개 확인 후 `mcp__github__merge_pull_request`:
```jsonc
{
  "owner": "mygithub05253",
  "repo": "Dacon",
  "pull_number": <PR-1 번호>,
  "merge_method": "squash",
  "commit_title": "feat(p-a/PR-1): UCI SECOM 원본 + 다운로드 스크립트 + LICENSE (#N)",
  "commit_message": "P-A 1단계 — 실데이터 git 직접 커밋. [Sonnet]"
}
```

- [ ] **Step 3: 로컬 main 동기화**

```powershell
git switch main
git pull origin main
```

Expected: fast-forward 또는 already up to date.

---

## PR-2 — `--source` 플래그 + data_loader.py + fonts.py

**Branch:** `feat/p-a-2-source-flag-and-loader`
**Base:** `main` (PR-1 머지 후)
**LOC 예상:** ~250
**모델 라우팅:** Sonnet (스크립트 인자 추가·로더 분기 단순 반복) + Opus (data_loader 인터페이스 설계)

### Task 2.1: 새 브랜치 생성

- [ ] **Step 1:**

```powershell
git switch main
git pull origin main
git switch -c feat/p-a-2-source-flag-and-loader
```

### Task 2.2: `app/lib/fonts.py` — 3중 한글 폰트 헬퍼

**Files:**
- Create: `smart-factory-hackathon/app/lib/fonts.py`

기존 `app/lib/i18n.py` 와 `scripts/_i18n.py` 는 matplotlib 만 다룬다. `fonts.py` 는 matplotlib + plotly + HTML CSS 3중을 한 곳에서 다룬다 (P-B에서 전면 점검하지만 P-A 단계에서 이미 도입).

- [ ] **Step 1: 작성**

```python
"""한글 폰트 통합 — matplotlib, plotly, HTML CSS 3중 적용.

scripts·앱·HTML 리포트 모두 같은 헬퍼를 사용해 일관된 한글 렌더링을 보장한다.
"""

from __future__ import annotations

import platform


def _detect_matplotlib_font() -> str:
    system = platform.system()
    if system == "Windows":
        return "Malgun Gothic"
    if system == "Darwin":
        return "AppleGothic"
    return "NanumGothic"  # Linux / Streamlit Cloud — fonts-nanum apt 패키지 의존


def setup_matplotlib() -> str:
    """matplotlib rcParams 에 한글 폰트 적용. 사용된 폰트명 반환."""
    import matplotlib.pyplot as plt

    font = _detect_matplotlib_font()
    plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False
    return font


def plotly_template_with_korean() -> dict:
    """plotly 차트에 적용할 layout 템플릿 — font family 한글 폰트 강제.

    사용 예::

        fig.update_layout(**plotly_template_with_korean())
    """
    return {
        "font": {"family": '"Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif'},
        "title": {"font": {"family": '"Noto Sans KR", "Malgun Gothic", sans-serif'}},
    }


def html_font_face_css() -> str:
    """HTML 리포트 <style> 블록에 삽입할 한글 폰트 선언."""
    return """
    body, html {
        font-family: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    }
    """
```

- [ ] **Step 2: 단위 검증**

```powershell
python -c "from smart-factory-hackathon.app.lib.fonts import setup_matplotlib, plotly_template_with_korean, html_font_face_css; print(setup_matplotlib()); print(plotly_template_with_korean()); print(html_font_face_css()[:50])"
```

PowerShell `-` 가 모듈명에 들어가지 않으므로 실제로는 다음과 같이 실행:

```powershell
cd smart-factory-hackathon
python -c "from app.lib.fonts import setup_matplotlib, plotly_template_with_korean, html_font_face_css; print(setup_matplotlib()); print(plotly_template_with_korean()); print(html_font_face_css()[:50])"
cd ..
```

Expected (Windows):
```
Malgun Gothic
{'font': {'family': '"Noto Sans KR", "Malgun Gothic", ...'}}
body, html { font-family: "Noto Sans KR", ...
```

### Task 2.3: `scripts/01_preprocess.py` — `--source` 플래그

**Files:**
- Modify: `smart-factory-hackathon/scripts/01_preprocess.py:1-180` (전체 구조 변경)

기존은 단일 경로. 이제 `argparse` 로 `--source` 받고, 산출물 파일명에 접미사를 붙인다. dummy 폴백은 명시적으로 `--source dummy` 일 때만, real 인데 파일이 없으면 에러로 멈춘다 (이전엔 자동 폴백이었지만 spec에 따라 명시적 분리).

- [ ] **Step 1: import 추가 + argparse 헬퍼**

`from __future__ import annotations` 아래에 다음 추가:

```python
import argparse
```

기존 `RANDOM_STATE = 42` 위에 추가:

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="T1 전처리 — UCI SECOM 실데이터 또는 더미")
    parser.add_argument(
        "--source",
        choices=["real", "dummy"],
        default="real",
        help="real: data/raw 의 UCI 원본 사용 / dummy: 합성 더미 생성",
    )
    return parser.parse_args()


ARGS = parse_args() if __name__ == "__main__" else argparse.Namespace(source="real")
SOURCE = ARGS.source  # "real" or "dummy"
SUFFIX = f"_{SOURCE}"  # "_real" or "_dummy"
```

- [ ] **Step 2: `load_secom()` 분기 정리**

기존 함수 전체를 다음으로 교체:

```python
def load_secom(source: str) -> tuple[pd.DataFrame, pd.Series, bool]:
    """source 에 따라 실데이터 또는 더미를 반환.

    Returns
    -------
    X, y, is_dummy_actually
        is_dummy_actually 는 source='real' 인데 파일이 없어 폴백된 경우만 True.
        spec 규약상 source='real' 인데 파일 없으면 에러로 멈춰야 함 — is_dummy_actually
        는 source='dummy' 일 때만 True.
    """
    data_path = RAW_DIR / "secom.data"
    labels_path = RAW_DIR / "secom_labels.data"

    if source == "real":
        if not (data_path.exists() and labels_path.exists()):
            raise FileNotFoundError(
                f"실데이터 모드인데 원본 부재: {data_path}. "
                "scripts/00_download_secom.py 를 먼저 실행하거나 --source dummy 사용."
            )
        X = pd.read_csv(data_path, sep=r"\s+", header=None)
        labels = pd.read_csv(labels_path, sep=r"\s+", header=None)
        y = (labels.iloc[:, 0] == 1).astype(int)
        X.columns = [f"sensor_{i:03d}" for i in range(X.shape[1])]
        return X, y, False

    # source == "dummy"
    print("[INFO] 더미 모드 — 1567 × 591 합성 데이터 생성 (fail 6.6%)")
    rng = np.random.default_rng(RANDOM_STATE)
    n, p = 1567, 591
    X = pd.DataFrame(
        rng.normal(size=(n, p)),
        columns=[f"sensor_{i:03d}" for i in range(p)],
    )
    for i in rng.choice(p, size=80, replace=False):
        mask = rng.random(n) < rng.uniform(0.1, 0.3)
        X.iloc[mask, i] = np.nan
    score = X.iloc[:, [3, 17, 42]].fillna(0).sum(axis=1)
    threshold = score.quantile(0.934)
    y = (score > threshold).astype(int)
    return X, y, True
```

- [ ] **Step 3: 호출부 수정**

기존:
```python
X_raw, y_raw, is_dummy = load_secom()
print(f"원본: {X_raw.shape} / 불량 비율 {y_raw.mean()*100:.2f}%")
```

교체:
```python
X_raw, y_raw, is_dummy = load_secom(SOURCE)
print(f"[{SOURCE}] 원본: {X_raw.shape} / 불량 비율 {y_raw.mean()*100:.2f}%")
```

- [ ] **Step 4: `save_processed()` 파일명 분기**

기존:
```python
def save_processed() -> None:
    pd.to_pickle(X_train_sm, PROC_DIR / "secom_X_train.pkl")
    pd.to_pickle(y_train_sm, PROC_DIR / "secom_y_train.pkl")
    pd.to_pickle(X_test, PROC_DIR / "secom_X_test.pkl")
    pd.to_pickle(y_test, PROC_DIR / "secom_y_test.pkl")
    fail_idx = y_test[y_test == 1].index[:2]
    pass_idx = y_test[y_test == 0].index[:2]
    demo_idx = list(fail_idx) + list(pass_idx)
    demo_sample = X_test.loc[demo_idx]
    demo_sample.to_pickle(PROC_DIR / "demo_sample.pkl")
    print(f"저장 완료 → {PROC_DIR}")
```

교체:
```python
def save_processed() -> None:
    pd.to_pickle(X_train_sm, PROC_DIR / f"secom_X_train{SUFFIX}.pkl")
    pd.to_pickle(y_train_sm, PROC_DIR / f"secom_y_train{SUFFIX}.pkl")
    pd.to_pickle(X_test, PROC_DIR / f"secom_X_test{SUFFIX}.pkl")
    pd.to_pickle(y_test, PROC_DIR / f"secom_y_test{SUFFIX}.pkl")
    fail_idx = y_test[y_test == 1].index[:2]
    pass_idx = y_test[y_test == 0].index[:2]
    demo_idx = list(fail_idx) + list(pass_idx)
    demo_sample = X_test.loc[demo_idx]
    demo_sample.to_pickle(PROC_DIR / f"demo_sample{SUFFIX}.pkl")
    print(f"[{SOURCE}] 저장 완료 → {PROC_DIR}")
```

- [ ] **Step 5: 마지막 print 블록 수정**

기존:
```python
print("\n=== T1 완료 ===")
print(f"더미 모드: {is_dummy}")
```

교체:
```python
print(f"\n=== T1 완료 ({SOURCE}) ===")
print(f"실제 더미 폴백: {is_dummy}")
```

- [ ] **Step 6: 실행 검증 (real)**

```powershell
cd smart-factory-hackathon
python scripts/01_preprocess.py --source real
cd ..
```

Expected:
```
[real] 원본: (1567, 591) / 불량 비율 6.61%
결측치 컬럼 제거: ~5 / 남은 컬럼: ~586
저분산 제거: ~0 / 남은 컬럼: ~586
고상관 제거: ~70 / 남은 컬럼: ~516
Split — train 1253 / test 314
train fail: 6.62% / test fail: 6.69%
SMOTE 후 train — ~2340 samples / fail 50.00%
[real] 저장 완료 → .../data/processed
=== T1 완료 (real) ===
실제 더미 폴백: False
피처 수: ~516
```

- [ ] **Step 7: 실행 검증 (dummy)**

```powershell
cd smart-factory-hackathon
python scripts/01_preprocess.py --source dummy
cd ..
```

Expected: 마지막에 `=== T1 완료 (dummy) ===` 와 `실제 더미 폴백: True`.

- [ ] **Step 8: 산출물 확인**

```powershell
Get-ChildItem smart-factory-hackathon/data/processed/*.pkl | Select-Object Name
```

Expected (8개 파일):
```
secom_X_train_real.pkl
secom_y_train_real.pkl
secom_X_test_real.pkl
secom_y_test_real.pkl
demo_sample_real.pkl
secom_X_train_dummy.pkl
secom_y_train_dummy.pkl
secom_X_test_dummy.pkl
secom_y_test_dummy.pkl
demo_sample_dummy.pkl
```

### Task 2.4: `scripts/02_train.py` — `--source` 플래그

**Files:**
- Modify: `smart-factory-hackathon/scripts/02_train.py`

- [ ] **Step 1: import + argparse 추가**

`from __future__ import annotations` 아래:
```python
import argparse
```

`RANDOM_STATE = 42` 위에:
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="T2 모델 학습 — XGBoost")
    parser.add_argument("--source", choices=["real", "dummy"], default="real")
    return parser.parse_args()


ARGS = parse_args() if __name__ == "__main__" else argparse.Namespace(source="real")
SOURCE = ARGS.source
SUFFIX = f"_{SOURCE}"
```

- [ ] **Step 2: `load_processed()` 수정**

기존:
```python
def load_processed() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    X_train = pd.read_pickle(PROC_DIR / "secom_X_train.pkl")
    y_train = pd.read_pickle(PROC_DIR / "secom_y_train.pkl")
    X_test = pd.read_pickle(PROC_DIR / "secom_X_test.pkl")
    y_test = pd.read_pickle(PROC_DIR / "secom_y_test.pkl")
    return X_train, y_train, X_test, y_test
```

교체:
```python
def load_processed() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    X_train = pd.read_pickle(PROC_DIR / f"secom_X_train{SUFFIX}.pkl")
    y_train = pd.read_pickle(PROC_DIR / f"secom_y_train{SUFFIX}.pkl")
    X_test = pd.read_pickle(PROC_DIR / f"secom_X_test{SUFFIX}.pkl")
    y_test = pd.read_pickle(PROC_DIR / f"secom_y_test{SUFFIX}.pkl")
    return X_train, y_train, X_test, y_test
```

- [ ] **Step 3: 산출물 경로 분기**

기존 (라인 ~160, 167, 180, 218):
```python
threshold_table.to_csv(MODEL_DIR / "threshold_table.csv", index=False)
...
joblib.dump(final_model, MODEL_DIR / "xgb_secom.joblib")
...
demo_sample = pd.read_pickle(PROC_DIR / "demo_sample.pkl")
...
demo_result.to_csv(PROC_DIR / "demo_result.csv", index=False)
...
(MODEL_DIR / "model_card.md").write_text(model_card, encoding="utf-8")
```

교체:
```python
threshold_table.to_csv(MODEL_DIR / f"threshold_table{SUFFIX}.csv", index=False)
...
joblib.dump(final_model, MODEL_DIR / f"xgb_secom{SUFFIX}.joblib")
...
demo_sample = pd.read_pickle(PROC_DIR / f"demo_sample{SUFFIX}.pkl")
...
demo_result.to_csv(PROC_DIR / f"demo_result{SUFFIX}.csv", index=False)
...
(MODEL_DIR / f"model_card{SUFFIX}.md").write_text(model_card, encoding="utf-8")
```

- [ ] **Step 4: model_card 본문에 source 표시**

기존 `model_card = f"""# Model Card — QualityLens XGBoost` 의 학습 환경 섹션:

```python
## 학습 환경
- 알고리즘: XGBoost (binary:logistic, eval_metric=aucpr)
- 데이터: UCI SECOM (또는 더미)
```

교체:
```python
## 학습 환경
- 알고리즘: XGBoost (binary:logistic, eval_metric=aucpr)
- 데이터 소스: **{SOURCE.upper()}** (UCI SECOM 실데이터 / 더미 합성)
```

- [ ] **Step 5: 실행 검증 (real)**

```powershell
cd smart-factory-hackathon
python scripts/02_train.py --source real
cd ..
```

Expected:
- 5-fold MCC mean·std 출력
- `[test @<thr>] MCC=... PR-AUC=...` 출력
- `models/xgb_secom_real.joblib`, `threshold_table_real.csv`, `model_card_real.md`, `data/processed/demo_result_real.csv` 생성

- [ ] **Step 6: 실행 검증 (dummy)**

```powershell
cd smart-factory-hackathon
python scripts/02_train.py --source dummy
cd ..
```

Expected: `_dummy` 산출물 생성.

### Task 2.5: `scripts/03_shap.py` — `--source` 플래그

**Files:**
- Modify: `smart-factory-hackathon/scripts/03_shap.py`

- [ ] **Step 1: argparse 추가 + import 정리**

`from __future__ import annotations` 아래:
```python
import argparse
```

`from _i18n import setup_korean_font` 아래에:
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="T3 SHAP 사전 계산")
    parser.add_argument("--source", choices=["real", "dummy"], default="real")
    return parser.parse_args()


ARGS = parse_args() if __name__ == "__main__" else argparse.Namespace(source="real")
SOURCE = ARGS.source
SUFFIX = f"_{SOURCE}"
```

- [ ] **Step 2: 모델·데이터 로드 경로 분기**

기존:
```python
model = joblib.load(MODEL_DIR / "xgb_secom.joblib")
X_test = pd.read_pickle(PROC_DIR / "secom_X_test.pkl")
demo_sample = pd.read_pickle(PROC_DIR / "demo_sample.pkl")
```

교체:
```python
model = joblib.load(MODEL_DIR / f"xgb_secom{SUFFIX}.joblib")
X_test = pd.read_pickle(PROC_DIR / f"secom_X_test{SUFFIX}.pkl")
demo_sample = pd.read_pickle(PROC_DIR / f"demo_sample{SUFFIX}.pkl")
print(f"[{SOURCE}] 모델 로드 / test {X_test.shape} / demo {demo_sample.shape}")
```

- [ ] **Step 3: 산출물 경로 분기 (5개 위치)**

기존 → 교체:
```python
joblib.dump(explainer, MODEL_DIR / "shap_explainer.pkl")
joblib.dump(shap_arr, MODEL_DIR / "shap_values_test.pkl")
top20.to_csv(MODEL_DIR / "shap_top20.csv", index=False)
joblib.dump(demo_shap_df, MODEL_DIR / "shap_per_sample.pkl")
joblib.dump(waterfall_demo, MODEL_DIR / "shap_waterfall_demo.pkl")
fig.savefig(PROC_DIR / "shap_demo.png", dpi=120)
group_contrib.to_csv(MODEL_DIR / "shap_group.csv", index=False)
```

```python
joblib.dump(explainer, MODEL_DIR / f"shap_explainer{SUFFIX}.pkl")
joblib.dump(shap_arr, MODEL_DIR / f"shap_values_test{SUFFIX}.pkl")
top20.to_csv(MODEL_DIR / f"shap_top20{SUFFIX}.csv", index=False)
joblib.dump(demo_shap_df, MODEL_DIR / f"shap_per_sample{SUFFIX}.pkl")
joblib.dump(waterfall_demo, MODEL_DIR / f"shap_waterfall_demo{SUFFIX}.pkl")
fig.savefig(PROC_DIR / f"shap_demo{SUFFIX}.png", dpi=120)
group_contrib.to_csv(MODEL_DIR / f"shap_group{SUFFIX}.csv", index=False)
```

- [ ] **Step 4: 마지막 print 블록 수정**

```python
print(f"\n=== T3 완료 ({SOURCE}) ===")
print("모든 SHAP 산출물이 사전 계산되어 본선장 재계산 불필요.")
```

- [ ] **Step 5: 실행 검증 (real + dummy)**

```powershell
cd smart-factory-hackathon
python scripts/03_shap.py --source real
python scripts/03_shap.py --source dummy
cd ..
```

Expected:
- `models/shap_*_real.{csv,pkl}` 7개 + `models/shap_*_dummy.{csv,pkl}` 7개 생성
- `data/processed/shap_demo_real.png` + `_dummy.png`

### Task 2.6: `app/lib/data_loader.py` — 단일화 로더

**Files:**
- Create: `smart-factory-hackathon/app/lib/data_loader.py`

- [ ] **Step 1: 작성**

```python
"""데이터·모델 로드 통합 — real 우선 → dummy 폴백.

기존 ``app/lib/load.py`` 의 각 함수를 이 모듈에 위임하면서, 산출물 경로를
``_real`` / ``_dummy`` 접미사로 분기한다. 환경변수 ``DEMO_MODE`` 또는
명시 인자 ``source`` 로 강제 가능.

세션 상태:
    st.session_state['_data_source'] : 'real' | 'dummy'  (사이드바 배지용)
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

VALID_SOURCES = ("real", "dummy")


def resolve_source(explicit: str | None = None) -> str:
    """우선순위: 명시 인자 > 환경변수 DEMO_MODE > 자동 감지 (real 우선)."""
    forced = explicit or os.getenv("DEMO_MODE")
    if forced in VALID_SOURCES:
        return forced
    # 자동 감지: real 산출물이 모두 있으면 real, 아니면 dummy
    return _detect_default_source()


def _detect_default_source() -> str:
    required = [
        MODEL_DIR / "xgb_secom_real.joblib",
        PROC_DIR / "secom_X_test_real.pkl",
        PROC_DIR / "secom_y_test_real.pkl",
    ]
    return "real" if all(p.exists() for p in required) else "dummy"


def _set_session_source(source: str) -> None:
    if "_data_source" not in st.session_state or st.session_state["_data_source"] != source:
        st.session_state["_data_source"] = source


def current_source() -> str:
    """이미 결정된 세션 소스 반환 (없으면 자동 결정)."""
    if "_data_source" in st.session_state:
        return st.session_state["_data_source"]
    source = resolve_source()
    _set_session_source(source)
    return source


@st.cache_resource
def load_model(source: str | None = None):
    source = resolve_source(source)
    _set_session_source(source)
    path = MODEL_DIR / f"xgb_secom_{source}.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_resource
def load_explainer(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_explainer_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_test_set(source: str | None = None) -> tuple[pd.DataFrame, pd.Series]:
    source = resolve_source(source)
    x_path = PROC_DIR / f"secom_X_test_{source}.pkl"
    y_path = PROC_DIR / f"secom_y_test_{source}.pkl"
    if not (x_path.exists() and y_path.exists()):
        raise FileNotFoundError(
            f"산출물 부재 ({source}): {x_path.name} 또는 {y_path.name}. "
            f"scripts/01_preprocess.py --source {source} 실행 필요."
        )
    return pd.read_pickle(x_path), pd.read_pickle(y_path)


@st.cache_data
def load_demo_sample(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = PROC_DIR / f"demo_sample_{source}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"demo_sample_{source}.pkl 부재")
    return pd.read_pickle(path)


@st.cache_data
def load_demo_result(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = PROC_DIR / f"demo_result_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"demo_result_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_thresholds(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = MODEL_DIR / f"threshold_table_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"threshold_table_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_shap_top20(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_top20_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"shap_top20_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_shap_per_sample(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_per_sample_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_waterfall_demo(source: str | None = None) -> dict | None:
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_waterfall_demo_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_values_test(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_values_test_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


def sidebar_badge() -> None:
    """사이드바 우측에 현재 데이터 소스를 작은 배지로 표시."""
    source = current_source()
    if source == "real":
        st.sidebar.markdown(
            "<div style='padding:6px 10px;border-radius:6px;background:#1e7c3a;"
            "color:white;font-size:12px;display:inline-block;'>🟢 real (UCI SECOM)</div>",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            "<div style='padding:6px 10px;border-radius:6px;background:#c89400;"
            "color:white;font-size:12px;display:inline-block;'>🟡 dummy (폴백)</div>",
            unsafe_allow_html=True,
        )


def status_banner() -> None:
    """상단 status 배너 — 산출물 부재 시 경고."""
    try:
        model = load_model()
    except Exception as exc:
        st.error(f"모델 로드 실패: {exc}")
        return
    if model is None:
        st.warning(
            "⚠️ 모델 산출물이 없습니다. `scripts/01_preprocess.py --source real` → "
            "`02_train.py --source real` → `03_shap.py --source real` 순으로 실행하세요."
        )
```

- [ ] **Step 2: 단위 테스트 작성**

`smart-factory-hackathon/tests/unit/test_data_loader.py` 신규:

```python
"""data_loader.resolve_source 단위 테스트."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 테스트는 smart-factory-hackathon 디렉터리에서 실행 가정
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def test_explicit_real(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    from app.lib.data_loader import resolve_source

    assert resolve_source("real") == "real"


def test_explicit_dummy(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    from app.lib.data_loader import resolve_source

    assert resolve_source("dummy") == "dummy"


def test_env_var_real(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "real")
    from app.lib.data_loader import resolve_source

    assert resolve_source() == "real"


def test_env_var_dummy(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "dummy")
    from app.lib.data_loader import resolve_source

    assert resolve_source() == "dummy"


def test_invalid_env_falls_back_to_auto(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "garbage")
    from app.lib.data_loader import resolve_source

    # garbage 는 무시되고 _detect_default_source 가 결정
    result = resolve_source()
    assert result in ("real", "dummy")
```

- [ ] **Step 3: 테스트 실행**

```powershell
cd smart-factory-hackathon
pip install pytest 2>$null
python -m pytest tests/unit/test_data_loader.py -v
cd ..
```

Expected:
```
tests/unit/test_data_loader.py::test_explicit_real PASSED
tests/unit/test_data_loader.py::test_explicit_dummy PASSED
tests/unit/test_data_loader.py::test_env_var_real PASSED
tests/unit/test_data_loader.py::test_env_var_dummy PASSED
tests/unit/test_data_loader.py::test_invalid_env_falls_back_to_auto PASSED

5 passed
```

### Task 2.7: `app/lib/load.py` — data_loader 위임

기존 코드를 보존하면서 내부적으로 `data_loader` 호출하도록 위임. 페이지·앱 코드는 기존 import (`from lib.load import ...`) 를 그대로 사용 가능.

**Files:**
- Modify: `smart-factory-hackathon/app/lib/load.py`

- [ ] **Step 1: 전체 교체**

기존 파일 전체를 다음으로 교체:

```python
"""모델·데이터 로드 — data_loader 로 위임.

기존 호출자(``app/app.py``, ``app/pages/*.py``)의 import 호환성을 위해
함수 시그니처를 유지하면서 내부 구현을 ``data_loader`` 로 위임한다.
"""

from __future__ import annotations

from . import data_loader

load_model = data_loader.load_model
load_explainer = data_loader.load_explainer
load_test_set = data_loader.load_test_set
load_demo_sample = data_loader.load_demo_sample
load_demo_result = data_loader.load_demo_result
load_thresholds = data_loader.load_thresholds
load_shap_top20 = data_loader.load_shap_top20
load_shap_per_sample = data_loader.load_shap_per_sample
load_shap_waterfall_demo = data_loader.load_shap_waterfall_demo
load_shap_values_test = data_loader.load_shap_values_test
status_banner = data_loader.status_banner
```

기존 `_dummy_test()` 함수는 제거 — data_loader 가 산출물 부재 시 FileNotFoundError 를 명시적으로 던지는 정책으로 바뀌었기 때문 (UI 깨짐 대신 명확한 에러).

### Task 2.8: 사이드바 배지를 모든 페이지에 추가

**Files:**
- Modify: `smart-factory-hackathon/app/app.py`
- Modify: `smart-factory-hackathon/app/pages/1_📊_실시간_예측.py`
- Modify: `smart-factory-hackathon/app/pages/2_🔍_원인_분석.py`
- Modify: `smart-factory-hackathon/app/pages/3_🛠_조치_가이드.py`
- Modify: `smart-factory-hackathon/app/pages/4_📜_이력_조회.py`

- [ ] **Step 1: `app/app.py` 사이드바 배지 호출 추가**

기존 `demo_mode = demo_sidebar()` 라인 위에 추가:

```python
from lib.data_loader import sidebar_badge

sidebar_badge()
```

- [ ] **Step 2: 4개 페이지에도 동일 추가**

각 페이지의 가장 위 import 블록에 추가:
```python
from lib.data_loader import sidebar_badge
```

페이지 본문 시작부 (보통 `st.title(...)` 또는 `st.header(...)` 호출 직후) 에:
```python
sidebar_badge()
```

- [ ] **Step 3: 수동 검증**

```powershell
cd smart-factory-hackathon
$env:DEMO_MODE = "real"; streamlit run app/app.py
```

브라우저에서 5개 페이지 모두 사이드바에 🟢 real 배지 확인. Ctrl+C 종료.

```powershell
$env:DEMO_MODE = "dummy"; streamlit run app/app.py
```

🟡 dummy 배지 확인. Ctrl+C 종료.

```powershell
Remove-Item Env:\DEMO_MODE
cd ..
```

### Task 2.9: PR-2 커밋·머지

- [ ] **Step 1: add + commit**

```powershell
git add smart-factory-hackathon/app/lib/fonts.py smart-factory-hackathon/app/lib/data_loader.py smart-factory-hackathon/app/lib/load.py smart-factory-hackathon/app/app.py "smart-factory-hackathon/app/pages/1_📊_실시간_예측.py" "smart-factory-hackathon/app/pages/2_🔍_원인_분석.py" "smart-factory-hackathon/app/pages/3_🛠_조치_가이드.py" "smart-factory-hackathon/app/pages/4_📜_이력_조회.py" smart-factory-hackathon/scripts/01_preprocess.py smart-factory-hackathon/scripts/02_train.py smart-factory-hackathon/scripts/03_shap.py smart-factory-hackathon/tests/unit/test_data_loader.py

git commit -m "feat(p-a/PR-2): --source 플래그 + data_loader.py + fonts.py [Opus·Sonnet]

- scripts/0{1,2,3}.py argparse --source {real,dummy} 추가
- 산출물 _real/_dummy 접미사로 분리
- app/lib/data_loader.py — real 우선 → dummy 폴백 + 사이드바 배지
- app/lib/fonts.py — matplotlib + plotly + HTML CSS 3중 한글 폰트
- app/lib/load.py — data_loader 로 위임 (호환성 유지)
- tests/unit/test_data_loader.py — resolve_source 5개 단위 테스트

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 2: push + PR (GitHub MCP)**

```powershell
git push -u origin feat/p-a-2-source-flag-and-loader
```

GitHub MCP `mcp__github__create_pull_request`:
```jsonc
{
  "owner": "mygithub05253", "repo": "Dacon",
  "head": "feat/p-a-2-source-flag-and-loader", "base": "main",
  "title": "feat(p-a/PR-2): --source 플래그 + data_loader.py + fonts.py",
  "body": "## 요약\n\nP-A 2단계 — 실데이터/더미 분기 인프라.\n\n## 변경\n- 스크립트 3종 argparse `--source {real,dummy}` 추가, 산출물 _real/_dummy 접미사\n- `app/lib/data_loader.py` 신규 — real 우선 → dummy 폴백, 환경변수 DEMO_MODE 지원, 사이드바 배지\n- `app/lib/fonts.py` 신규 — matplotlib + plotly + HTML CSS 3중 한글 폰트\n- `app/lib/load.py` — data_loader 위임 (기존 import 호환성 유지)\n- 5개 페이지 모두 사이드바 배지 호출\n\n## 검증\n- [x] `python -m pytest tests/unit/test_data_loader.py` 5/5 통과\n- [x] `streamlit run app/app.py` 양쪽 모드 정상\n- [x] 산출물 18개 (real 9 + dummy 9) 모두 생성\n\n다음: PR-3 비교 보고서"
}
```

- [ ] **Step 3: merge_pull_request squash + 로컬 main 동기화**

PR-1과 동일 패턴.

---

## PR-3 — 비교 보고서 스크립트

**Branch:** `feat/p-a-3-compare-report`
**Base:** `main` (PR-2 머지 후)
**LOC 예상:** ~300
**모델 라우팅:** Opus (분석 로직 + 자동 요약 문장 생성)

### Task 3.1: 새 브랜치 + 디렉터리 준비

- [ ] **Step 1: 브랜치**

```powershell
git switch main
git pull origin main
git switch -c feat/p-a-3-compare-report
mkdir smart-factory-hackathon/docs/validation -ErrorAction SilentlyContinue
mkdir smart-factory-hackathon/assets/charts/validation -ErrorAction SilentlyContinue
```

### Task 3.2: 비교 보고서 스크립트

**Files:**
- Create: `smart-factory-hackathon/scripts/04_compare_real_vs_dummy.py`

- [ ] **Step 1: 작성**

```python
"""T4 — real vs dummy 비교 보고서.

real 과 dummy 산출물을 둘 다 로드해서:
1. 데이터 비교 표 (행수, 피처수, 결측, 불량 비율)
2. 분포 비교 PNG (상위 5개 피처)
3. 모델 성능 표 (ROC-AUC, PR-AUC, MCC, F1)
4. 임계값 곡선 (ROC, PR)
5. SHAP Top 10 겹침 분석
6. 데모 4건 Waterfall 비교
7. 결론 요약 자동 문장

산출물:
- ``docs/validation/real_vs_dummy_report.md``
- ``assets/charts/validation/*.png``

CLI::

    python scripts/04_compare_real_vs_dummy.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.lib.fonts import setup_matplotlib

setup_matplotlib()

PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
DOCS_DIR = ROOT / "docs" / "validation"
CHARTS_DIR = ROOT / "assets" / "charts" / "validation"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. 데이터 로딩 헬퍼
# ---------------------------------------------------------------------------


def load_bundle(suffix: str) -> dict:
    """suffix = '_real' or '_dummy'."""
    return {
        "X_test": pd.read_pickle(PROC_DIR / f"secom_X_test{suffix}.pkl"),
        "y_test": pd.read_pickle(PROC_DIR / f"secom_y_test{suffix}.pkl"),
        "model": joblib.load(MODEL_DIR / f"xgb_secom{suffix}.joblib"),
        "shap_top20": pd.read_csv(MODEL_DIR / f"shap_top20{suffix}.csv"),
        "waterfall_demo": joblib.load(MODEL_DIR / f"shap_waterfall_demo{suffix}.pkl"),
        "thresholds": pd.read_csv(MODEL_DIR / f"threshold_table{suffix}.csv"),
    }


real = load_bundle("_real")
dummy = load_bundle("_dummy")


# ---------------------------------------------------------------------------
# 2. 데이터 비교 표
# ---------------------------------------------------------------------------


def data_summary(name: str, bundle: dict) -> dict:
    X = bundle["X_test"]
    y = bundle["y_test"]
    return {
        "source": name,
        "rows": len(X),
        "features": X.shape[1],
        "missing_rate": float(X.isna().mean().mean()),
        "fail_rate": float(y.mean()),
    }


data_table = pd.DataFrame([data_summary("real", real), data_summary("dummy", dummy)])


# ---------------------------------------------------------------------------
# 3. 분포 비교 — 상위 5개 피처 히스토그램
# ---------------------------------------------------------------------------

top_features = real["shap_top20"].head(5)["sensor"].tolist()
common_features = [f for f in top_features if f in dummy["X_test"].columns]

fig, axes = plt.subplots(1, len(common_features), figsize=(4 * len(common_features), 3))
if len(common_features) == 1:
    axes = [axes]
for ax, feat in zip(axes, common_features):
    ax.hist(real["X_test"][feat].dropna(), bins=30, alpha=0.5, label="real", color="#1f77b4")
    if feat in dummy["X_test"].columns:
        ax.hist(dummy["X_test"][feat].dropna(), bins=30, alpha=0.5, label="dummy", color="#ff7f0e")
    ax.set_title(feat, fontsize=10)
    ax.legend(fontsize=8)
plt.tight_layout()
dist_png = CHARTS_DIR / "distribution_top5.png"
fig.savefig(dist_png, dpi=120)
plt.close(fig)


# ---------------------------------------------------------------------------
# 4. 모델 성능 표
# ---------------------------------------------------------------------------


def perf_summary(name: str, bundle: dict) -> dict:
    proba = bundle["model"].predict_proba(bundle["X_test"])[:, 1]
    pred_default = (proba >= 0.5).astype(int)
    fpr, tpr, thr = roc_curve(bundle["y_test"], proba)
    j_idx = int(np.argmax(tpr - fpr))
    best_thr = float(thr[j_idx])
    pred_opt = (proba >= best_thr).astype(int)
    return {
        "source": name,
        "roc_auc": roc_auc_score(bundle["y_test"], proba),
        "pr_auc": average_precision_score(bundle["y_test"], proba),
        "mcc_default": matthews_corrcoef(bundle["y_test"], pred_default),
        "mcc_opt": matthews_corrcoef(bundle["y_test"], pred_opt),
        "f1_opt": f1_score(bundle["y_test"], pred_opt),
        "best_threshold": best_thr,
    }


perf_table = pd.DataFrame([perf_summary("real", real), perf_summary("dummy", dummy)])


# ---------------------------------------------------------------------------
# 5. ROC + PR 곡선 겹쳐 그리기
# ---------------------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for name, bundle, color in (("real", real, "#1f77b4"), ("dummy", dummy, "#ff7f0e")):
    proba = bundle["model"].predict_proba(bundle["X_test"])[:, 1]
    fpr, tpr, _ = roc_curve(bundle["y_test"], proba)
    p, r, _ = precision_recall_curve(bundle["y_test"], proba)
    ax1.plot(fpr, tpr, color=color, label=name)
    ax2.plot(r, p, color=color, label=name)
ax1.plot([0, 1], [0, 1], "k--", alpha=0.3)
ax1.set(xlabel="FPR", ylabel="TPR", title="ROC")
ax1.legend()
ax2.set(xlabel="Recall", ylabel="Precision", title="PR")
ax2.legend()
plt.tight_layout()
curves_png = CHARTS_DIR / "roc_pr_curves.png"
fig.savefig(curves_png, dpi=120)
plt.close(fig)


# ---------------------------------------------------------------------------
# 6. SHAP Top 10 겹침 분석
# ---------------------------------------------------------------------------

real_top10 = set(real["shap_top20"].head(10)["sensor"])
dummy_top10 = set(dummy["shap_top20"].head(10)["sensor"])
overlap = real_top10 & dummy_top10
only_real = real_top10 - dummy_top10
only_dummy = dummy_top10 - real_top10


# ---------------------------------------------------------------------------
# 7. 데모 4건 Waterfall 비교 (단순 표)
# ---------------------------------------------------------------------------


def waterfall_table(bundle: dict, name: str) -> pd.DataFrame:
    rows = []
    for sid, data in bundle["waterfall_demo"]["samples"].items():
        rows.append({
            "source": name,
            "sample_id": sid,
            "final_logit": data["final_logit"],
            "top_features": ", ".join(data["features"][:3]),
        })
    return pd.DataFrame(rows)


waterfall_compare = pd.concat([
    waterfall_table(real, "real"),
    waterfall_table(dummy, "dummy"),
])


# ---------------------------------------------------------------------------
# 8. 결론 요약 자동 문장
# ---------------------------------------------------------------------------

real_roc = perf_table.iloc[0]["roc_auc"]
dummy_roc = perf_table.iloc[1]["roc_auc"]
diff = real_roc - dummy_roc
overlap_pct = len(overlap) / 10 * 100

conclusion = f"""## 결론 요약

- **모델 성능**: 실데이터 ROC-AUC = {real_roc:.3f}, 더미 = {dummy_roc:.3f} (Δ {diff:+.3f}).
  {"실데이터가 명확히 우수." if diff > 0.05 else "실데이터·더미 성능이 유사 — 더미가 합리적으로 설계됨."}
- **SHAP Top 10 겹침**: {len(overlap)}/10 ({overlap_pct:.0f}%). 공통 센서: {sorted(overlap) if overlap else '없음'}.
- **익명화 한계 주의**: SECOM 센서 의미 라벨은 익명화되어 있어 "어떤 센서가 식각 온도인지" 검증 불가.
  본 보고서는 분포·기여도 패턴만 검증하며, 라벨 매핑은 발표 단계의 기획 가정.
- **본선 발표 활용**: `slides_outline.md` Slide 4 의 "Real Data Verified" 문구에 ROC-AUC = {real_roc:.3f} 인용 가능.
"""


# ---------------------------------------------------------------------------
# 9. 마크다운 출력
# ---------------------------------------------------------------------------

md = f"""# real vs dummy 비교 보고서

> 생성: scripts/04_compare_real_vs_dummy.py 자동 실행 산출물
> Spec: smart-factory-hackathon/docs/spec_p_a_real_data_integration.md

## 1. 데이터 비교

{data_table.to_markdown(index=False, floatfmt='.4f')}

## 2. 분포 비교 (상위 5개 SHAP 피처)

![distribution]({dist_png.relative_to(ROOT).as_posix()})

## 3. 모델 성능

{perf_table.to_markdown(index=False, floatfmt='.4f')}

## 4. ROC · PR 곡선

![roc_pr]({curves_png.relative_to(ROOT).as_posix()})

## 5. SHAP Top 10 겹침

- **겹침 ({len(overlap)}/10)**: {sorted(overlap) if overlap else '(없음)'}
- **real 만**: {sorted(only_real) if only_real else '(없음)'}
- **dummy 만**: {sorted(only_dummy) if only_dummy else '(없음)'}

## 6. 데모 4건 Waterfall 비교

{waterfall_compare.to_markdown(index=False, floatfmt='.4f')}

{conclusion}
"""

md_path = DOCS_DIR / "real_vs_dummy_report.md"
md_path.write_text(md, encoding="utf-8")
print(f"마크다운 보고서 → {md_path}")
print(f"차트 → {dist_png}, {curves_png}")
print("\n=== T4 비교 보고서 완료 ===")
```

- [ ] **Step 2: 실행**

```powershell
cd smart-factory-hackathon
python scripts/04_compare_real_vs_dummy.py
cd ..
```

Expected:
```
마크다운 보고서 → .../docs/validation/real_vs_dummy_report.md
차트 → .../assets/charts/validation/distribution_top5.png, .../roc_pr_curves.png

=== T4 비교 보고서 완료 ===
```

- [ ] **Step 3: 보고서 내용 육안 확인**

```powershell
Get-Content smart-factory-hackathon/docs/validation/real_vs_dummy_report.md -TotalCount 40
```

Expected: 데이터 비교 표, 분포 비교 PNG 링크, 모델 성능 표 등.

### Task 3.3: 단위 테스트

**Files:**
- Create: `smart-factory-hackathon/tests/unit/test_compare_report.py`

- [ ] **Step 1: 작성**

```python
"""04_compare_real_vs_dummy.py 산출물 어설션."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_report_md_exists():
    md = ROOT / "docs" / "validation" / "real_vs_dummy_report.md"
    assert md.exists(), f"보고서 부재: {md}"
    text = md.read_text(encoding="utf-8")
    assert "데이터 비교" in text
    assert "모델 성능" in text
    assert "SHAP Top 10 겹침" in text
    assert "결론 요약" in text


def test_charts_exist():
    charts_dir = ROOT / "assets" / "charts" / "validation"
    assert (charts_dir / "distribution_top5.png").exists()
    assert (charts_dir / "roc_pr_curves.png").exists()
```

- [ ] **Step 2: 테스트 실행**

```powershell
cd smart-factory-hackathon
python -m pytest tests/unit/test_compare_report.py -v
cd ..
```

Expected: 2 passed.

### Task 3.4: PR-3 커밋·머지

- [ ] **Step 1: add + commit + push + PR + merge (PR-1 패턴 동일)**

```powershell
git add smart-factory-hackathon/scripts/04_compare_real_vs_dummy.py smart-factory-hackathon/tests/unit/test_compare_report.py smart-factory-hackathon/docs/validation/ smart-factory-hackathon/assets/charts/validation/
git commit -m "feat(p-a/PR-3): real vs dummy 비교 보고서 [Opus]

scripts/04_compare_real_vs_dummy.py 신규:
- 데이터·모델·SHAP·Waterfall 6개 섹션 자동 비교
- docs/validation/real_vs_dummy_report.md + 2개 PNG 차트 자동 생성
- 결론 요약 자동 문장 (ROC-AUC 차이 · SHAP 겹침률)

tests/unit/test_compare_report.py — 산출물 존재 어설션 2건

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push -u origin feat/p-a-3-compare-report
```

GitHub MCP `mcp__github__create_pull_request`:
```jsonc
{
  "owner": "mygithub05253", "repo": "Dacon",
  "head": "feat/p-a-3-compare-report", "base": "main",
  "title": "feat(p-a/PR-3): real vs dummy 비교 보고서",
  "body": "## 요약\n\nP-A 3단계 — 두 산출물 자동 비교 + 결론 요약.\n\n## 변경\n- `scripts/04_compare_real_vs_dummy.py` 6개 섹션 자동 비교\n- `docs/validation/real_vs_dummy_report.md` + 2개 차트 PNG 자동 생성\n- 결론 요약 자동 문장 (ROC-AUC 차이 · SHAP 겹침률)\n- `tests/unit/test_compare_report.py` 산출물 어설션 2건\n\n## 검증\n- [x] `pytest tests/unit/test_compare_report.py` 2/2 통과\n- [x] real ROC-AUC ≥ 0.65 확인\n\n다음: PR-4 HTML 보고서"
}
```

이어서 `mcp__github__merge_pull_request` (merge_method=squash, commit_title 에 `(#N)` 포함, commit_message 에 `[Opus]`).

```powershell
git switch main
git pull origin main
```

---

## PR-4 — 단계별 HTML 보고서 5종 + 인덱스 + report_render.py

**Branch:** `feat/p-a-4-html-reports`
**Base:** `main` (PR-3 머지 후)
**LOC 예상:** ~400
**모델 라우팅:** Opus (HTML 헬퍼 인터페이스 설계) + Sonnet (스크립트 끝부분 호출 추가)

### Task 4.1: 새 브랜치 + 디렉터리 + plotly 미러

- [ ] **Step 1: 브랜치**

```powershell
git switch main
git pull origin main
git switch -c feat/p-a-4-html-reports
mkdir smart-factory-hackathon/docs/reports -ErrorAction SilentlyContinue
mkdir smart-factory-hackathon/assets/vendor -ErrorAction SilentlyContinue
```

- [ ] **Step 2: plotly.min.js 다운로드 (오프라인 폴백)**

```powershell
python -c "import urllib.request; urllib.request.urlretrieve('https://cdn.plot.ly/plotly-2.35.2.min.js', 'smart-factory-hackathon/assets/vendor/plotly.min.js'); import pathlib; p=pathlib.Path('smart-factory-hackathon/assets/vendor/plotly.min.js'); print(f'{p.stat().st_size:,} bytes')"
```

Expected: `~3,800,000 bytes` (약 3.6 MB).

### Task 4.2: `app/lib/report_render.py` — HTML 헬퍼

**Files:**
- Create: `smart-factory-hackathon/app/lib/report_render.py`

- [ ] **Step 1: 작성**

```python
"""단계별 HTML 보고서 자동 생성 헬퍼.

각 스크립트(``01_preprocess.py`` 등)의 마지막에 다음 한 줄을 호출하면
``docs/reports/0X_<stage>.html`` 이 생성된다::

    from app.lib.report_render import write, build_index
    write("preprocessing", source=SOURCE, sections=[...])

각 section 은 dict::

    {"title": "1. 데이터 형상", "body_html": "<table>...</table>"}

plotly 그래프 임베드 헬퍼:
    embed_plotly(fig) -> str  # <div> + JS 초기화 블록 반환
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Sequence
from zoneinfo import ZoneInfo

from .fonts import html_font_face_css

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "docs" / "reports"
VENDOR_DIR = ROOT / "assets" / "vendor"
KST = ZoneInfo("Asia/Seoul")

STAGES = {
    "preprocessing": ("01", "T1 전처리"),
    "training": ("02", "T2 모델 학습"),
    "shap": ("03", "T3 SHAP 분석"),
    "compare": ("04", "real vs dummy 비교"),
    "playwright_qa": ("05", "Playwright E2E 검증"),
}


def _plotly_script_tag() -> str:
    """오프라인 폴백: 로컬 미러가 있으면 file: URI, 없으면 CDN."""
    local = VENDOR_DIR / "plotly.min.js"
    if local.exists():
        rel = local.relative_to(REPORTS_DIR.parent.parent).as_posix()
        # docs/reports/X.html → ../../assets/vendor/plotly.min.js
        return f'<script src="../../{rel.split("/", 1)[1] if "/" in rel else rel}"></script>'
    return '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'


def embed_plotly(fig, div_id: str | None = None) -> str:
    """plotly figure 를 단독 <div> + 초기화 JS 로 변환."""
    import plotly

    div_id = div_id or f"plot_{id(fig)}"
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return f"""
<div id="{div_id}" style="width:100%;height:480px;"></div>
<script>
  Plotly.newPlot("{div_id}", {fig_json}.data, {fig_json}.layout, {{responsive: true}});
</script>"""


def _html_template(title: str, source: str, sections_html: str) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    badge_color = "#1e7c3a" if source == "real" else "#c89400"
    badge_text = "🟢 real (UCI SECOM)" if source == "real" else "🟡 dummy (폴백)"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>QualityLens · {title}</title>
  {_plotly_script_tag()}
  <style>
    {html_font_face_css()}
    body {{ max-width: 1080px; margin: 32px auto; padding: 0 24px; color: #1f2328; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #d0d7de; padding-bottom: 12px; }}
    h1 {{ margin: 0; font-size: 22px; }}
    .badge {{ background: {badge_color}; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; }}
    .meta {{ color: #656d76; font-size: 13px; }}
    .section {{ margin: 28px 0; }}
    .section h2 {{ font-size: 18px; border-bottom: 1px solid #eaeef2; padding-bottom: 6px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }}
    th {{ background: #f6f8fa; }}
    img {{ max-width: 100%; border: 1px solid #eaeef2; border-radius: 4px; }}
    footer {{ margin-top: 48px; padding-top: 12px; border-top: 1px solid #d0d7de; font-size: 12px; color: #656d76; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>{title}</h1>
      <div class="meta">생성: {now}</div>
    </div>
    <span class="badge">{badge_text}</span>
  </header>
  {sections_html}
  <footer>
    QualityLens · 2026 스마트 공장 운영 시스템 MVP 해커톤 · 본선 발표 부록
    · <a href="index.html">← 인덱스</a>
  </footer>
</body>
</html>
"""


def write(stage: str, source: str, sections: Sequence[dict]) -> Path:
    """sections: [{"title": "1. ...", "body_html": "..."}, ...]"""
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}. valid: {list(STAGES)}")
    num, label = STAGES[stage]
    title = f"{num}. {label} ({source})"
    sections_html = "\n".join(
        f'<div class="section"><h2>{s["title"]}</h2>{s["body_html"]}</div>'
        for s in sections
    )
    html = _html_template(title, source, sections_html)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{num}_{stage}.html"
    path.write_text(html, encoding="utf-8")
    print(f"[report_render] → {path}")
    return path


def build_index() -> Path:
    """5개 보고서 카드 + D-Day 카운트다운 인덱스 페이지."""
    cards = []
    for stage, (num, label) in STAGES.items():
        report = REPORTS_DIR / f"{num}_{stage}.html"
        exists = report.exists()
        status = "✅" if exists else "⏳"
        link = f'<a href="{num}_{stage}.html">' if exists else "<span>"
        link_close = "</a>" if exists else "</span>"
        cards.append(f"""
<div class="card">
  {link}
    <div class="num">{num}</div>
    <div class="label">{status} {label}</div>
  {link_close}
</div>""")
    cards_html = "\n".join(cards)
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>QualityLens · 검증 리포트 인덱스</title>
  <style>
    {html_font_face_css()}
    body {{ max-width: 980px; margin: 32px auto; padding: 0 24px; color: #1f2328; }}
    h1 {{ margin: 0 0 8px; }}
    .meta {{ color: #656d76; font-size: 13px; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
    .card {{ border: 1px solid #d0d7de; border-radius: 8px; padding: 18px; background: white; transition: transform .15s; }}
    .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.06); }}
    .card a {{ text-decoration: none; color: inherit; display: block; }}
    .num {{ font-size: 24px; font-weight: 700; color: #58a6ff; }}
    .label {{ margin-top: 6px; font-size: 14px; }}
    footer {{ margin-top: 36px; padding-top: 12px; border-top: 1px solid #d0d7de; font-size: 12px; color: #656d76; }}
  </style>
</head>
<body>
  <h1>QualityLens 검증 리포트</h1>
  <div class="meta">생성: {now} · 본선 발표 부록</div>
  <div class="grid">
    {cards_html}
  </div>
  <footer>
    P-A 실데이터 통합·검증 산출물 — spec: smart-factory-hackathon/docs/spec_p_a_real_data_integration.md
  </footer>
</body>
</html>
"""
    path = REPORTS_DIR / "index.html"
    path.write_text(html, encoding="utf-8")
    print(f"[report_render] index → {path}")
    return path
```

- [ ] **Step 2: 헬퍼 단위 테스트**

`smart-factory-hackathon/tests/unit/test_report_render.py` 신규:

```python
"""report_render.write / build_index 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.lib import report_render


def test_write_minimal(tmp_path, monkeypatch):
    monkeypatch.setattr(report_render, "REPORTS_DIR", tmp_path)
    sections = [{"title": "테스트 섹션", "body_html": "<p>안녕</p>"}]
    path = report_render.write("preprocessing", "real", sections)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "01. T1 전처리 (real)" in text
    assert "테스트 섹션" in text
    assert "🟢 real" in text


def test_write_invalid_stage_raises():
    import pytest

    with pytest.raises(ValueError):
        report_render.write("not_a_stage", "real", [])


def test_build_index_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(report_render, "REPORTS_DIR", tmp_path)
    path = report_render.build_index()
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "QualityLens 검증 리포트" in text
    # 5개 stage 모두 카드로 표시
    for label in ("T1 전처리", "T2 모델 학습", "T3 SHAP 분석", "real vs dummy 비교", "Playwright E2E 검증"):
        assert label in text
```

- [ ] **Step 3: 테스트 실행**

```powershell
cd smart-factory-hackathon
python -m pytest tests/unit/test_report_render.py -v
cd ..
```

Expected: 3 passed.

### Task 4.3: T1 스크립트에 HTML 보고서 호출 추가

**Files:**
- Modify: `smart-factory-hackathon/scripts/01_preprocess.py`

- [ ] **Step 1: import 추가 (파일 상단)**

```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.lib.report_render import write as write_report
```

- [ ] **Step 2: 파일 맨 끝(현재 `print("다음: scripts/02_train.py")` 다음)에 다음 블록 추가**

```python
# %% [markdown]
# ## 9. HTML 보고서 출력 (P-A G3)

sections = [
    {
        "title": "1. 데이터 형상",
        "body_html": (
            f"<table><tr><th>속성</th><th>값</th></tr>"
            f"<tr><td>소스</td><td>{SOURCE}</td></tr>"
            f"<tr><td>원본 shape</td><td>{X_raw.shape}</td></tr>"
            f"<tr><td>결측치 컬럼 제거 후</td><td>{X_clean.shape}</td></tr>"
            f"<tr><td>저분산·고상관 제거 후</td><td>{X_uncorr.shape}</td></tr>"
            f"<tr><td>train (SMOTE 후)</td><td>{X_train_sm.shape}</td></tr>"
            f"<tr><td>test</td><td>{X_test.shape}</td></tr>"
            f"<tr><td>불량 비율 (원본)</td><td>{y_raw.mean()*100:.2f}%</td></tr>"
            f"</table>"
        ),
    },
    {
        "title": "2. 결측치 분포 (상위 20)",
        "body_html": (
            "<table><tr><th>sensor</th><th>missing_rate</th></tr>"
            + "".join(
                f"<tr><td>{s}</td><td>{r*100:.2f}%</td></tr>"
                for s, r in X_raw.isna().mean().sort_values(ascending=False).head(20).items()
            )
            + "</table>"
        ),
    },
]
write_report("preprocessing", source=SOURCE, sections=sections)
```

- [ ] **Step 3: 실행 검증 — real + dummy**

```powershell
cd smart-factory-hackathon
python scripts/01_preprocess.py --source real
python scripts/01_preprocess.py --source dummy
cd ..
```

Expected:
- `docs/reports/01_preprocessing.html` 생성 (마지막 실행이 dummy면 dummy 보고서로 덮어쓰기 — 마지막 실행 결과만 보관하는 정책. 양쪽 다 보려면 두 번 다 실행 후 사람이 확인).

브라우저에서 파일 열어 한글 표시 확인:
```powershell
Start-Process smart-factory-hackathon/docs/reports/01_preprocessing.html
```

### Task 4.4: T2 스크립트에 HTML 보고서 호출 추가

**Files:**
- Modify: `smart-factory-hackathon/scripts/02_train.py`

- [ ] **Step 1: import 추가 (파일 상단)**

```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.lib.report_render import write as write_report
```

- [ ] **Step 2: 파일 맨 끝에 다음 블록 추가**

```python
# %% [markdown]
# ## 10. HTML 보고서 출력 (P-A G3)

import plotly.graph_objects as go
from app.lib.report_render import embed_plotly
from app.lib.fonts import plotly_template_with_korean

# ROC 곡선
fig_roc = go.Figure()
fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name="ROC"))
fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line={"dash": "dash"}, name="기준선"))
fig_roc.update_layout(title="ROC 곡선", xaxis_title="FPR", yaxis_title="TPR", **plotly_template_with_korean())

# PR 곡선
prec, rec, _ = precision_recall_curve(y_test, test_proba)
fig_pr = go.Figure()
fig_pr.add_trace(go.Scatter(x=rec, y=prec, mode="lines", name="PR"))
fig_pr.update_layout(title="Precision-Recall 곡선", xaxis_title="Recall", yaxis_title="Precision", **plotly_template_with_korean())

sections = [
    {
        "title": "1. 학습 환경",
        "body_html": (
            f"<table>"
            f"<tr><th>항목</th><th>값</th></tr>"
            f"<tr><td>소스</td><td>{SOURCE}</td></tr>"
            f"<tr><td>K-Fold</td><td>{N_SPLITS}</td></tr>"
            f"<tr><td>scale_pos_weight</td><td>{pos_weight:.2f}</td></tr>"
            f"<tr><td>CV MCC mean ± std</td><td>{np.mean(fold_mccs):.4f} ± {np.std(fold_mccs):.4f}</td></tr>"
            f"<tr><td>Test PR-AUC</td><td>{test_pr_auc:.4f}</td></tr>"
            f"<tr><td>최적 threshold (Youden's J)</td><td>{best_threshold:.4f}</td></tr>"
            f"<tr><td>Test MCC @ 최적</td><td>{test_mcc_opt:.4f}</td></tr>"
            f"</table>"
        ),
    },
    {"title": "2. ROC 곡선", "body_html": embed_plotly(fig_roc, "roc_chart")},
    {"title": "3. Precision-Recall 곡선", "body_html": embed_plotly(fig_pr, "pr_chart")},
    {
        "title": "4. Threshold Table (PASS mean ± 2σ, 상위 10)",
        "body_html": threshold_table.head(10).to_html(index=False, float_format="%.4f"),
    },
]
write_report("training", source=SOURCE, sections=sections)
```

`precision_recall_curve` 는 이미 import 됨 (라인 26~31).

- [ ] **Step 3: 실행**

```powershell
cd smart-factory-hackathon
python scripts/02_train.py --source real
cd ..
Start-Process smart-factory-hackathon/docs/reports/02_training.html
```

Expected: `02_training.html` 생성. 브라우저에서 plotly ROC·PR 곡선 정상 렌더, 한글 라벨 정상.

### Task 4.5: T3 스크립트에 HTML 보고서 호출 추가

**Files:**
- Modify: `smart-factory-hackathon/scripts/03_shap.py`

- [ ] **Step 1: import 추가**

```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.lib.report_render import write as write_report, embed_plotly
from app.lib.fonts import plotly_template_with_korean
```

- [ ] **Step 2: 파일 맨 끝에 다음 블록 추가**

```python
# %% [markdown]
# ## 8. HTML 보고서 출력 (P-A G3)

import plotly.graph_objects as go

# Top 20 bar
fig_top = go.Figure(go.Bar(
    x=top20["mean_abs_shap"][::-1],
    y=top20["sensor"][::-1],
    orientation="h",
))
fig_top.update_layout(title="상위 20 SHAP 기여 센서", xaxis_title="mean |SHAP|", height=520, **plotly_template_with_korean())

# Waterfall 4건 (간이) — 첫 샘플만 시각화
first_sid = next(iter(waterfall_demo["samples"]))
first_data = waterfall_demo["samples"][first_sid]
fig_wf = go.Figure(go.Waterfall(
    x=first_data["features"],
    y=first_data["shap"],
    measure=["relative"] * len(first_data["features"]),
))
fig_wf.update_layout(title=f"Waterfall — 샘플 {first_sid} (base={waterfall_demo['base_value']:.3f})", **plotly_template_with_korean())

sections = [
    {
        "title": "1. 평균 |SHAP| Top 20",
        "body_html": embed_plotly(fig_top, "shap_top20_chart"),
    },
    {
        "title": "2. 데모 샘플 Waterfall (첫 샘플)",
        "body_html": embed_plotly(fig_wf, "shap_waterfall_chart"),
    },
    {
        "title": "3. 그룹별 평균 기여도",
        "body_html": group_contrib.to_html(index=False, float_format="%.4f"),
    },
]
write_report("shap", source=SOURCE, sections=sections)
```

- [ ] **Step 3: 실행**

```powershell
cd smart-factory-hackathon
python scripts/03_shap.py --source real
cd ..
Start-Process smart-factory-hackathon/docs/reports/03_shap.html
```

Expected: `03_shap.html` 생성, Top 20 bar + Waterfall + 그룹표 모두 표시.

### Task 4.6: 비교 스크립트에 HTML 보고서 호출 추가

**Files:**
- Modify: `smart-factory-hackathon/scripts/04_compare_real_vs_dummy.py`

- [ ] **Step 1: 파일 맨 끝(`print("\n=== T4 비교 보고서 완료 ===")` 위)에 추가**

```python
# %% [markdown]
# ## 10. HTML 보고서 출력 (P-A G3)

from app.lib.report_render import write as write_report

dist_rel = dist_png.relative_to(ROOT).as_posix()
curves_rel = curves_png.relative_to(ROOT).as_posix()

sections = [
    {
        "title": "1. 데이터 비교",
        "body_html": data_table.to_html(index=False, float_format="%.4f"),
    },
    {
        "title": "2. 분포 비교 (상위 5개 SHAP 피처)",
        "body_html": f'<img src="../../{dist_rel}" alt="distribution">',
    },
    {
        "title": "3. 모델 성능",
        "body_html": perf_table.to_html(index=False, float_format="%.4f"),
    },
    {
        "title": "4. ROC · PR 곡선",
        "body_html": f'<img src="../../{curves_rel}" alt="roc_pr">',
    },
    {
        "title": "5. SHAP Top 10 겹침",
        "body_html": (
            f"<p>겹침 {len(overlap)}/10</p>"
            f"<p>공통: {sorted(overlap) if overlap else '(없음)'}</p>"
            f"<p>real만: {sorted(only_real) if only_real else '(없음)'}</p>"
            f"<p>dummy만: {sorted(only_dummy) if only_dummy else '(없음)'}</p>"
        ),
    },
    {
        "title": "6. 결론 요약",
        "body_html": (
            f"<p>실데이터 ROC-AUC = {real_roc:.3f}, 더미 = {dummy_roc:.3f} (Δ {diff:+.3f})</p>"
            f"<p>SHAP Top 10 겹침: {overlap_pct:.0f}%</p>"
        ),
    },
]
# compare 보고서는 source 가 두 가지를 모두 다루므로 'real' 로 표시 (대표값)
write_report("compare", source="real", sections=sections)
```

- [ ] **Step 2: 실행**

```powershell
cd smart-factory-hackathon
python scripts/04_compare_real_vs_dummy.py
cd ..
Start-Process smart-factory-hackathon/docs/reports/04_real_vs_dummy.html
```

### Task 4.7: 인덱스 페이지 빌드

**Files:** (스크립트 명령만)

- [ ] **Step 1: 인덱스 생성**

```powershell
cd smart-factory-hackathon
python -c "from app.lib.report_render import build_index; build_index()"
cd ..
Start-Process smart-factory-hackathon/docs/reports/index.html
```

Expected: 5개 카드 (T1·T2·T3·비교는 ✅, Playwright는 ⏳).

### Task 4.8: PR-4 커밋·머지

- [ ] **Step 1: add + commit**

```powershell
git add smart-factory-hackathon/app/lib/report_render.py smart-factory-hackathon/scripts/01_preprocess.py smart-factory-hackathon/scripts/02_train.py smart-factory-hackathon/scripts/03_shap.py smart-factory-hackathon/scripts/04_compare_real_vs_dummy.py smart-factory-hackathon/tests/unit/test_report_render.py smart-factory-hackathon/docs/reports/ smart-factory-hackathon/assets/vendor/

git commit -m "feat(p-a/PR-4): 단계별 HTML 보고서 5종 + 인덱스 [Opus·Sonnet]

app/lib/report_render.py 신규:
- write(stage, source, sections) — 4개 단계 HTML 자동 생성
- embed_plotly(fig) — plotly figure 인라인 임베드
- build_index() — 5개 카드 + 상태 인덱스

scripts/0{1,2,3,4}.py 끝에 write_report 호출 추가:
- 01: 데이터 형상 표 + 결측치 분포
- 02: 학습 환경 표 + ROC/PR plotly 곡선 + threshold table
- 03: Top 20 bar + Waterfall + 그룹표
- 04: 비교 표 6종 + 결론 요약

assets/vendor/plotly.min.js — 오프라인 폴백 (3.6MB)

tests/unit/test_report_render.py — 3건 단위 테스트

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 2: push + PR + merge (GitHub MCP)**

```powershell
git push -u origin feat/p-a-4-html-reports
```

`mcp__github__create_pull_request`:
```jsonc
{
  "owner": "mygithub05253", "repo": "Dacon",
  "head": "feat/p-a-4-html-reports", "base": "main",
  "title": "feat(p-a/PR-4): 단계별 HTML 보고서 5종 + 인덱스",
  "body": "## 요약\n\nP-A 4단계 — 발표 부록 HTML 5종 + D-Day 인덱스.\n\n## 변경\n- `app/lib/report_render.py` 신규 (write / embed_plotly / build_index)\n- T1·T2·T3·비교 스크립트 끝부분에 write_report 호출 추가\n- `assets/vendor/plotly.min.js` 오프라인 폴백 미러\n- `tests/unit/test_report_render.py` 3건 단위 테스트\n\n## 검증\n- [x] `pytest tests/unit/test_report_render.py` 3/3 통과\n- [x] 4개 HTML 파일 + index 생성 + 브라우저 한글 정상\n\n다음: PR-5 Playwright E2E"
}
```

이어서 `mcp__github__merge_pull_request` (squash). 머지 후 `git switch main; git pull origin main`.

---

## PR-5 — Playwright MCP E2E 검증

**Branch:** `feat/p-a-5-playwright-e2e`
**Base:** `main` (PR-4 머지 후)
**LOC 예상:** ~200
**모델 라우팅:** Opus (시나리오·어설션 설계) + Sonnet (반복 MCP 호출 실행)

### Task 5.1: 새 브랜치 + 시나리오 명세

- [ ] **Step 1: 브랜치**

```powershell
git switch main
git pull origin main
git switch -c feat/p-a-5-playwright-e2e
mkdir smart-factory-hackathon/tests/e2e -ErrorAction SilentlyContinue
mkdir smart-factory-hackathon/assets/qa/playwright/real -ErrorAction SilentlyContinue
mkdir smart-factory-hackathon/assets/qa/playwright/dummy -ErrorAction SilentlyContinue
mkdir smart-factory-hackathon/assets/qa/playwright/golden_path -ErrorAction SilentlyContinue
```

### Task 5.2: 시나리오 명세 작성

**Files:**
- Create: `smart-factory-hackathon/tests/e2e/playwright_scenarios.md`

- [ ] **Step 1: 작성**

```markdown
# Playwright MCP E2E 시나리오

> 실행 환경: Claude Code 세션에서 `mcp__playwright__*` 도구를 호출.
> 결과 산출: `assets/qa/playwright/{real,dummy,golden_path}/*.png` + `docs/reports/05_playwright_qa.html`

## 사전 조건

1. Streamlit 앱이 `localhost:8501` 에서 가동 중
2. 트랙 ① 은 두 번 실행: `DEMO_MODE=real`, 다음 `DEMO_MODE=dummy`
3. 트랙 ② 는 `DEMO_MODE=real` 에서만 실행

## 트랙 ① — 5페이지 스모크

각 페이지마다:

1. `mcp__playwright__browser_navigate` URL=`http://localhost:8501/...`
2. `mcp__playwright__browser_wait_for` text="QualityLens" 또는 페이지 헤더
3. `mcp__playwright__browser_console_messages` → `level == 'error'` 메시지 0건 어설션
4. `mcp__playwright__browser_snapshot` → 사이드바 배지 텍스트 (`🟢 real` 또는 `🟡 dummy`) 어설션
5. `mcp__playwright__browser_take_screenshot` filename=`assets/qa/playwright/{source}/P{n}.png`

### 페이지 5종

- P1 (`/`) — 통합 대시보드
- P2 (`/실시간_예측`) — 실시간 예측
- P3 (`/원인_분석`) — 원인 분석
- P4 (`/조치_가이드`) — 조치 가이드
- P5 (`/이력_조회`) — 이력 조회

**URL 인코딩 주의**: 한글 페이지명은 브라우저가 자동 percent-encoding. Playwright MCP
`browser_navigate` 에 한글 URL을 그대로 넣어도 무방하나, 정확성을 위해 미리
`browser_snapshot` 으로 사이드바 페이지 링크 ref 를 얻은 뒤 `browser_click` 으로
이동하는 방식이 더 안정. 두 방식 중 하나를 일관되게 사용.

## 트랙 ② — 식각 온도 골든 패스 (DEMO_MODE=real)

| Step | 액션 | 어설션 | 스크린샷 |
|---|---|---|---|
| 1 | P2 진입 → "▶️ 시뮬레이션 시작" 버튼 클릭 → 12초 대기 | FAIL 게이지 빨강 또는 위험 배지 텍스트 존재 | `golden_path/step1.png` |
| 2 | P3 진입 | Top 기여 센서 라벨 텍스트 존재 (`sensor_` 또는 `식각`) | `golden_path/step2.png` |
| 3 | P4 진입 → 첫 번째 "✅ 수용" 버튼 클릭 | 토스트 또는 카운터 1 이상 | `golden_path/step3.png` |
| 4 | P5 진입 → "조치 이력" 탭 클릭 | 방금 수용 항목 한 줄 이상 | `golden_path/step4.png` |
| 5 | P1 복귀 | KPI 상태 녹색 또는 "정상" 텍스트 존재 | `golden_path/step5.png` |

## 통과 기준

- 트랙 ① — 콘솔 에러 0건, 스크린샷 10장 모두 생성
- 트랙 ② — 5단계 모두 어설션 통과, 스크린샷 5장 모두 생성
- 모든 스크린샷에서 한글이 깨지지 않음 (육안 검증)
```

### Task 5.3: Playwright 실행 헬퍼

**Files:**
- Create: `smart-factory-hackathon/tests/e2e/run_playwright_qa.py`

- [ ] **Step 1: 작성**

이 스크립트는 Playwright MCP 자체를 호출하는 게 아니라, 이미 캡처된 스크린샷들을 HTML 보고서로 묶는 역할. MCP 호출은 Claude Code 세션에서 직접 실행.

```python
"""Playwright MCP 캡처 결과를 HTML 보고서로 묶는 헬퍼.

MCP 호출 자체는 Claude Code 세션에서 직접 수행하고, 이 스크립트는
``assets/qa/playwright/`` 에 모인 PNG 들을 ``docs/reports/05_playwright_qa.html`` 로 묶는다.

CLI::

    python tests/e2e/run_playwright_qa.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from app.lib.report_render import write as write_report, build_index

QA_DIR = ROOT / "assets" / "qa" / "playwright"


def list_screenshots(subdir: str) -> list[Path]:
    target = QA_DIR / subdir
    if not target.exists():
        return []
    return sorted(target.glob("*.png"))


def gallery_html(title: str, shots: list[Path]) -> str:
    if not shots:
        return f"<p><em>{title} 스크린샷 없음</em></p>"
    items = "\n".join(
        f'<figure style="margin:8px;display:inline-block;width:300px;">'
        f'<img src="../../{p.relative_to(ROOT).as_posix()}" alt="{p.name}" style="width:100%;border:1px solid #d0d7de;border-radius:4px;">'
        f'<figcaption style="font-size:12px;color:#656d76;">{p.name}</figcaption>'
        f'</figure>'
        for p in shots
    )
    return f'<div>{items}</div>'


def main() -> int:
    real_shots = list_screenshots("real")
    dummy_shots = list_screenshots("dummy")
    golden_shots = list_screenshots("golden_path")

    pass_real = "✅" if len(real_shots) >= 5 else "❌"
    pass_dummy = "✅" if len(dummy_shots) >= 5 else "❌"
    pass_golden = "✅" if len(golden_shots) >= 5 else "❌"

    summary_html = (
        f"<table>"
        f"<tr><th>트랙</th><th>스크린샷</th><th>상태</th></tr>"
        f"<tr><td>트랙 ① real (5페이지)</td><td>{len(real_shots)}/5</td><td>{pass_real}</td></tr>"
        f"<tr><td>트랙 ① dummy (5페이지)</td><td>{len(dummy_shots)}/5</td><td>{pass_dummy}</td></tr>"
        f"<tr><td>트랙 ② 골든 패스 (5단계)</td><td>{len(golden_shots)}/5</td><td>{pass_golden}</td></tr>"
        f"</table>"
    )

    sections = [
        {"title": "1. 어설션 결과 요약", "body_html": summary_html},
        {"title": "2. 트랙 ① real 스크린샷", "body_html": gallery_html("트랙 ① real", real_shots)},
        {"title": "3. 트랙 ① dummy 스크린샷", "body_html": gallery_html("트랙 ① dummy", dummy_shots)},
        {"title": "4. 트랙 ② 골든 패스 스크린샷", "body_html": gallery_html("트랙 ② 골든 패스", golden_shots)},
    ]
    write_report("playwright_qa", source="real", sections=sections)
    build_index()  # 인덱스 갱신
    print(f"\n총 {len(real_shots) + len(dummy_shots) + len(golden_shots)}장 스크린샷 묶음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Task 5.4: Streamlit 가동

- [ ] **Step 1: 별도 터미널에서 (또는 백그라운드)**

```powershell
cd smart-factory-hackathon
$env:DEMO_MODE = "real"
streamlit run app/app.py
```

Expected: 브라우저에서 `localhost:8501` 자동 열림.

### Task 5.5: Playwright MCP 트랙 ① real 캡처 (Claude Code 세션에서 실행)

- [ ] **Step 1: P1 캡처**

```jsonc
// mcp__playwright__browser_navigate
{"url": "http://localhost:8501/"}
```
```jsonc
// mcp__playwright__browser_wait_for
{"text": "QualityLens"}
```
```jsonc
// mcp__playwright__browser_console_messages
{}
// 결과의 messages 중 level == 'error' 0건 어설션
```
```jsonc
// mcp__playwright__browser_take_screenshot
{"filename": "smart-factory-hackathon/assets/qa/playwright/real/P1.png", "fullPage": true}
```

- [ ] **Step 2~5: P2~P5 동일 패턴**

URL 변경:
- P2: `http://localhost:8501/실시간_예측`
- P3: `http://localhost:8501/원인_분석`
- P4: `http://localhost:8501/조치_가이드`
- P5: `http://localhost:8501/이력_조회`

각 페이지에서 `wait_for` 페이지 헤더 + `console_messages` + `take_screenshot`.

### Task 5.6: 트랙 ① dummy 캡처

- [ ] **Step 1: Streamlit 재시작 (dummy 모드)**

기존 streamlit 종료 (Ctrl+C). 새 터미널:
```powershell
cd smart-factory-hackathon
$env:DEMO_MODE = "dummy"
streamlit run app/app.py
```

- [ ] **Step 2: P1~P5 동일 패턴, filename 만 `dummy/Px.png`**

### Task 5.7: 트랙 ② 골든 패스 (DEMO_MODE=real 재기동)

- [ ] **Step 1: Streamlit 재시작 (real 모드)**

```powershell
cd smart-factory-hackathon
$env:DEMO_MODE = "real"
streamlit run app/app.py
```

- [ ] **Step 2: Step 1 — P2 시뮬레이션 시작**

```jsonc
{"url": "http://localhost:8501/실시간_예측"}  // navigate
{"text": "실시간 예측"}                         // wait_for
```

`mcp__playwright__browser_click` 으로 "▶️ 시뮬레이션 시작" 버튼 클릭 (정확한 element ref 는 `browser_snapshot` 결과에서 확인).

```jsonc
{"time": 12}  // browser_wait_for time=12 (초 단위 대기)
{"filename": "smart-factory-hackathon/assets/qa/playwright/golden_path/step1.png", "fullPage": true}
```

- [ ] **Step 3~5: P3·P4·P5 + P1 복귀, 각 단계 어설션·스크린샷 (시나리오 명세 표대로)**

### Task 5.8: HTML 보고서 생성 + 검증

- [ ] **Step 1: 스트리밍 종료 후 헬퍼 실행**

```powershell
cd smart-factory-hackathon
python tests/e2e/run_playwright_qa.py
cd ..
Start-Process smart-factory-hackathon/docs/reports/05_playwright_qa.html
```

Expected: 3개 트랙 × 5장 = 15장 스크린샷이 갤러리로 표시. 어설션 표 `✅ × 3`.

- [ ] **Step 2: 한글 깨짐 육안 검증**

각 스크린샷에서:
- 사이드바 배지의 한글 ("real (UCI SECOM)" / "dummy (폴백)")
- 페이지 타이틀의 한글 ("실시간 예측", "원인 분석" 등)
- 차트 라벨의 한글

깨진 부분이 있으면 P-B 작업 시 우선 수정 대상.

### Task 5.9: PR-5 커밋·머지

- [ ] **Step 1: add + commit**

```powershell
git add smart-factory-hackathon/tests/e2e/ smart-factory-hackathon/assets/qa/playwright/ smart-factory-hackathon/docs/reports/05_playwright_qa.html smart-factory-hackathon/docs/reports/index.html

git commit -m "feat(p-a/PR-5): Playwright MCP E2E 검증 + 결과 리포트 [Opus·Sonnet]

tests/e2e/playwright_scenarios.md — 트랙 ①(5페이지×2모드) + 트랙 ②(골든 패스 5단계) 명세
tests/e2e/run_playwright_qa.py — 스크린샷 → HTML 갤러리 자동 묶음

assets/qa/playwright/real/P{1..5}.png — DEMO_MODE=real 5페이지
assets/qa/playwright/dummy/P{1..5}.png — DEMO_MODE=dummy 5페이지
assets/qa/playwright/golden_path/step{1..5}.png — 식각 온도 골든 패스

docs/reports/05_playwright_qa.html — 갤러리 + 어설션 표
docs/reports/index.html — 5번 보고서 ✅ 갱신

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 2: push + PR + merge (GitHub MCP)**

```powershell
git push -u origin feat/p-a-5-playwright-e2e
```

`mcp__github__create_pull_request`:
```jsonc
{
  "owner": "mygithub05253", "repo": "Dacon",
  "head": "feat/p-a-5-playwright-e2e", "base": "main",
  "title": "feat(p-a/PR-5): Playwright MCP E2E 검증 + 결과 리포트",
  "body": "## 요약\n\nP-A 5단계 — 트랙 ①(5페이지×2모드 = 10장) + 트랙 ②(골든 패스 5장).\n\n## 변경\n- `tests/e2e/playwright_scenarios.md` 시나리오 명세\n- `tests/e2e/run_playwright_qa.py` 스크린샷 → HTML 갤러리\n- 15장 스크린샷 캡처\n- `docs/reports/05_playwright_qa.html` 갤러리\n\n## 검증\n- [x] 콘솔 에러 0건 (트랙 ①)\n- [x] 골든 패스 5단계 어설션 통과\n- [x] 한글 깨짐 육안 확인\n\n다음: PR-6 발표 자료"
}
```

이어서 `mcp__github__merge_pull_request` (squash). 머지 후 `git switch main; git pull origin main`.

---

## PR-6 — 발표 자료 + README 보강

**Branch:** `feat/p-a-6-presentation`
**Base:** `main` (PR-5 머지 후)
**LOC 예상:** ~50
**모델 라우팅:** Sonnet (문서 편집 위주)

### Task 6.1: 새 브랜치

- [ ] **Step 1:**

```powershell
git switch main
git pull origin main
git switch -c feat/p-a-6-presentation
```

### Task 6.2: README "데이터" 섹션 보강

**Files:**
- Modify: `smart-factory-hackathon/README.md`

- [ ] **Step 1: "UCI SECOM 데이터 받기" 섹션을 다음으로 교체 (라인 102~104)**

기존:
```markdown
### UCI SECOM 데이터 받기

`data/raw/secom.data`, `data/raw/secom_labels.data` 를 [UCI 저장소](https://archive.ics.uci.edu/dataset/179/secom)에서 받아 배치. 없어도 더미 데이터로 파이프라인 전체가 동작합니다.
```

교체:
```markdown
### UCI SECOM 실데이터

본 프로젝트는 **UCI SECOM 실데이터 1567행 591피처** 로 학습·검증을 완료했습니다.
원본 데이터는 `data/raw/secom.data`, `secom_labels.data` 로 git에 직접 포함되어
본선장 오프라인 환경에서도 즉시 사용 가능합니다. 라이선스·인용은
[data/raw/LICENSE.md](data/raw/LICENSE.md) 참조.

더미 모드는 폴백 전용입니다. 명시적으로 `--source dummy` 또는 `DEMO_MODE=dummy`
환경변수로만 활성화됩니다.

### 검증 산출물

- [real vs dummy 비교 보고서](docs/validation/real_vs_dummy_report.md) — 모델 성능 6개 지표 비교
- [단계별 HTML 보고서 인덱스](docs/reports/index.html) — T1·T2·T3·비교·Playwright 5종
- [Playwright E2E 시나리오](tests/e2e/playwright_scenarios.md) — 5페이지×2모드 + 골든 패스

### 실행 (실데이터)

```powershell
python scripts/01_preprocess.py --source real
python scripts/02_train.py --source real
python scripts/03_shap.py --source real
python scripts/04_compare_real_vs_dummy.py
$env:DEMO_MODE = "real"; streamlit run app/app.py
```
```

### Task 6.3: 슬라이드 outline 갱신

**Files:**
- Modify: `smart-factory-hackathon/docs/slides_outline.md`

- [ ] **Step 1: Slide 4 (기능) 섹션에 다음 한 줄 추가**

기존 Slide 4 본문에:
```markdown
**Real Data Verified** — UCI SECOM 실데이터 1567×591로 학습·검증 완료
(상세: docs/validation/real_vs_dummy_report.md)
```

- [ ] **Step 2: Slide 7 (시연) 섹션에 다음 한 줄 추가**

```markdown
사이드바 데이터 소스 배지(🟢 real / 🟡 dummy)로 실시간 가시화
```

### Task 6.4: demo_script Q&A 보강

**Files:**
- Modify: `smart-factory-hackathon/docs/demo_script.md`

- [ ] **Step 1: Q&A 섹션 끝에 다음 두 항목 추가**

```markdown
- **Q: 라벨이 진짜 식각 온도인가요?**
  A: UCI SECOM 데이터는 591개 센서가 모두 익명화(`sensor_000`~`sensor_590`)되어
     있습니다. "식각 온도" 같은 의미 라벨은 본 프로젝트의 기획 가정으로 매핑한
     것이며, 분포·기여도 패턴은 실데이터 그대로입니다.

- **Q: 모델 성능 수치의 근거는?**
  A: docs/validation/real_vs_dummy_report.md 의 모델 성능 표에 ROC-AUC, PR-AUC,
     MCC, F1 6개 지표가 실데이터 / 더미 양쪽으로 명시되어 있습니다.
     본선 발표 부록으로 인쇄 또는 화면 공유 가능합니다.
```

### Task 6.5: PR-6 커밋·머지

- [ ] **Step 1: add + commit**

```powershell
git add smart-factory-hackathon/README.md smart-factory-hackathon/docs/slides_outline.md smart-factory-hackathon/docs/demo_script.md
git commit -m "docs(p-a/PR-6): 발표 자료 보강 — README + 슬라이드 + Q&A [Sonnet]

- README '데이터' 섹션 — UCI 실데이터 명시 + 검증 산출물 링크
- slides_outline.md — Slide 4 'Real Data Verified' + Slide 7 사이드바 배지
- demo_script.md — 익명화 라벨·성능 근거 Q&A 2건 추가

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push -u origin feat/p-a-6-presentation
```

- [ ] **Step 2: push + PR + merge (GitHub MCP)**

```powershell
git push -u origin feat/p-a-6-presentation
```

`mcp__github__create_pull_request`:
```jsonc
{
  "owner": "mygithub05253", "repo": "Dacon",
  "head": "feat/p-a-6-presentation", "base": "main",
  "title": "docs(p-a/PR-6): 발표 자료 + README 보강 — P-A 완료",
  "body": "## 요약\n\nP-A 마무리 — 본선 발표 메시지 정렬.\n\n## 변경\n- README '데이터' 섹션 — UCI 실데이터 + 검증 산출물 링크\n- slides_outline.md — Slide 4 'Real Data Verified' + Slide 7 배지\n- demo_script.md — 익명화·성능 근거 Q&A 2건\n\n## 검증\n- [x] 모든 링크 유효 (data/raw/LICENSE.md, docs/validation/, docs/reports/index.html)\n\n**P-A 종료**. 다음 단계: P-B(한글 폰트 점검) brainstorming 또는 P-D(벤치마킹) 병렬 위임."
}
```

이어서 `mcp__github__merge_pull_request` (squash). 머지 후 main 동기화.

---

## 최종 검증 — 모든 PR 머지 후

### Task FINAL.1: 통합 동작 확인

- [ ] **Step 1: main 동기화**

```powershell
git switch main
git pull origin main
```

- [ ] **Step 2: 클린 리빌드**

```powershell
cd smart-factory-hackathon
Remove-Item data/processed/*.pkl, data/processed/*.csv, data/processed/*.png -ErrorAction SilentlyContinue
Remove-Item models/*.joblib, models/*.pkl, models/*.csv, models/*.md -ErrorAction SilentlyContinue
python scripts/01_preprocess.py --source real
python scripts/02_train.py --source real
python scripts/03_shap.py --source real
python scripts/01_preprocess.py --source dummy
python scripts/02_train.py --source dummy
python scripts/03_shap.py --source dummy
python scripts/04_compare_real_vs_dummy.py
python -c "from app.lib.report_render import build_index; build_index()"
cd ..
```

- [ ] **Step 3: 검증 통과 기준 (spec 섹션 15) 모두 체크**

- [ ] `data/raw/secom.data` 1567×591 로드
- [ ] real ROC-AUC ≥ 0.65 (`docs/validation/real_vs_dummy_report.md` 확인)
- [ ] SHAP top 20 real / dummy 둘 다 존재
- [ ] `docs/validation/real_vs_dummy_report.md` + `docs/reports/04_real_vs_dummy.html` 존재
- [ ] `docs/reports/0{1,2,3,4,5}_*.html` 5개 + `index.html`
- [ ] HTML 한글 정상
- [ ] `$env:DEMO_MODE="real"; streamlit run app/app.py` 5페이지 무에러
- [ ] `$env:DEMO_MODE="dummy"; streamlit run app/app.py` 5페이지 무에러
- [ ] 사이드바 배지 정상
- [ ] Playwright 트랙 ① 콘솔 에러 0건 + 스크린샷 10장
- [ ] Playwright 트랙 ② 골든 패스 5단계 스크린샷 5장
- [ ] 6개 sub-PR 모두 GitHub MCP 경로로 생성·머지

### Task FINAL.2: 다음 spec(P-B) 진입 신호

- [ ] **Step 1: P-A 완료 보고**

사용자에게 보고:
- 6개 PR 머지 완료 + `docs/reports/index.html` 인쇄 가능 상태
- Playwright 스크린샷에서 발견된 한글 깨짐이 있다면 P-B 작업 범위에 추가
- P-B (한글 폰트 전수 점검) brainstorming 진입 또는 P-D (벤치마킹) 병렬 위임 결정 요청
