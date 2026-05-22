# Spec — P-B: Streamlit 배포 Hotfix & 하이브리드 메모리 + 작업 추적 대시보드

> 작성일: 2026-05-22 (D-Day, 본선 당일 09:00 KST 직전)
> 작성자: 이동원 (kik328288@gmail.com)
> 모델 라우팅:
>   - **Opus**: 5섹션 근본 원인 분석, sub-PR 분할 설계, 하이브리드 메모리 아키텍처, 대시보드 정보 구조, real 배포 연구, 10단계 전문가 점검
>   - **Sonnet**: dummy 산출물 빌드 스크립트 수정, graceful degradation 한 줄 try/except, HTML 템플릿 채움, INDEX.md 갱신, 캡처 파일명 표준화
>   - **Codex GPT-5.5/5.4** (Claude 토큰 5시간 한도 도달 시): Sonnet 역할 대체 — 반복 코드 수정, 템플릿 채움, 문서 포맷 정리. HANDOVER.md를 컨텍스트로 사용.
> 상태: 초안 → 사용자 셀프 리뷰 대기

---

## 1. 배경 & 트리거 사건

### 1.1 트리거 사건 (2026-05-22 발견)

Streamlit Cloud 배포 URL 접속 시 다음 에러로 앱이 시작조차 못 함:

```
FileNotFoundError: 산출물 부재 (dummy): secom_X_test_dummy.pkl 또는 secom_y_test_dummy.pkl.
  scripts/01_preprocess.py --source dummy 실행 필요.
  at app/lib/data_loader.py:83
  via app/app.py:44  X_test, y_test = load_test_set()
```

본선 09:00 KST 직전 발견 → 심사위원이 배포 URL을 클릭하면 빈 에러만 보이는 **최악 시나리오**. P-A까지의 폴리시 완성도가 무의미해질 위험.

### 1.2 동시 처리할 만성 갭

| 갭 | 현황 | 위험 |
|---|---|---|
| **세션 단절** | Claude 5시간 한도 도달 시 대안 없음. 다른 세션·도구로 옮기면 컨텍스트 상실. | 본선 D-Day에 한도 도달 시 작업 마비 |
| **진행 가시화 부족** | 단계별 HTML(P-A PR-4)은 산출물 보고서일 뿐, "지금 어디까지 됐고 다음 뭐 할지" 일별 추적 도구 없음 | 발표 백업/심사 자료 준비 누락 위험 |
| **기획서 vs 실구현 괴리** | 초기 기획서(QualityLens_기획서.pdf, 243KB)와 현재 구현 간 변경점 정리 안 됨 | 발표 시 일관성 부족 |
| **캡처 산만** | smart-factory-hackathon/ 루트에 slide-*.jpg, qa-slide-*.jpg 등 혼재 | 버전·맥락 추적 불가 |
| **real 산출물 배포 미해결** | xgb_secom_real.joblib(~수십 MB) 배포 방안 부재 | 시연 시 dummy만 보여줄 수밖에 없음 |

### 1.3 P-B 범위 정의

P-A가 "실데이터 통합 + 검증"이었다면, P-B는 **"운영 안정화 + 협업 인프라"**.
한글 폰트 전수 점검은 별도 spec(`spec_p_c_korean_font_audit.md`)으로 분리하여 P-C로 미룬다.

---

## 2. 목표 (G1~G7)

- **G1 (Hotfix)**: dummy 산출물 7종 git 커밋 + `load_test_set()` graceful degradation → 배포 URL이 항상 안정 시연
- **G2 (캡처 인프라)**: `docs/captures/v{n}/` 버전 폴더 + INDEX.md 자동 갱신 → 작업/발표 자료 추적 가능
- **G3 (하이브리드 메모리)**: `docs/HANDOVER.md` + `docs/SESSION_LOG.md` → Claude/Codex/Sonnet 어떤 도구로 이어받아도 컨텍스트 복원 가능
- **G4 (작업 추적 대시보드)**: `docs/dashboard/index.html` 정적 페이지 — 진행 이력 + 발표 준비도 + 기획서 변경점을 한눈에. **매 sub-PR 완료 시 자동 갱신**
- **G5 (real 배포 연구)**: 전처리·압축·Git LFS·외부 호스팅 4가지 옵션 비교 보고서 → 본선 후 실행 결정
- **G6 (10단계 전문가 점검)**: PM/UX/Eng/QA/Sec/DevOps/Doc/Data/AI/Biz 10개 관점 체크리스트 → 매 sub-PR PR-Description에 첨부
- **G7 (Git 워크플로우 정착)**: P-A의 6 sub-PR 패턴 재사용 — pull → branch → commit → push → PR → auto merge

