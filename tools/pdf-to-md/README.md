# pdf-to-md 사용법

PDF/PPTX를 Markdown으로 바꾸는 도구입니다. 어떤 변환 도구를 쓸지는 자동으로 정합니다.

## 설치

AI 도구를 쓰고 있다면 아래처럼 말하면 됩니다.

```text
@INSTALL.md 설치해줘
```

VS Code Chat은 Agent Mode에서 실행하세요. AI가 터미널을 실행할 수 없는 모드라면 직접 설치 파일을 실행합니다.

Mac:

```text
install.command 더블클릭
```

Windows:

```text
install.bat 더블클릭
```

Windows에서 설치 직후 명령을 못 찾는 오류가 나오면 재부팅한 뒤 `install.bat`을 다시 실행하세요.

AI skill 설치 위치는 기본적으로 `project only`입니다. 즉 `Documents/pdf-to-md` 작업 폴더 안에만 연결합니다. 설치 중 `global`을 선택하면 개인 전역 폴더에 설치되어 다른 프로젝트에서도 쓸 수 있습니다.

VS Code Chat과 GitHub Copilot skill은 표준 Agent Skills 위치를 씁니다. 프로젝트는 `.github/skills/pdf-to-md`, 개인은 `~/.copilot/skills/pdf-to-md`입니다.

Maintainer path summary: Claude Code uses `~/.claude/skills` and `.claude/skills`; Codex uses shared `~/.agents/skills` and `.agents/skills`; Gemini CLI uses `~/.gemini/skills` and `.gemini/skills`; VS Code/GitHub Copilot use `~/.copilot/skills` and `.github/skills`; OpenCode uses `~/.config/opencode/skills` and `.opencode/skills`; Antigravity uses `~/.gemini/antigravity/skills` and `.agents/skills`.

## 파일 정리 예시

설치 후 `Documents/pdf-to-md` 폴더를 씁니다.

```text
Documents/pdf-to-md/
  courses/
    컴퓨팅사고/
      ch01-컴퓨팅의-요소들/
        source/
          강의자료.pptx
          교재.pdf
```

원본 PDF/PPTX는 원하는 폴더에 두어도 됩니다. 변환 결과는 항상 원본 파일이 있는 폴더 아래 `markdown/`에 생깁니다.

## 변환 결과

예를 들어 원본이 여기 있으면:

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/강의자료.pptx
```

결과는 여기 생깁니다.

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/markdown/강의자료.md
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/markdown/images/강의자료/
```

숨김 폴더 `.reports/`에는 변환 기록이 저장됩니다. 학생은 보통 볼 필요 없습니다.

```text
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/.reports/
```

## 변환하기

Mac은 `convert.command`를 더블클릭합니다. Windows는 `convert.bat`을 더블클릭합니다. 파일 경로를 물어보면 PDF/PPTX 파일을 끌어다 놓거나 경로를 붙여넣습니다.

AI에게 맡길 때는 이렇게 말하면 됩니다.

```text
이 파일을 Markdown으로 변환해줘:
Documents/pdf-to-md/courses/컴퓨팅사고/ch01-컴퓨팅의-요소들/source/강의자료.pptx
```

AI는 결과 위치를 묻지 않고 원본 파일이 있는 폴더 아래 `markdown/`에 저장하면 됩니다.

## 문제가 생기면

- Windows에서 명령을 못 찾으면 재부팅 후 다시 실행합니다.
- 그림이 일부 안 보이면 원본 PPTX에 WMF 같은 오래된 이미지가 있을 수 있습니다.
- 변환 결과가 이상하면 원본 파일과 `.reports/` 폴더를 담당자에게 보냅니다.
