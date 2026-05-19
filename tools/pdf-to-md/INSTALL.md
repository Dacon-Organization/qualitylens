# pdf-to-md 설치하기

대상: PDF/PPTX를 Markdown으로 바꾸고 싶은 학생. 복잡한 설치 용어나 명령어를 몰라도 됩니다.

## 1. 먼저 할 일

인터넷이 연결되어 있어야 합니다. 설치 파일은 Python과 필요한 변환 도구를 자동으로 준비합니다.

Windows는 설치 후 새 PowerShell 창, 로그아웃/로그인, 또는 재부팅이 필요할 수 있습니다. 설치 직후 `uv`, `python`, `java`를 못 찾는다고 나오면 재부팅 후 같은 설치 파일을 다시 실행하세요. 이미 설치된 것은 재사용됩니다.

## 2. 설치 방법

### Mac

1. 이 폴더에서 `install.command`를 더블클릭합니다.
2. macOS가 막으면 파일을 우클릭한 뒤 **열기**를 누릅니다.
3. 질문이 나오면 잘 모르는 항목은 Enter를 누릅니다.
4. 설치가 끝나면 `~/Documents/pdf-to-md` 폴더가 생깁니다.

### Windows

1. 이 폴더에서 `install.bat`을 더블클릭합니다.
2. Windows가 확인을 물으면 실행을 허용합니다.
3. 질문이 나오면 잘 모르는 항목은 Enter를 누릅니다.
4. 설치가 끝나면 `Documents\pdf-to-md` 폴더가 생깁니다.
5. 설치 직후 명령을 못 찾는 오류가 나오면 Windows를 재부팅한 뒤 `install.bat`을 다시 실행합니다.

`install.bat`이 동작하지 않으면 AI에게 `@INSTALL.md 설치해줘`라고 맡기세요.

## 3. AI에게 맡겨서 설치

VS Code Chat, Claude Code, Codex, Gemini CLI, OpenCode 같은 agentic AI를 이미 쓰고 있다면 이 파일을 멘션해서 맡겨도 됩니다.

```text
@INSTALL.md 설치해줘
```

AI가 터미널을 실행할 수 있는 모드여야 합니다. VS Code Chat에서는 Agent Mode가 필요합니다.

AI는 이 문서를 읽고 운영체제에 맞는 설치 파일을 실행합니다. 사용자가 설치 장소, Python, uv, Java 같은 도구를 알 필요는 없습니다.

AI가 내부적으로 실행할 명령:

```bash
# Mac
./install.command --auto
```

```powershell
# Windows
.\install.bat -Auto
```

## 4. 파일을 어디에 두면 되나요?

설치 후 아래 샘플 폴더가 자동으로 만들어집니다.

```text
Documents/pdf-to-md/
  courses/
    sample-course/
      ch01/
        source/
```

과목과 chapter 이름은 마음대로 바꿔도 됩니다.

추천 예시:

```text
Documents/pdf-to-md/
  courses/
    컴퓨팅사고/
      ch01-컴퓨팅의-요소들/
        source/
          강의자료.pptx
          교재.pdf
```

## 5. 변환 결과는 어디에 생기나요?

규칙은 하나입니다.

```text
PDF/PPTX가 있는 폴더 아래에 markdown/ 폴더가 생깁니다.
```

예를 들어 원본이 여기 있으면:

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/강의자료.pptx
```

결과는 여기 생깁니다.

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/markdown/강의자료.md
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/markdown/images/강의자료/
```

변환 기록은 같은 폴더의 숨김 폴더에 저장됩니다.

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/.reports/
```

학생은 보통 `.reports/`를 볼 필요가 없습니다.

## 6. 변환 방법

### 가장 쉬운 방법

Mac은 `convert.command`를 더블클릭합니다. Windows는 `convert.bat`을 더블클릭합니다. 파일 경로를 물어보면 PDF/PPTX 파일을 끌어다 놓거나 경로를 붙여넣습니다.

### AI에게 맡기는 방법

```text
이 파일을 Markdown으로 변환해줘:
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/강의자료.pptx
```

AI는 결과 위치를 물어보지 말고 원본 파일이 있는 폴더 아래 `markdown/`에 저장하면 됩니다.

## 7. 설치기가 자동으로 하는 일

설치기는 다음을 자동으로 처리합니다.

1. `uv` 확인 및 설치
2. Python 3.12 실행 환경 준비
3. 변환 도구 설치
4. Java가 있으면 사용, 없으면 가능한 경우만 자동 설치 시도
5. 작업 폴더 생성
6. Claude Code, Codex, Gemini CLI, VS Code Chat, GitHub Copilot, OpenCode, Antigravity 감지
7. 감지된 AI 도구에 skill 연결
8. 설치 결과를 `INSTALL_REPORT.md`에 기록

AI skill 설치 위치는 `project / global` 중 고를 수 있습니다. 기본값은 project입니다.

- `project`: `Documents/pdf-to-md` 작업 폴더 안에만 설치합니다. 학생 배포 기본값입니다.
- `global`: 개인 전역 폴더에 설치합니다. 여러 프로젝트에서 계속 쓸 때만 선택합니다.

VS Code Chat과 GitHub Copilot은 Agent Skills 표준 위치를 함께 씁니다. 프로젝트 skill은 `.github/skills/pdf-to-md`, 개인 skill은 `~/.copilot/skills/pdf-to-md`에 연결됩니다.

Maintainer note: installer skill targets are intentionally limited to the provider-documented paths below.

| Provider | Personal/global path | Project/workspace path |
|---|---|---|
| Claude Code | `~/.claude/skills/pdf-to-md` | `.claude/skills/pdf-to-md` |
| Codex | `~/.agents/skills/pdf-to-md` | `.agents/skills/pdf-to-md` |
| Gemini CLI | `~/.gemini/skills/pdf-to-md` | `.gemini/skills/pdf-to-md` |
| VS Code Copilot | `~/.copilot/skills/pdf-to-md` | `.github/skills/pdf-to-md` |
| GitHub Copilot CLI | `~/.copilot/skills/pdf-to-md` | `.github/skills/pdf-to-md` |
| OpenCode | `~/.config/opencode/skills/pdf-to-md` | `.opencode/skills/pdf-to-md` |
| Antigravity | `~/.gemini/antigravity/skills/pdf-to-md` | `.agents/skills/pdf-to-md` |

Antigravity uses `.agents/skills`; `.agent/skills` is backward compatibility only and is not written by this installer.

사용자가 변환 도구를 고를 필요는 없습니다. 변환할 때 PDF/PPTX를 분석해서 여러 도구 중 좋은 결과를 자동 선택합니다.

## 8. 자주 막히는 경우

### Windows에서 설치 후 명령을 못 찾음

새 PowerShell 창을 열고 다시 시도하세요. 그래도 같으면 Windows를 재부팅한 뒤 `install.bat`을 다시 실행하세요.

### Java를 찾을 수 없음

Java는 선택 사항입니다. 일부 PDF 품질이 좋아질 수 있지만, Java가 없어도 변환은 계속됩니다.

### 설치가 멈추거나 실패함

인터넷 연결을 확인한 뒤 설치 파일을 다시 실행하세요. agentic AI를 쓸 수 있으면 `@INSTALL.md`를 멘션해서 설치를 맡기세요.

### 변환 결과에 그림이 일부 안 보임

PPTX 안에 WMF 같은 오래된 이미지 형식이 있으면 일부 Markdown 앱에서 표시하지 못할 수 있습니다. 이 경우 `.reports/`와 원본 파일을 담당자에게 보내면 됩니다.