---

## 3. 비목표 (YAGNI)

- 한글 폰트 전수 점검 (→ P-C로 분리)
- 모델 재학습·하이퍼파라미터 변경
- 새 페이지·새 기능 추가 (P-A까지의 5페이지 유지)
- Codex 자동 호출 자동화 (수동 전환 + HANDOVER.md 인계로 충분)
- 대시보드의 실시간 갱신(WebSocket/SSE) — 정적 HTML + 수동 빌드 스크립트로 시작

---

## 4. 5섹션 근본 원인 분석 (요약)

> 상세는 세션 채팅 로그 보존. 여기에는 결론만.

| 섹션 | 핵심 |
|---|---|
| **① 근본 원인** | `_detect_default_source()`가 real 산출물 부재 → `dummy` 폴백 → dummy 산출물도 미커밋 → FileNotFoundError raise |
| **② 영향 범위** | 메인 페이지 + P2~P5 전체 다운, demo_mode 분기 이전 호출되어 demo 모드여도 죽음 |
| **③ 옵션 비교** | A(dummy 커밋) ⭐⭐⭐⭐⭐ / B(real 커밋) ⭐⭐⭐ / C(부팅 시 학습) ⭐⭐ / D(LFS) ⭐⭐ / E(graceful degradation) — A+E 조합 채택 |
| **④ 권장안** | dummy 7종 커밋 + try/except 안전망 + `app.py:44` 호출 위치 demo 분기 안쪽으로 이동 + .gitignore 명시화 |
| **⑤ 검증** | P1(로컬 재현) → P2(단위) → P3(graceful path) → P4(Playwright 5p×dummy) → P5(배포 E2E) → P6(캡처 v1 보관) |

---

## 5. Sub-PR 분할 (6개)

| # | 제목 | 산출물 | 모델 | 검증 |
|---|---|---|---|---|
| **PR-1** | Hotfix: dummy 산출물 7종 + graceful degradation | `data/processed/secom_{X,y}_test_dummy.pkl`, `models/xgb_secom_dummy.joblib`, `shap_*_dummy.pkl` 4종, `data_loader.py` try/except, `app.py:44` 위치 이동, `.gitignore` 명시화 | Sonnet (스크립트 실행 + 코드 수정) | 로컬 재현 / Playwright 5p×dummy |
| **PR-2** | 캡처 인프라: `docs/captures/v{n}/` + INDEX | `docs/captures/v1/`, `scripts/05_update_captures_index.py`, 첫 v1 캡처 5종(메인 + P2~P5) | Sonnet | INDEX.md 자동 생성 확인 |
| **PR-3** | 하이브리드 메모리: HANDOVER + SESSION_LOG | `docs/HANDOVER.md`(현황·다음 액션·환경 변수), `docs/SESSION_LOG.md`(일별 추가형), 갱신 스크립트 | Opus(구조) + Sonnet(템플릿) | Codex 시뮬레이션 (HANDOVER만으로 다음 액션 식별 가능?) |
| **PR-4** | 작업 추적 대시보드 v1 | `docs/dashboard/index.html`, `docs/dashboard/data.json`, `scripts/06_build_dashboard.py` | Opus(정보 구조 + 실무 벤치마킹) + Sonnet(렌더링) | 로컬 브라우저 열기 + 모바일 확인 |
| **PR-5** | real 배포 연구 보고서 | `docs/research/real_deploy_options.md` (전처리·압축·LFS·외부 호스팅 4안 비교, 결정 보류) | Opus | 자체 비교표 합리성 확인 |
| **PR-6** | 발표 백업: 기획서 변경점 + 발표 자료 보강 | `docs/presentation/spec_vs_impl_diff.md`, `docs/presentation/qa_pack_p_b.md` | Opus(diff 분석) + Sonnet(작성) | 기획서 PDF 대조 |

