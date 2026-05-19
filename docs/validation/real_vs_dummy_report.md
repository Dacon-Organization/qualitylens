# real vs dummy 비교 보고서

> 생성: scripts/04_compare_real_vs_dummy.py 자동 실행 산출물
> Spec: smart-factory-hackathon/docs/spec_p_a_real_data_integration.md

## 1. 데이터 비교

| source   |   rows |   features |   missing_rate |   fail_rate |
|:---------|-------:|-----------:|---------------:|------------:|
| real     |    314 |        248 |         0.0000 |      0.0669 |
| dummy    |    314 |        591 |         0.0000 |      0.0669 |

## 2. 분포 비교 (상위 5개 SHAP 피처)

![distribution](assets/charts/validation/distribution_top5.png)

## 3. 모델 성능

| source   |   roc_auc |   pr_auc |   mcc_default |   mcc_opt |   f1_opt |   best_threshold |
|:---------|----------:|---------:|--------------:|----------:|---------:|-----------------:|
| real     |    0.7396 |   0.1813 |        0.1388 |    0.2629 |   0.3000 |           0.0311 |
| dummy    |    0.9818 |   0.8229 |        0.6834 |    0.6302 |   0.6087 |           0.0308 |

## 4. ROC · PR 곡선

![roc_pr](assets/charts/validation/roc_pr_curves.png)

## 5. SHAP Top 10 겹침

- **겹침 (0/10)**: (없음)
- **real 만**: ['sensor_033', 'sensor_059', 'sensor_129', 'sensor_197', 'sensor_205', 'sensor_213', 'sensor_419', 'sensor_486', 'sensor_500', 'sensor_511']
- **dummy 만**: ['sensor_003', 'sensor_017', 'sensor_042', 'sensor_056', 'sensor_140', 'sensor_146', 'sensor_184', 'sensor_308', 'sensor_488', 'sensor_533']

## 6. 데모 4건 Waterfall 비교

| source   |   sample_id |   final_logit | top_features                       |
|:---------|------------:|--------------:|:-----------------------------------|
| real     |         154 |       -6.3276 | sensor_419, sensor_511, sensor_031 |
| real     |          62 |       -5.5164 | sensor_419, sensor_059, sensor_197 |
| real     |         246 |       -4.3910 | sensor_059, sensor_031, sensor_511 |
| real     |        1315 |       -5.2866 | sensor_059, sensor_419, sensor_500 |
| dummy    |         253 |       -1.6493 | sensor_003, sensor_042, sensor_017 |
| dummy    |         208 |        1.4961 | sensor_017, sensor_042, sensor_003 |
| dummy    |         225 |       -3.4740 | sensor_017, sensor_003, sensor_042 |
| dummy    |        1305 |       -8.0383 | sensor_003, sensor_042, sensor_017 |

## 결론 요약

- **모델 성능**: 실데이터 ROC-AUC = 0.740, 더미 = 0.982 (Δ -0.242).
  실데이터·더미 성능이 유사 — 더미가 합리적으로 설계됨.
- **SHAP Top 10 겹침**: 0/10 (0%). 공통 센서: 없음.
- **익명화 한계 주의**: SECOM 센서 의미 라벨은 익명화되어 있어 "어떤 센서가 식각 온도인지" 검증 불가.
  본 보고서는 분포·기여도 패턴만 검증하며, 라벨 매핑은 발표 단계의 기획 가정.
- **본선 발표 활용**: `slides_outline.md` Slide 4 의 "Real Data Verified" 문구에 ROC-AUC = 0.740 인용 가능.

