#!/usr/bin/env python3
"""
pdf-to-md — One-click environment setup.

Usage:
    python setup.py                                 # interactive
    python setup.py --non-interactive               # auto: detected AI tools
    python setup.py --non-interactive --cli auto    # auto: detected AI tools
    python setup.py --non-interactive --scope project # install AI skill in workspace
    python setup.py --non-interactive --scope global # install AI skill globally
    python setup.py --workspace ~/Documents/pdf-to-md
    python setup.py --non-interactive --cli gemini  # auto: gemini
    python setup.py --non-interactive --cli all     # install to all CLIs
"""

from __future__ import annotations

import json
import os
import platform
import glob
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

OS = platform.system()
HOME = Path.home()
SKILL_NAME = "pdf-to-md"
VENV_PATH = HOME / ".pdf-to-md-venv"
CONFIG_PATH = HOME / ".pdf_to_md_config.json"
WORKSPACE_PATH = HOME / "Documents" / "pdf-to-md"

NON_INTERACTIVE = "--non-interactive" in sys.argv or "-y" in sys.argv


def _flag(name: str, default: str | None = None) -> str | None:
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


CLI_FLAG = _flag("--cli", default="auto")
WORKSPACE_FLAG = _flag("--workspace", default=None)
SCOPE_FLAG = _flag("--scope", default="project")

# CLI → global skill installation path
SKILL_DIRS = {
    "claude": HOME / ".claude/skills",
    "gemini": HOME / ".gemini/skills",
    "copilot": HOME / ".copilot/skills",
    "codex": HOME / ".agents/skills",
    "opencode": HOME / ".config/opencode/skills",
    # VS Code Copilot uses the Agent Skills standard, not an extension folder.
    "vscode": HOME / ".copilot/skills",
    "antigravity": HOME / ".gemini/antigravity/skills",
}


PROJECT_ROOT = WORKSPACE_PATH


AI_TARGETS = [
    {
        "key": "claude",
        "label": "Claude Code",
        "path": SKILL_DIRS["claude"],
        "project_path": PROJECT_ROOT / ".claude/skills",
        "commands": ["claude"],
        "markers": [HOME / ".claude"],
    },
    {
        "key": "codex",
        "label": "Codex",
        "path": SKILL_DIRS["codex"],
        "project_path": PROJECT_ROOT / ".agents/skills",
        "commands": ["codex"],
        "markers": [HOME / ".codex"],
    },
    {
        "key": "gemini",
        "label": "Gemini CLI",
        "path": SKILL_DIRS["gemini"],
        "project_path": PROJECT_ROOT / ".gemini/skills",
        "commands": ["gemini"],
        "markers": [HOME / ".gemini"],
    },
    {
        "key": "vscode",
        "label": "VS Code Chat",
        "path": SKILL_DIRS["vscode"],
        "project_path": PROJECT_ROOT / ".github/skills",
        "commands": ["code"],
        "markers": [HOME / ".vscode"],
    },
    {
        "key": "copilot",
        "label": "GitHub Copilot",
        "path": SKILL_DIRS["copilot"],
        "project_path": PROJECT_ROOT / ".github/skills",
        "commands": ["copilot", "gh"],
        "markers": [HOME / ".copilot"],
    },
    {
        "key": "opencode",
        "label": "OpenCode",
        "path": SKILL_DIRS["opencode"],
        "project_path": PROJECT_ROOT / ".opencode/skills",
        "commands": ["opencode"],
        "markers": [HOME / ".opencode"],
    },
    {
        "key": "antigravity",
        "label": "Antigravity",
        "path": SKILL_DIRS["antigravity"],
        "project_path": PROJECT_ROOT / ".agents/skills",
        "commands": ["antigravity"],
        "markers": [HOME / ".antigravity"],
    },
]

ALIASES = {
    "claude-code": "claude",
    "claude_code": "claude",
    "vs-code": "vscode",
    "vscode-chat": "vscode",
    "vs_code_chat": "vscode",
    "github-copilot": "copilot",
    "github_copilot": "copilot",
    "open-code": "opencode",
    "anti-gravity": "antigravity",
    "antiravity": "antigravity",
}

# Packages for each venv
PKGS_PDF_MASTER_NO_ODL = ["pymupdf", "python-pptx", "docling", "pypdf"]
PKGS_PDF_MASTER = ["opendataloader-pdf"] + PKGS_PDF_MASTER_NO_ODL
PKGS_MINERU = ["mineru"]
MAC_OCR = [
    "pyobjc-framework-Vision",
    "pyobjc-framework-Quartz",
    "pyobjc-framework-Cocoa",
]
WIN_OCR = ["winsdk"]


