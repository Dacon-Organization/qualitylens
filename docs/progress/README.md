# docs/progress/ — 작업별 진행 시각화 HTML

각 작업(S-1 ~ S-4 등)이 완료될 때마다 단일 HTML 파일을 생성해 보관한다.
복구·발표·로드맵 재구성 시 빠르게 훑어볼 수 있도록 vanilla HTML(외부 의존 X).

## 인덱스

- [INDEX.html](INDEX.html) — 전체 작업 진척 한눈에
- 각 작업 파일: `s{번호}_{kebab-case}.html`

## 작성 규칙

1. **단일 파일**: CSS/JS 인라인, 외부 CDN 금지 (오프라인 동작 보장)
2. **공통 헤더**: 작업명, 모델(Sonnet/Opus), 브랜치, PR 번호, 산출물 목록
3. **핵심 다이어그램·코드 스니펫**: 작업의 핵심을 한 화면에
4. **체크리스트**: 무엇이 끝났고 무엇이 남았는지
5. **다음 단계**: 후속 작업으로의 연결

## 명명 규칙

```
s1_risk_tier.html        ← S-1 3단계 컬러 코딩
s2_shap_waterfall.html   ← S-2 SHAP Waterfall + Dependence
s3_action_log.html       ← S-3 원클릭 수용 + 이력
s4_streaming.html        ← S-4 스트리밍 시뮬레이션
```