**각 sub-PR PR-Description 필수 포함**:
- 10단계 전문가 점검 체크리스트 (§10 참조)
- 캡처 v{n} 링크
- HANDOVER.md 갱신 라인
- 대시보드 갱신 여부

---

## 6. 하이브리드 메모리 시스템 설계

### 6.1 문제 정의

- Claude 5시간 한도 도달 → Codex GPT-5.5/5.4로 전환 → 컨텍스트 0에서 재시작
- 워크트리, 브랜치, 진행 단계, 결정 사항, 다음 액션을 매번 다시 설명 = 시간/토큰 낭비

### 6.2 산출물

**`smart-factory-hackathon/docs/HANDOVER.md`** — 항상 최신 상태 (덮어쓰기형)

```markdown
# HANDOVER — 마지막 갱신: {YYYY-MM-DD HH:MM KST} / 도구: {Claude Opus|Sonnet|Codex GPT-5.5}

## 0. 한 줄 현황
- {예: "P-B PR-1 진행 중, dummy 산출물 4/7 커밋 완료"}

## 1. 환경
- 워크트리: {경로}
- 브랜치: {이름}
- origin/main 대비: ahead {n} / behind {m}

## 2. 마지막 결정 사항 (최근 5건)
- {YYYY-MM-DD} {결정 내용} (#PR-번호)

## 3. 다음 액션 (TOP 3)
1. {파일/명령어 수준의 구체 액션}
2. ...
3. ...

## 4. 차단 요소 / 사용자 확인 대기
- {예: "real 배포 방안 — 사용자 결정 대기"}

## 5. 도구 전환 가이드
- Claude → Codex 전환 시: `SESSION_LOG.md` 최근 3일 + `dashboard/data.json` + 이 파일만 로드하면 충분
- Codex → Claude 복귀 시: 동일
```

**`smart-factory-hackathon/docs/SESSION_LOG.md`** — 일별 추가형 (절대 덮어쓰지 않음)

```markdown
## 2026-05-22 14:30 KST [Claude Opus]
- P-B 스펙 v1 작성 (#PR-?)
- 결정: A+E 조합 채택 (dummy 커밋 + graceful degradation)
- 다음: PR-1 착수
```

### 6.3 운영 규칙

- 모든 sub-PR commit 메시지 끝줄에 **`HANDOVER 갱신: YES/NO`** 표기 강제
- HANDOVER.md는 50줄 이하 유지 (스크롤 없이 한 화면)
- SESSION_LOG.md는 무한 누적, 분기별 archive

---

## 7. 작업 추적 대시보드 설계 (G4)

### 7.1 실무 벤치마킹 대상 (웹크롤링 / 사례 조사 대상)

PR-4 착수 시 다음을 빠르게 스캔하여 정보 구조 참고:

| 도구 | 참고할 패턴 |
|---|---|
| **Linear** | "Cycle" 진행률 / 우선순위 라벨 / 변경 로그 |
| **Notion Roadmap** | Status × Owner 매트릭스 |
| **GitHub Projects (Beta)** | 칸반 + 마일스톤 + 자동화 |
| **Basecamp Hill Charts** | "어느 언덕에 있는가"의 시각 비유 |
| **Shape Up** | "Scope Map" — 불확실성 vs 진행도 2축 |
| **Spotify Squad Health Check** | 신호등(🟢🟡🔴) 자기 평가 |

### 7.2 대시보드 정보 구조 (한 페이지)