# ── Output helpers ────────────────────────────────────────────────────────────


def bar(t: str):
    print(f"\n{'─' * 52}\n  {t}\n{'─' * 52}")


def ok(m: str):
    print(f"  ✅ {m}")


def skip(m: str):
    print(f"  ⬜ {m}")


def warn(m: str):
    print(f"  ⚠️  {m}")


def fail(m: str):
    print(f"  ❌ {m}")


def info(m: str):
    print(f"  → {m}")


def update_project_paths():
    global PROJECT_ROOT
    PROJECT_ROOT = WORKSPACE_PATH
    project_paths = {
        "claude": PROJECT_ROOT / ".claude/skills",
        "codex": PROJECT_ROOT / ".agents/skills",
        "gemini": PROJECT_ROOT / ".gemini/skills",
        "vscode": PROJECT_ROOT / ".github/skills",
        "copilot": PROJECT_ROOT / ".github/skills",
        "opencode": PROJECT_ROOT / ".opencode/skills",
        "antigravity": PROJECT_ROOT / ".agents/skills",
    }
    for target in AI_TARGETS:
        target["project_path"] = project_paths[target["key"]]


def configure_workspace() -> Path:
    global WORKSPACE_PATH
    default = WORKSPACE_PATH
    if WORKSPACE_FLAG:
        WORKSPACE_PATH = Path(WORKSPACE_FLAG).expanduser()
    elif NON_INTERACTIVE:
        info(f"작업 폴더 자동 선택: {default}")
    else:
        print("\n  작업 폴더를 정합니다.")
        print("  PDF/PPTX를 넣고 결과를 받을 폴더입니다.")
        try:
            raw = input(f"  작업 폴더 (Enter: {default}): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = ""
        if raw:
            WORKSPACE_PATH = Path(raw).expanduser()
    update_project_paths()
    return WORKSPACE_PATH


def append_once(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in existing:
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n# pdf-to-md installer\n{line}\n")


def persist_user_path(paths: list[Path]):
    existing_paths = [str(p) for p in paths if p.exists()]
    if not existing_paths:
        return

    if OS == "Windows":
        current = os.environ.get("PATH", "")
        for p in existing_paths:
            if p not in current.split(os.pathsep):
                current = p + os.pathsep + current
        os.environ["PATH"] = current
        return

    joined = ":".join(f'"{p}"' for p in existing_paths)
    line = f"export PATH={joined}:$PATH"
    append_once(HOME / ".zshrc", line)
    append_once(HOME / ".bashrc", line)
    os.environ["PATH"] = os.pathsep.join(existing_paths + [os.environ.get("PATH", "")])


def ensure_workspace() -> Path:
    bar("Step 0.5: 작업 폴더 준비")
    WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)
    sample_chapter = WORKSPACE_PATH / "courses" / "sample-course" / "ch01"
    sample_source = sample_chapter / "source"
    for folder in (sample_source, sample_source / "markdown", sample_source / ".reports"):
        folder.mkdir(parents=True, exist_ok=True)
    readme = WORKSPACE_PATH / "README.md"
    if not readme.exists():
        readme.write_text(
            "\n".join(
                [
                    "# pdf-to-md",
                    "",
                    "Recommended layout:",
                    "",
                    "```text",
                    "courses/",
                    "  <course>/",
                    "    ch01-<chapter>/",
                    "      source/",
                    "        lecture.pptx",
                    "        reading.pdf",
                    "        markdown/  # converted Markdown and images",
                    "        .reports/  # hidden route reports and tool diagnostics",
                    "```",
                    "",
                    "Converted files are always saved under the input file's folder:",
                    "`<input folder>/markdown/` and `<input folder>/.reports/`.",
                    "",
                    "AI tools can open this folder as the project workspace.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    ok(f"작업 폴더: {WORKSPACE_PATH}")
    return WORKSPACE_PATH


def ask(prompt: str, choices: list, default: str) -> str:
    if NON_INTERACTIVE:
        info(f"{prompt}: 자동 선택 → {default}")
        return default
    opts = " / ".join(f"[{c}]" if c == default else c for c in choices)
    while True:
        try:
            ans = input(f"\n  {prompt} ({opts}): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return default
        if not ans:
            return default
        hits = [c for c in choices if c.startswith(ans)]
        if len(hits) == 1:
            return hits[0]
        if ans in choices:
            return ans
        print(f"  다시 입력하세요: {opts}")


# ── Step 0: CLI selection ─────────────────────────────────────────────────────


def detect_ai_targets() -> list[dict]:
    detected = []
    for target in AI_TARGETS:
        command_hits = [cmd for cmd in target["commands"] if shutil.which(cmd)]
        marker_hits = [p for p in target["markers"] if p.exists()]
        installed = bool(command_hits or marker_hits)
        detected.append(
            {
                **target,
                "installed": installed,
                "command_hits": command_hits,
                "marker_hits": marker_hits,
            }
        )
    return detected


def recommend_target(detected: list[dict]) -> str:
    for preferred in ("vscode", "copilot", "claude", "codex", "gemini", "opencode", "antigravity"):
        for target in detected:
            if target["key"] == preferred and target["installed"]:
                return preferred
    return "skip"


def automatic_targets(detected: list[dict]) -> list[str]:
    installed = [target["key"] for target in detected if target["installed"]]
    return installed or ["skip"]


def normalize_target_name(raw: str) -> str:
    lowered = raw.strip().lower()
    return ALIASES.get(lowered, lowered)


def parse_target_selection(raw: str, detected: list[dict]) -> list[str]:
    key_by_number = {
        str(i): target["key"]
        for i, target in enumerate(detected, 1)
    }
    all_keys = [target["key"] for target in detected]
    selected = []
    for part in raw.split(","):
        part = normalize_target_name(part)
        if not part:
            continue
        resolved = key_by_number.get(part) or part
        if resolved == "all":
            return all_keys
        if resolved in ("skip", "none", "converter", "converter-only"):
            return ["skip"]
        if resolved not in SKILL_DIRS:
            warn(f"무시된 입력: {part}")
            continue
        selected.append(resolved)
    return list(dict.fromkeys(selected))


def ask_options() -> list[str]:
    bar("Step 0: AI 도구 자동 확인")
    detected = detect_ai_targets()
    recommended = recommend_target(detected)
    valid_choices = list(SKILL_DIRS.keys()) + ["all", "skip"]

    if NON_INTERACTIVE:
        raw = CLI_FLAG or recommended
        if raw == "auto":
            clis = automatic_targets(detected)
            if clis == ["skip"]:
                info("감지된 AI 도구 없음 → 변환기만 설치")
            else:
                info(f"감지된 AI 도구 자동 연결: {', '.join(clis)}")
            return clis
        if raw == "all":
            return list(SKILL_DIRS.keys())
        if raw == "skip":
            info("AI 도구 연결: 건너뜀")
            return ["skip"]
        clis = [normalize_target_name(c) for c in raw.split(",")]
        if any(c in ("none", "converter", "converter-only") for c in clis):
            info("AI 도구 연결: 건너뜀")
            return ["skip"]
        for c in clis:
            if c not in SKILL_DIRS:
                fail(f"알 수 없는 AI 도구: {c} (유효: {valid_choices})")
                sys.exit(2)
        info(f"AI 도구: {', '.join(clis)}")
        return clis

    print("\n  설치되어 있는 것으로 보이는 AI 도구를 확인했습니다.")
    for i, target in enumerate(detected, 1):
        mark = "감지됨" if target["installed"] else "미감지"
        rec = "  ← 추천" if target["key"] == recommended else ""
        print(f"    [{i}] {target['label']:<16} {mark}{rec}")
    print("    [8] 변환기만 설치       AI 도구 연결 없이 PDF/PPTX 변환만 사용")
    print("    [9] 전부 설치           위 AI 도구 폴더에 모두 복사")
    print("\n  잘 모르겠으면 Enter를 누르세요. 추천 항목으로 설치합니다.")
    default_display = "8" if recommended == "skip" else str(
        next(i for i, target in enumerate(detected, 1) if target["key"] == recommended)
    )
    try:
        ans = input(f"  선택 (기본값: {default_display}): ").strip() or default_display
    except (EOFError, KeyboardInterrupt):
        ans = default_display

    if ans == "8":
        return ["skip"]
    if ans == "9":
        return list(SKILL_DIRS.keys())

    selected = parse_target_selection(ans, detected)
    if selected:
        return selected

    return ["skip"] if recommended == "skip" else [recommended]


def normalize_install_scope(raw: str | None) -> str:
    scope = (raw or "project").strip().lower()
    aliases = {
        "p": "project",
        "project-only": "project",
        "project_only": "project",
        "workspace": "project",
        "local": "project",
        "g": "global",
        "global-only": "global",
        "global_only": "global",
        "personal": "global",
    }
    return aliases.get(scope, scope)


def ask_install_scope(target_clis: list[str]) -> str:
    if target_clis == ["skip"]:
        return "project"

    valid_scopes = ["project", "global"]
    if NON_INTERACTIVE:
        scope = normalize_install_scope(SCOPE_FLAG)
        if scope not in valid_scopes:
            fail(f"알 수 없는 설치 범위: {SCOPE_FLAG} (유효: {valid_scopes})")
            sys.exit(2)
        info(f"AI skill 설치 범위: {scope}")
        return scope

    bar("Step 0.1: AI skill 설치 범위")
    print("\n  [1] project  추천: Documents/pdf-to-md 작업 폴더에만 설치")
    print("  [2] global   모든 프로젝트에서 쓰도록 개인 전역 폴더에 설치")
    print("\n  잘 모르겠으면 Enter를 누르세요. project로 설치합니다.")
    try:
        ans = input("  선택 (기본값: 1): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        ans = ""
    if ans in ("", "1"):
        return "project"
    if ans == "2":
        return "global"
    scope = normalize_install_scope(ans)
    if scope in valid_scopes:
        return scope
    warn(f"알 수 없는 설치 범위: {ans} → project로 설치")
    return "project"


# ── Step 1: uv ────────────────────────────────────────────────────────────────


def find_uv() -> str | None:
    u = shutil.which("uv")
    if u:
        return u
    candidates = [
        HOME / ".local/bin/uv",
        HOME / ".cargo/bin/uv",
        HOME / ".local/bin/uv.exe",
        HOME / "AppData/Local/uv/uv.exe",
        HOME / "AppData/Roaming/uv/uv.exe",
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


def ensure_uv() -> str:
    bar("Step 1: uv 확인")
    u = find_uv()
    if u:
        ok(f"이미 설치됨: {u}")
        return u
    info("uv 설치 중...")
    if OS != "Windows" and not shutil.which("curl"):
        fail("curl 없음 — 인터넷 설치 스크립트를 내려받을 수 없습니다")
        print("    AI에게 @INSTALL.md 설치해줘 라고 맡기거나, curl 설치 후 다시 실행하세요.")
        sys.exit(1)
    cmd = (
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "irm https://astral.sh/uv/install.ps1 | iex",
        ]
        if OS == "Windows"
        else ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"]
    )
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        fail("자동 설치 실패")
        print("    Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("    Windows:   irm https://astral.sh/uv/install.ps1 | iex")
        sys.exit(1)
    extra = [
        HOME / ".local/bin",
        HOME / ".cargo/bin",
        HOME / "AppData/Local/uv",
    ]
    persist_user_path(extra)
    u = find_uv()
    if not u:
        fail("설치 후 찾을 수 없음 — 새 터미널에서 재실행하세요")
        if OS == "Windows":
            print("    Windows에서는 PATH 반영 때문에 재부팅 후 install.bat을 다시 실행해야 할 수 있습니다.")
        sys.exit(1)
    ok(f"설치 완료: {u}")
    return u


# ── Step 1.5: Java (ODL optional quality boost) ───────────────────────────────


def check_java() -> bool:
    """Returns True if Java is available. Best-effort installs Java when missing."""
    bar("Step 1.5: Java 확인 (선택: ODL 품질 향상)")
    if java_available():
        ok_java()
        return True

    warn("Java 없음 → 자동 설치 시도")
    install_java_best_effort()
    if java_available():
        ok_java()
        return True

    warn("Java 자동 설치 실패 또는 즉시 감지 실패 → ODL은 건너뛰고 fitz + MinerU로 계속 진행합니다")
    print("  Java는 선택 사항입니다. 수동 설치가 필요하면:")
    if OS == "Darwin":
        print("    macOS:   brew install --cask temurin@11")
    elif OS == "Windows":
        print("    Windows: winget install EclipseAdoptium.Temurin.11.JDK")
    else:
        print("    Linux:   sudo apt install openjdk-11-jdk")
    return False


def java_available() -> bool:
    try:
        return subprocess.run(["java", "-version"], capture_output=True, text=True).returncode == 0
    except FileNotFoundError:
        return False


def ok_java():
    r = subprocess.run(["java", "-version"], capture_output=True, text=True)
    first = (r.stderr or r.stdout or "java OK").splitlines()[0]
    ok(f"Java 감지: {first}")


def install_java_best_effort():
    if OS == "Darwin":
        brew = shutil.which("brew")
        if not brew:
            warn("Homebrew 없음 → Java 자동 설치 생략, 변환 설치는 계속 진행")
            return
        r = subprocess.run(
            [brew, "install", "--cask", "temurin@11"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            warn("Homebrew Java 설치 실패")
            print(textwrap.indent((r.stderr or r.stdout)[-500:], "    "))
            return
        java_home = subprocess.run(
            ["/usr/libexec/java_home", "-v", "11"],
            capture_output=True,
            text=True,
        )
        if java_home.returncode == 0 and java_home.stdout.strip():
            jhome = java_home.stdout.strip()
            os.environ["JAVA_HOME"] = jhome
            os.environ["PATH"] = str(Path(jhome) / "bin") + os.pathsep + os.environ.get("PATH", "")
            append_once(HOME / ".zshrc", 'export JAVA_HOME=$(/usr/libexec/java_home -v 11)')
            append_once(HOME / ".zshrc", 'export PATH="$JAVA_HOME/bin:$PATH"')
    elif OS == "Windows":
        winget = shutil.which("winget")
        if not winget:
            warn("winget 없음 → Java 자동 설치 생략, 변환 설치는 계속 진행")
            print("    Windows에서 Java 품질 경로가 필요하면 나중에 재부팅 후 설치기를 다시 실행해도 됩니다.")
            return
        r = subprocess.run(
            [
                winget,
                "install",
                "--id",
                "EclipseAdoptium.Temurin.11.JDK",
                "-e",
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            warn("winget Java 설치 실패")
            print(textwrap.indent((r.stderr or r.stdout)[-500:], "    "))
            return
        candidates = [
            Path(p)
            for p in glob.glob(r"C:\Program Files\Eclipse Adoptium\jdk-11*\bin")
            + glob.glob(r"C:\Program Files\Java\jdk-11*\bin")
        ]
        persist_user_path(candidates)
        print("    Windows는 Java PATH 반영에 재부팅이 필요할 수 있습니다.")
    else:
        warn("Linux Java 자동 설치는 배포판별 권한 차이 때문에 생략")


# ── Step 2: venv ──────────────────────────────────────────────────────────────


def py_bin(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if OS == "Windows" else "bin/python")


def ensure_venv(uv: str, venv: Path) -> Path:
    pbin = py_bin(venv)
    if pbin.exists():
        ok(f"기존 재사용: {venv}")
        return pbin
    info(f"생성 중: {venv}")
    r = subprocess.run(
        [uv, "venv", "--python", "3.12", str(venv)], capture_output=True, text=True
    )
    if r.returncode != 0:
        fail(f"venv 생성 실패\n{r.stderr}")
        sys.exit(1)
    if not pbin.exists():
        fail(f"Python 없음: {pbin}")
        sys.exit(1)
    ok(f"생성 완료: {venv}")
    return pbin


def pip_install(uv: str, pbin: Path, pkgs: list[str], label: str) -> bool:
    if not pkgs:
        return True
    r = subprocess.run(
        [uv, "pip", "install", "--python", str(pbin)] + pkgs,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        ok(f"{label} 완료")
        return True
    warn(f"{label} 실패 (선택 항목)")
    print(textwrap.indent(r.stderr[-400:], "    "))
    return False


# ── Detect existing installs ──────────────────────────────────────────────────


def find_existing_pdf_master_python() -> str | None:
    candidates = [
        HOME
        / ".pdf-master-venv"
        / ("Scripts/python.exe" if OS == "Windows" else "bin/python"),
        HOME
        / ".pdf-to-md-pdfmaster-venv"
        / ("Scripts/python.exe" if OS == "Windows" else "bin/python"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def find_existing_mineru_python() -> str | None:
    candidates = [
        HOME
        / ".mineru-venv"
        / ("Scripts/python.exe" if OS == "Windows" else "bin/python"),
        HOME
        / ".pdf-to-md-mineru-venv"
        / ("Scripts/python.exe" if OS == "Windows" else "bin/python"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ── Step 3: install packages ──────────────────────────────────────────────────


def install_packages(
    uv: str, pbin_unified: Path, java_ok: bool
) -> tuple[dict, str, str]:
    """
    Try unified venv first. On conflict, split into pdf-master + mineru venvs.
    Returns (installed_dict, pdf_master_python, mineru_python).
    """
    bar("Step 3: 패키지 설치")
    installed = {}
    pdf_pkgs = PKGS_PDF_MASTER if java_ok else PKGS_PDF_MASTER_NO_ODL
    if not java_ok:
        skip("opendataloader-pdf — Java 없으므로 건너뜀")

    # Check if existing venvs already have what we need
    existing_pdf = find_existing_pdf_master_python()
    existing_mineru = find_existing_mineru_python()

    if existing_pdf and existing_mineru:
        info(f"기존 venv 재사용: pdf-master={existing_pdf}")
        info(f"기존 venv 재사용: mineru={existing_mineru}")
        ok("두 venv 모두 발견 — split 모드 사용")
        installed["mode"] = "split"
        installed["pdf_master_python"] = existing_pdf
        installed["mineru_python"] = existing_mineru
        return installed, existing_pdf, existing_mineru

    # Try unified install
    label = (
        "pymupdf + ODL + pptx + docling + mineru"
        if java_ok
        else "pymupdf + pptx + docling + mineru"
    )
    info(f"통합 venv 설치 시도 중 ({label})...")
    all_pkgs = pdf_pkgs + PKGS_MINERU
    r = subprocess.run(
        [uv, "pip", "install", "--python", str(pbin_unified)] + all_pkgs,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        ok("통합 venv 설치 성공")
        installed["mode"] = "unified"
        pdf_py = str(pbin_unified)
        mineru_py = str(pbin_unified)
        installed["pdf_master_python"] = pdf_py
        installed["mineru_python"] = mineru_py
    else:
        warn("통합 설치 실패 (패키지 충돌) → split 모드로 전환")
        # Fall back to split venvs
        pdf_venv = HOME / ".pdf-to-md-pdfmaster-venv"
        mineru_venv = HOME / ".pdf-to-md-mineru-venv"
        pdf_pbin = ensure_venv(uv, pdf_venv)
        mineru_pbin = ensure_venv(uv, mineru_venv)
        pdf_ok = pip_install(uv, pdf_pbin, pdf_pkgs, "pdf-master 패키지")
        mineru_ok = pip_install(uv, mineru_pbin, PKGS_MINERU, "mineru 패키지")
        if not pdf_ok:
            fail("필수 PDF/PPTX 패키지 설치 실패 — 네트워크 확인 후 재실행하세요")
            sys.exit(1)
        if not mineru_ok:
            warn("MinerU 설치 실패 — 기본 PDF/PPTX 변환은 계속 사용 가능")
        installed["mode"] = "split"
        pdf_py = str(pdf_pbin)
        mineru_py = str(mineru_pbin)
        installed["pdf_master_python"] = pdf_py
        installed["mineru_python"] = mineru_py

    # OCR (optional)
    bar("Step 4: OCR (선택)")
    unified_or_pdf = pbin_unified if installed["mode"] == "unified" else Path(pdf_py)
    if OS == "Darwin":
        installed["apple_vision"] = pip_install(
            uv, unified_or_pdf, MAC_OCR, "Apple Vision (Mac)"
        )
    elif OS == "Windows":
        installed["windows_ocr"] = pip_install(
            uv, unified_or_pdf, WIN_OCR, "winsdk (Windows)"
        )
    else:
        skip("Linux: OCR via ODL 폴백")

    return installed, pdf_py, mineru_py


# ── Step 5: verify ────────────────────────────────────────────────────────────


def verify(pdf_py: str, mineru_py: str, java_ok: bool) -> dict:
    bar("Step 5: 검증")
    checks = {
        "pymupdf": (pdf_py, "import fitz"),
        "opendataloader-pdf": (pdf_py, "import opendataloader_pdf"),
        "python-pptx": (pdf_py, "import pptx"),
        "docling": (pdf_py, "from docling.document_converter import DocumentConverter"),
        "mineru": (mineru_py, "import mineru"),
        "Apple Vision": (pdf_py, "import Vision"),
        "Windows OCR": (pdf_py, "import winsdk"),
    }
    v = {}
    # ODL only required when Java was available and installed
    required = {"pymupdf", "python-pptx"}
    if java_ok:
        required.add("opendataloader-pdf")
    for name, (py, code) in checks.items():
        r = subprocess.run([py, "-c", code], capture_output=True)
        passed = r.returncode == 0
        v[name] = passed
        if passed:
            ok(name)
        elif name in required:
            fail(name)
        else:
            skip(f"{name} (선택)")
    for p in required:
        if not v.get(p):
            fail(f"필수 패키지 검증 실패: {p} — 네트워크 확인 후 재실행하세요")
            sys.exit(1)
    return v


# ── Step 6: copy skill files ──────────────────────────────────────────────────


def copy_skill_tree(src: Path, dst: Path):
    if src.resolve() == dst.resolve():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        dest_item = dst / item.name
        if item.is_dir():
            if dest_item.exists():
                shutil.rmtree(dest_item)
            shutil.copytree(item, dest_item)
        else:
            shutil.copy2(item, dest_item)


def should_install_project(target: dict) -> bool:
    return PROJECT_ROOT.exists()


def copy_skill(target_clis: list[str], install_scope: str = "project") -> list[dict]:
    bar("Step 6: AI 도구 연결")
    destinations = []
    installed_paths = set()
    if target_clis == ["skip"]:
        skip("AI 도구 연결 건너뜀 — convert.command 또는 convert.ps1로 직접 변환하세요")
        return destinations
    if install_scope not in ("project", "global"):
        fail(f"알 수 없는 설치 범위: {install_scope}")
        sys.exit(2)
    skill_src = Path(__file__).parent
    target_map = {target["key"]: target for target in AI_TARGETS}
    for cli in target_clis:
        target = target_map[cli]
        if install_scope == "global":
            dst = target["path"] / SKILL_NAME
        else:
            dst = target["project_path"] / SKILL_NAME

        dst_key = str(dst.resolve())
        if install_scope == "project" and not should_install_project(target):
            destinations.append(
                {
                    "provider": cli,
                    "scope": "project",
                    "path": str(dst),
                    "recommended": False,
                    "note": "프로젝트 폴더가 명확하지 않아 안내만 기록",
                }
            )
            skip(f"{target['label']} project 후보 → {dst}")
        elif dst_key not in installed_paths:
            copy_skill_tree(skill_src, dst)
            installed_paths.add(dst_key)
            destinations.append(
                {
                    "provider": cli,
                    "scope": install_scope,
                    "path": str(dst),
                    "recommended": True,
                }
            )
            ok(f"{target['label']} {install_scope} → {dst}")
        else:
            skip(f"{target['label']} {install_scope} → 이미 설치됨: {dst}")
    return destinations


def write_workspace_launcher():
    launcher = WORKSPACE_PATH / "convert-here.command"
    launcher.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                "set -eu",
                f'KIT_DIR="{Path(__file__).parent}"',
                'cd "$KIT_DIR"',
                'exec ./convert.command',
                "",
            ]
        ),
        encoding="utf-8",
    )
    try:
        launcher.chmod(0o755)
    except OSError:
        pass


# ── Step 7: save config ───────────────────────────────────────────────────────


def save_config(
    installed: dict,
    pdf_py: str,
    mineru_py: str,
    verified: dict,
    clis: list[str],
    install_scope: str,
    destinations: list[dict],
):
    bar("Step 7: config 저장")
    cfg = {
        "pdf_master_python": pdf_py,
        "mineru_python": mineru_py,
        "mode": installed.get("mode", "unified"),
        "os": OS,
        "cli": clis,
        "install_scope": install_scope,
        "project_root": str(PROJECT_ROOT),
        "workspace": str(WORKSPACE_PATH),
        "destinations": destinations,
        "installed": installed,
        "verified": verified,
        "ready": True,
        "apple_vision": verified.get("Apple Vision", False),
        "windows_ocr": verified.get("Windows OCR", False),
        "docling": verified.get("docling", False),
        "mineru": verified.get("mineru", False),
    }
    CONFIG_PATH.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ok(f"저장: {CONFIG_PATH}")
    return cfg


# ── Report ────────────────────────────────────────────────────────────────────


def write_install_report(cfg: dict, clis: list[str], destinations: list[dict]):
    detected = detect_ai_targets()
    lines = [
        "# pdf-to-md 설치 보고서",
        "",
        f"- OS: {OS}",
        f"- 작업 폴더: `{WORKSPACE_PATH}`",
        f"- 프로젝트 설치 기준 폴더: `{PROJECT_ROOT}`",
        f"- AI skill 설치 범위: `{cfg.get('install_scope', 'project')}`",
        f"- 환경 모드: `{cfg['mode']}`",
        "",
        "## 감지된 AI 도구",
        "",
    ]
    for target in detected:
        status = "감지됨" if target["installed"] else "미감지"
        lines.append(f"- {target['label']}: {status}")
        lines.append(f"  - global 후보: `{target['path'] / SKILL_NAME}`")
        lines.append(f"  - project 후보: `{target['project_path'] / SKILL_NAME}`")
    lines.extend(["", "## 실제 설치 위치", ""])
    if not destinations:
        lines.append("- AI 도구 연결 없음. 변환기는 이 폴더에서 `convert.command` 또는 `convert.ps1`로 사용합니다.")
    else:
        for dest in destinations:
            mark = "설치" if dest.get("recommended") else "안내"
            lines.append(f"- {dest['provider']} / {dest['scope']}: {mark} → `{dest['path']}`")
    lines.extend(
        [
            "",
            "## 사용법",
            "",
            "- Mac: `convert.command` 더블클릭",
            "- Windows: `convert.ps1` 실행",
            f"- 작업 폴더: `{WORKSPACE_PATH}`",
            "- AI 도구에서: `이 PDF/PPTX를 Markdown으로 변환해줘: <파일 경로>`",
            "",
        ]
    )
    report_file = Path(__file__).parent / "INSTALL_REPORT.md"
    report_file.write_text("\n".join(lines), encoding="utf-8")
    ok(f"설치 보고서: {report_file}")
    return report_file


def report(cfg: dict, clis: list[str], destinations: list[dict]):
    print(f"\n{'=' * 52}")
    print("  🎉 pdf-to-md 환경 준비 완료!")
    print(f"{'=' * 52}")
    print(f"\n  모드:   {cfg['mode']}")
    print(f"  OS:     {OS}")
    print(f"  작업 폴더: {WORKSPACE_PATH}")
    print(f"  기능:")
    print("    ✅ 한글/영문 디지털 PDF")
    print("    ✅ PPTX → Markdown (docling + pptx-direct 자동 선택)")
    print("    ✅ 2단 논문, 슬라이드, 교과서 자동 라우팅")
    if cfg.get("apple_vision"):
        print("    ✅ 스캔 OCR (Apple Vision)")
    if cfg.get("docling"):
        print("    ✅ Docling 복잡 레이아웃")
    if cfg.get("mineru"):
        print("    ✅ MinerU 챕터 분할")
    print("\n  사용법:")
    if OS == "Windows":
        print("    convert.ps1 실행 → 파일 경로 붙여넣기")
    else:
        print("    convert.command 더블클릭 → 파일 경로 붙여넣기")
    print(f"    작업 폴더에 파일 넣기: {WORKSPACE_PATH}")
    print("    또는: uv run --python 3.12 python convert.py <파일.pdf 또는 파일.pptx>")
    if clis == ["skip"]:
        print("\n  AI 도구 연결: 건너뜀")
    else:
        print(f"\n  연결된 AI 도구: {', '.join(clis)}")
        print(f"  AI skill 설치 범위: {cfg.get('install_scope', 'project')}")
        for dest in destinations:
            if dest.get("recommended"):
                print(f"    {dest['provider']} ({dest['scope']}) → {dest['path']}")
    print(f"\n  설치 보고서: {Path(__file__).parent / 'INSTALL_REPORT.md'}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    print(f"\n{'=' * 52}")
    print("  pdf-to-md — 환경 자동 설정")
    print(f"  OS: {OS} / Python {sys.version.split()[0]}")
    if NON_INTERACTIVE:
        print("  모드: 자동 (--non-interactive)")
    print(f"{'=' * 52}")

    configure_workspace()
    ensure_workspace()
    target_clis = ask_options()
    install_scope = ask_install_scope(target_clis)

    uv = ensure_uv()
    java_ok = check_java()
    pbin_unified = ensure_venv(uv, VENV_PATH)
    installed, pdf_py, mineru_py = install_packages(uv, pbin_unified, java_ok)
    verified = verify(pdf_py, mineru_py, java_ok)
    destinations = copy_skill(target_clis, install_scope=install_scope)
    write_workspace_launcher()
    cfg = save_config(installed, pdf_py, mineru_py, verified, target_clis, install_scope, destinations)
    write_install_report(cfg, target_clis, destinations)
    report(cfg, target_clis, destinations)


if __name__ == "__main__":
    main()
