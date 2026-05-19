# Spec — QualityLens 본선 준비 (2026-05-22)

> 작성일: 2026-05-19 (D-3)
> 본선: 2026-05-22(금) 09:00 KST
> 작성자: 이동원 (kik328288@gmail.com)
> 상태: 초안 → 사용자 검토 대기

---

## 1. 배경

QualityLens는 2026 스마트 공장 운영 시스템 MVP 해커톤 출전작이다. 예선을 통과해 본선에 진출했으며, 본선장에서는 두 가지 제약이 결정적이다.

1. **토큰 제약** — 본선장에서는 Claude 구독이 아닌 Codex(GPT-5.x Plus) 환경
2. **시간 제약** — D-3에서 D-Day까지 무거운 작업을 모두 완료해야 함

이 spec은 D-3 ~ D-1 사이 사전 작업의 범위·아키텍처·운영 규칙을 정의한다.

## 2. 목표

- **G1**: 본선장에서 모델·SHAP 재계산 없이 시연 가능한 산출물 사전 완성
- **G2**: Claude(Opus/Sonnet/Haiku) → Codex(GPT-5.4/5.5) 폴백 라우팅 규칙 명문화
- **G3**: 진행 상황을 채팅이 아닌 외부 HTML 로드맵에 누적 — 컨텍스트 외부화
- **G4**: 5분 발표 + 백업 시나리오 사전 완성 + 시연 골든 패스 검증

## 3. 비목표 (YAGNI)

- 다공정 확장 (단일 SECOM 데이터셋 한정)
- 실시간 PLC 자동 제어 (조치 가이드 표시까지만)
- 다국어 UI (한국어 단일)
- 모바일 반응형 (해커톤 시연은 데스크탑)

## 4. 접근 방식 — Heavy Front-load

D-3 ~ D-1에 Claude로 풀스택 사전 완성, D-Day에는 Codex 호출 최소화.

### 4.1 사전 작업 5트랙

| 트랙 | 산출물 | Claude | Codex 폴백 |
|---|---|---|---|
| T1 데이터 파이프라인 | `data/processed/secom_{train,test}.pkl` | Sonnet | GPT-5.4 |
| T2 모델 학습 & 캐싱 | `models/xgb_secom.joblib` + `threshold_table.csv` | **Opus** | GPT-5.5 |
| T3 SHAP 사전 계산 | `models/shap_explainer.pkl` + `shap_top20.csv` | **Opus** | GPT-5.5 |
| T4 Streamlit UI | `app/app.py` + `app/pages/P1~P5.py` | Opus 골격 → Sonnet 디테일 | GPT-5.4 |
| T5 발표·데모 | `docs/demo_script.md` + 백업 슬라이드 | Sonnet | GPT-5.4 |

### 4.2 의존성

```
T1 ─► T2 ─► T3
         └────┐
              ▼
              T4 ─► T5
```

### 4.3 토큰 절약 5대 원칙 (codex-bridge/token-saving.md)

1. 모델 재학습 금지 — 직렬화 로드만
2. SHAP 재계산 금지 — 사전 계산본 로드
3. 채팅 컨텍스트 의존 최소화 — HTML 로드맵 노트가 정본
4. 단일 파일 단위 호출 — 멀티 파일 동시 수정 금지
5. 데모 시연 중 모델 호출 금지 — 결정론적 데모 모드

## 5. 시각화 로드맵 HTML (`docs/roadmap.html`)

단일 파일 외부 의존 없는 vanilla HTML/CSS/JS. localStorage 기반 자동 저장.

### 5.1 구성

1. 헤더 — D-Day 카운트다운 (KST)
2. 전체 진행률 바 — 체크박스 자동 합산
3. 5트랙 진행 보드 — 각 트랙별 카드 + 추천 모델 + Codex 폴백 + 체크박스
4. 의존성 다이어그램 — T1→T2→T3→T4→T5
5. 하이브리드 모델 라우팅 표 — Claude ↔ Codex 1:1 매핑
6. 본선 D-Day 체크리스트 — 환경 점검 8항목
7. 5분 발표 시나리오 표 — 분당 토픽 + 화면 전환 큐
8. 작업 노트 영역 — textarea + localStorage + .md 다운로드