```
┌────────────────────────────────────────────────────┐
│ QualityLens — 본선 대시보드   D-{n}  ⏱ {now}      │
├────────────────────────────────────────────────────┤
│ [발표 준비도]  ▓▓▓▓▓▓▓░░ 73%   🟢 정상            │
│ [코드 안정도]  ▓▓▓▓▓▓▓▓▓ 92%   🟢 정상            │
│ [배포 상태]    ▓▓▓░░░░░░ 30%   🔴 hotfix 진행중   │
├────────────────────────────────────────────────────┤
│ Sub-PR 진행                                        │
│  ✅ PR-1 Hotfix          🟢 머지됨 14:50           │
│  🚧 PR-2 캡처 인프라     🟡 작업중                 │
│  ⏳ PR-3 하이브리드 메모리                          │
│  ⏳ PR-4 대시보드 (이 화면)                         │
│  ⏳ PR-5 real 배포 연구                             │
│  ⏳ PR-6 기획서 변경점                              │
├────────────────────────────────────────────────────┤
│ 기획서 vs 구현 변경점 (상위 5건)                    │
│  ▸ "실시간 스트리밍" → 1초 폴링 시뮬                │
│  ▸ "다공정 확장"     → 식각 단일 시나리오로 축소    │
│  ▸ ...                                              │
├────────────────────────────────────────────────────┤
│ 캡처 갤러리 (v{최신})         [v1] [v2] ...        │
│  [thumb1] [thumb2] [thumb3] [thumb4] [thumb5]      │
├────────────────────────────────────────────────────┤
│ 최근 결정 (HANDOVER 동기화)                        │
│  • 14:30 A+E 조합 채택                             │
│  • 14:15 P-B 스펙 v1 작성                          │
└────────────────────────────────────────────────────┘
```

### 7.3 빌드 방식

- `scripts/06_build_dashboard.py` — `docs/dashboard/data.json` 읽어 `index.html` 렌더
- `data.json` 데이터 소스: HANDOVER.md 파싱 + git log + `docs/captures/v*/INDEX.md`
- 정적 HTML → 로컬 브라우저로 열거나 GitHub Pages로 노출 가능
- 매 sub-PR 머지 후 pre-commit hook으로 자동 빌드 (검토 후 도입)

---

## 8. 캡처 폴더 구조

```
smart-factory-hackathon/docs/captures/
├── INDEX.md              ← 전체 버전 목록 + 썸네일
├── v1/                   ← 첫 캡처 세트 (P-B PR-2)
│   ├── INDEX.md          ← v1 내 캡처 메타 + 설명
│   ├── 01_main_dummy.png
│   ├── 02_p2_streaming.png
│   ├── 03_p3_shap.png
│   ├── 04_p4_threshold.png
│   ├── 05_p5_alert.png
│   └── notes.md          ← 캡처 당시 이슈/맥락
├── v2/                   ← 변경 발생 시 신규
└── ...
```

**버전 발행 규칙**:
- UI 변경, 폰트 변경, 데이터 소스 전환 시 신규 버전
- 매 본선 리허설 후 신규 버전
- v{n}/notes.md 에 "왜 새 버전인가" 필수 기록

**기존 루트 캡처 처리** (slide-*.jpg, qa-slide-*.jpg, thumbnails.jpg 등):
- 발표 슬라이드용은 `docs/presentation/slides/` 로 이동
- QA 캡처는 `docs/captures/v0/` 으로 history 보존
- 루트 정리는 PR-2에 포함

---

## 9. real 산출물 배포 연구 (G5, PR-5 단독)

### 9.1 옵션 비교 매트릭스

| 옵션 | 크기 영향 | 셋업 시간 | 배포 신뢰성 | 본선 가능성 |
|---|---|---|---|---|
| **(a) Quantization + dtype 다운캐스트** (float64→float32, joblib compress=9) | -60~70% | 30분 | 높음 | ⭐⭐⭐⭐⭐ |
| **(b) 핵심 피처만 학습** (분산-상관 필터 강화로 591 → 100~150) | -50% | 1시간 | 높음 (성능 영향 검증 필요) | ⭐⭐⭐⭐ |
| **(c) Git LFS** | 0 (단지 보관) | 1시간 + Streamlit Cloud LFS 토큰 설정 | 보통 (LFS quota 1GB) | ⭐⭐⭐ |
| **(d) 외부 호스팅** (HuggingFace Hub / S3 / Google Drive) | 0 | 1~2시간 | 높음 (단 부팅 시 다운로드 ~10s) | ⭐⭐⭐⭐ |
| **(e) Streamlit Cloud secrets에서 zip 다운로드** | 0 | 1시간 | 보통 | ⭐⭐⭐ |

