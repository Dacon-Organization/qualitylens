# pdf-to-md — QualityLens 프로젝트 사용 노트

> 원본: `C:/Users/kik32/Downloads/pdf-to-md-student/pdf-to-md/` (수정 금지)
> 본 복사본: 우리 프로젝트 컨벤션 + 본선 활용 가이드를 추가한 작업본
> 도구 출처: 교수님 강의 자료

## 우리 프로젝트에서의 용도

| 시점 | 사용 사례 | 결과물 활용 |
|---|---|---|
| 본선 사전 (D-2 ~ D-1) | `QualityLens_기획서.pdf` → MD 변환 | 발표 스크립트·Q&A 답변에 본문 인용 가능 |
| 본선 사전 | UCI SECOM paper / Kaggle Smart Manufacturing 설명 PDF | 데이터 출처 슬라이드 보강 |
| 본선 후 | 심사 피드백 PPTX | 회고·다음 단계 도출 |

## 설치 (Windows, AI 위임)

원본 INSTALL.md 안내에 따라:

```text
@INSTALL.md 설치해줘
```

또는 직접:

```powershell
cd smart-factory-hackathon\tools\pdf-to-md
.\install.bat -Auto
```

설치 결과는 사용자 `Documents/pdf-to-md/` 에 떨어집니다 (이건 원본 동작 그대로 — 우리 레포는 도구의 소스만 보유).

## 사용 예 (QualityLens 기획서 변환)

설치 완료 후:

```powershell
python smart-factory-hackathon\tools\pdf-to-md\convert.py "smart-factory-hackathon\QualityLens_기획서.pdf"
```

결과 위치 (원본 도구 컨벤션):

```
smart-factory-hackathon/
└── QualityLens_기획서.pdf
└── markdown/
    └── QualityLens_기획서.md
    └── images/QualityLens_기획서/...
└── .reports/QualityLens_기획서.route.json
```

이 `.md`를 우리 `docs/` 에 인용하거나 발표 스크립트 보강에 활용.

## 본 사본의 위치를 유지하는 이유

- 원본은 Downloads에 있어 **OS·계정·기기 변경 시 사라질 위험**
- 우리 프로젝트에 복사본을 두면 **본선장 노트북에서도 재현 가능**
- `tools/pdf-to-md/` 는 우리 도구 모음 — 향후 다른 외부 스킬도 같은 위치에 모음

## 절대 하지 말 것

- 원본(`C:/Users/kik32/Downloads/pdf-to-md-student/`)의 어떤 파일도 수정·삭제 금지 (교수님 강의 자료)
- 우리 사본의 `SKILL.md`도 가능하면 원형 유지 — Codex/Claude의 자동 트리거 정확도가 description 매칭에 달려 있어서 (agent_skills WS-01-100 § Skill 발동 흐름)
- 커스터마이징이 필요하면 본 `PROJECT_NOTES.md` 에만 메모 추가