### 5.2 본선장에서의 역할

- 채팅 히스토리 대신 작업 노트가 컨텍스트의 정본
- Codex 세션 시작 시 노트 발췌만 붙여넣기
- 발표 보조 자료로 그대로 재활용 가능 (URL 공유 또는 화면 캡처)

## 6. 신규 스킬 3종 (Codex 환경 대비)

기존 5개 스킬(data-pipeline / modeling / xai / ui / quality)에 추가:

### 6.1 `skills/codex-bridge/`

- `INDEX.md` — 핵심 원칙 + Claude ↔ Codex 매핑
- `model-routing.md` — 복잡도별 모델 결정 표
- `token-saving.md` — 5대 절약 원칙
- `prompt-templates.md` — Claude/Codex 동일 템플릿 (T-01 ~ T-04)
- `fallback-playbook.md` — 5종 비상 대응

### 6.2 `skills/streamlit-build/`

- `INDEX.md` — 캐싱 5원칙
- `app-structure.md` — 디렉터리 + 진입점 골격
- `page-specs.md` — P1~P5 위젯·차트 명세
- `cache-policy.md` — `cache_data` vs `cache_resource`
- `demo-toggle.md` — 데모↔실데이터 라디오 + 골든 패스

### 6.3 `skills/demo-script/`

- `INDEX.md` — 5분 발표 5대 원칙
- `five-min-flow.md` — 분당 토픽 + 전환 큐
- `backup-scenarios.md` — 시연 실패 대응 2종
- `qna-prep.md` — 예상 질문 5선 + 답변

## 7. 디렉터리 추가

```
smart-factory-hackathon/
├── app/                    # 신규 (D-1 작업)
│   ├── app.py
│   ├── pages/
│   └── lib/
├── data/                   # 신규 (gitignored, 샘플만 포함)
│   ├── raw/
│   └── processed/
├── models/                 # 신규
├── notebooks/              # 신규
├── docs/
│   ├── roadmap.html        # 신규 (이 PR)
│   ├── demo_script.md      # T5에서 작성
│   └── spec_finals_prep.md # 본 spec (이 PR)
└── skills/
    ├── codex-bridge/       # 신규 (이 PR)
    ├── streamlit-build/    # 신규 (이 PR)
    └── demo-script/        # 신규 (이 PR)
```

## 8. 검증 기준

이 spec이 작동 가능하다고 판단하는 조건:

- [ ] T1~T5 산출물이 본선장 노트북에 로컬로 존재
- [ ] `streamlit run app/app.py` 한 줄로 5페이지 정상 렌더
- [ ] 데모 모드에서 모델·SHAP 재계산 없이 시연 완료
- [ ] HTML 로드맵의 작업 노트로 발표 자료 인용 가능
- [ ] 5분 발표 리허설 1회 이상 시간 측정 완료

## 9. 후속 작업 (이 PR 머지 후)

본 PR이 머지되면 다음 순서로 진행:

1. **T1 데이터 파이프라인** (Sonnet) — `notebooks/01_preprocess.ipynb`
2. **T2 모델 학습** (Opus) — `notebooks/02_train.ipynb`
3. **T3 SHAP 사전 계산** (Opus) — `notebooks/03_shap.ipynb`
4. **T4 Streamlit UI** (Opus 골격 → Sonnet 디테일) — `app/`
5. **T5 발표·데모** (Sonnet) — `docs/demo_script.md`

각 단계 완료 시 `roadmap.html`의 체크박스를 채우고 작업 노트에 결과 기록.

## 10. 위험 요소

| 위험 | 영향 | 완화책 |
|---|---|---|
| joblib 버전 충돌 | 모델 로드 실패 | `requirements.txt` 버전 고정, 본선장 pip upgrade 금지 |
| 인터넷 끊김 | 모델 호출 불가 | 모든 자산 로컬 보관, 오프라인 시연 가능 |
| 5분 초과 | 감점 | 4:30 알람, 백업 시나리오 |
| Codex Plus 로그인 실패 | 코드 수정 불가 | 사전에 D-3에 모든 작업 완료 (호출 최소화) |
| 데모 즉흥 입력 실패 | 신뢰 손상 | 데모 모드 강제, 사전 캐싱 샘플만 사용 |