### 9.2 비정형 데이터 처리 수업 자료 연계점

- (a) Quantization: 모델 가중치 dtype 다운캐스트 (수업의 "수치 표현 절감")
- (b) 피처 선택: 분산 임계 / 상관 임계 강화 (수업의 "차원 축소")
- 보너스: SHAP top-K(예: top 50)만 추론용으로 보존 → 메모리 대폭 절감

### 9.3 PR-5 결정 방식

PR-5는 **결정이 아닌 비교 보고서**. 본선 후 사용자가 (a)+(b) 조합으로 갈지 결정.

---

## 10. 10단계 전문가 관점 체크리스트

매 sub-PR PR-Description에 다음 표를 채워 첨부.

| # | 관점 | 핵심 질문 | 통과 기준 |
|---|---|---|---|
| 1 | **PM** | 본선 일정·심사 기준에 부합? | 발표 일정 D-Day 영향 0 |
| 2 | **UX** | 사용자(심사위원)가 1분 내 가치 파악? | 메인 진입 3초 내 KPI 4종 가시 |
| 3 | **Eng** | 코드 수정 범위·복잡도 최소? | 변경 라인 < 200, 새 의존성 0 |
| 4 | **QA** | 회귀 테스트 통과? | Playwright 5p × 2 mode = 10 case PASS |
| 5 | **Security** | secret·LFS 토큰 노출 없음? | .env / .streamlit/secrets.toml 점검 |
| 6 | **DevOps** | 배포 빌드 시간·실패율 영향? | 부팅 시간 < 60s 유지 |
| 7 | **Doc** | 문서 동기화? | README / spec / HANDOVER 3종 갱신 |
| 8 | **Data** | 데이터 라이선스·출처 명시? | LICENSE.md 인용 표기 유지 |
| 9 | **AI** | 모델 일관성·재현성? | RANDOM_STATE=42 유지, 결정성 확인 |
| 10 | **Biz** | 발표 메시지·기획서와 정합? | 기획서 변경점 spec_vs_impl_diff에 기록 |

---

## 11. 검증 계획

| 단계 | 검증 | 도구 | 합격선 |
|---|---|---|---|
| **V1** dummy 폴백 로컬 | 산출물 삭제 후 `streamlit run app/app.py` | shell | 메인 KPI 4종 렌더 |
| **V2** 단위 | `pytest tests/test_data_loader.py` 신규 1건 | pytest | PASS |
| **V3** graceful | dummy 산출물도 삭제 후 진입 | manual | "데이터 준비 중" 안내 페이지 |
| **V4** 통합 | Playwright MCP 5p × dummy 모드 | Playwright | 5/5 PASS, 콘솔 에러 0 |
| **V5** 배포 | Streamlit Cloud 재배포 | browse skill | 메인 URL 200 + KPI 가시 |
| **V6** 캡처 | v1 5종 + INDEX.md | manual | 모든 페이지 captured |
| **V7** 인계 | HANDOVER.md만 보고 "다음 액션 1개" 추론 | self-test | 5분 내 추론 가능 |
| **V8** 대시보드 | 로컬 + 모바일 뷰포트 | browse skill | 정보 7섹션 모두 가독 |

---

## 12. 일정 (D-Day 2026-05-22 09:00 KST 본선)

> 본선까지 시간이 매우 촉박. PR 우선순위 = PR-1 > PR-2 > PR-3 > PR-4 > PR-6 > PR-5
> PR-5는 본선 후 작업 가능 (사용자 결정 보류 보고서)

| 시각 (KST) | 작업 | 모델 |
|---|---|---|
| 즉시 | 스펙 사용자 셀프 리뷰 + 확정 | (대화) |
| +30분 | PR-1 dummy 빌드 + 커밋 + graceful degradation | Sonnet |
| +1시간 | PR-1 Playwright 검증 + PR 머지 | Sonnet |
| +1.5시간 | PR-2 캡처 인프라 + v1 5종 | Sonnet |
| +2시간 | PR-3 HANDOVER + SESSION_LOG | Opus + Sonnet |
| +3시간 | PR-4 대시보드 v1 (벤치마킹 1시간 포함) | Opus + Sonnet |
| +4시간 | PR-6 기획서 변경점 + 발표 보강 | Opus + Sonnet |
| 본선 후 | PR-5 real 배포 연구 | Opus |

**Claude 토큰 한도 도달 시**:
- 즉시 `HANDOVER.md` 갱신 + 사용자에게 알림 + `/compact` 수행
- Codex GPT-5.5로 전환 → HANDOVER + SESSION_LOG 최근 3일 + dashboard/data.json만 로드

---

## 13. 참고 자료

| 출처 | 용도 | 비고 |
|---|---|---|
| `C:\Users\kik32\내 드라이브\Master_Obsidian\10_School\Obsidian_School\가천대학교\BDAI\12기\AI기반 MVP설계와 PM의사결정 실습` | PM/일정·결정 의사결정 프레임 | PR-3, PR-4 정보 구조 설계 시 |
| `C:\Users\kik32\내 드라이브\Master_Obsidian` (전체) | 코딩 패턴·재사용 컴포넌트 | 필요 시 grep |
| `smart-factory-hackathon/QualityLens_기획서.pdf` (243KB) | 기획서 vs 구현 diff 원본 | PR-6 입력 |
| UCI SECOM | 데이터 라이선스 출처 (P-A 유지) | 변경 없음 |
| Linear / Notion / Basecamp / Spotify Health Check | 대시보드 정보 구조 벤치마킹 | PR-4 |
| 비정형 데이터 처리 수업 자료 (수업 노트) | quantization · 피처 선택 근거 | PR-5 |

---

## 14. Git 워크플로우

```
(매 sub-PR)
git fetch origin main
git rebase origin/main             # 또는 merge
# ... 작업 ...
git add <specific files>
git commit -m "feat(p-b/PR-{n}): ..."
git push origin <branch>
gh pr create --title "..." --body "..."
# auto-merge: PR-Description 본문에 10단계 체크리스트 통과 + V1~V8 해당 항목 통과 명시
gh pr merge --squash --auto
```

**브랜치 이름 규칙**: `claude/p-b-pr-{n}-{short-slug}` (예: `claude/p-b-pr-1-dummy-artifacts`)

---

## 15. 셀프 리뷰 (작성자 자체)

| 항목 | 평가 | 메모 |
|---|---|---|
| 트리거 명확성 | ✅ | FileNotFoundError 스택 + 영향 범위 명시 |
| 옵션 비교 충분성 | ✅ | 5개 옵션 + 권장안 근거 |
| sub-PR 분할 합리성 | ⚠️ | 6개는 P-A 패턴과 일치. 다만 본선 4시간 내 6개 머지는 타이트 — PR-5 본선 후로 명시 ✅ |
| 하이브리드 메모리 실효성 | ⚠️ | HANDOVER.md만으로 Codex가 정말 이어받을 수 있는지 → PR-3 V7 검증으로 점검 |
| 대시보드 과잉 설계 우려 | ⚠️ | v1은 정적 HTML로 시작, WebSocket/SSE는 미적용 (YAGNI 준수) |
| 10단계 체크리스트 운영 부담 | ⚠️ | 10개 매번 채우면 무거움 → PR-Description 템플릿화로 부담 완화 (PR-3에서 같이) |
| 일정 현실성 | ❌ | 본선 09:00 KST가 D-Day이면 위 4시간 일정도 늦음. 사용자 확인 필요 |

**작성자 결정 필요 사항** (사용자 확인 요청):
1. **본선 D-Day 시간 확인**: 정말 오늘(2026-05-22) 09:00 KST인가? P-A PR-6 commit 시점이 이미 그 이후라면 본선 진행 중일 가능성.
2. **PR-4 대시보드 우선순위**: 본선 시간 부족 시 PR-4를 본선 후로 미룰지?
3. **Codex 모델 정확한 버전**: GPT-5.5 / 5.4 중 어느 것을 기본으로?

---

> **셀프 리뷰 결론**: 1~2 결정사항만 사용자가 회신해주면 PR-1 즉시 착수. 일정은 사용자 답변에 맞춰 재조정.
