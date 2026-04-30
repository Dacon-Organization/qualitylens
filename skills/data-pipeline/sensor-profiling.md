# Sensor Profiling

## 목적
591개 센서의 데이터 품질을 정량화하여 전처리 전략 결정에 활용.

---

## 1. 결측률 분석

### 계산
```python
missing_rate = df.isnull().mean()  # 센서별 결측률 (0.0~1.0)
```

### 드롭 기준
| 결측률 | 조치 |
|--------|------|
| > 40%  | **드롭** — 정보 부족 |
| 10~40% | KNN Imputation (k=5) |
| < 10%  | Median Imputation |

```python
# 40% 이상 결측 센서 제거
high_missing = missing_rate[missing_rate > 0.4].index
df_clean = df.drop(columns=high_missing)
# 예상 결과: 591 → ~400개 센서 남음
```

---

## 2. 분포 분석

### 통계량 계산
```python
profile = pd.DataFrame({
    'mean':     df.mean(),
    'std':      df.std(),
    'skewness': df.skew(),       # |skew| > 2 → 심각한 비대칭
    'kurtosis': df.kurtosis(),   # > 7 → 이상치 의심
    'missing':  df.isnull().mean(),
})
```

### 분포 분류
| 조건 | 분류 | 대응 |
|------|------|------|
| `|skew| < 0.5` | 정규 분포 근사 | StandardScaler |
| `0.5 ≤ |skew| < 2` | 약한 비대칭 | RobustScaler 고려 |
| `|skew| ≥ 2` | 강한 비대칭 | log1p 변환 후 스케일링 |

---

## 3. 이상치 탐지

### IQR 방법
```python
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1
outlier_mask = (df < Q1 - 1.5 * IQR) | (df > Q3 + 1.5 * IQR)
outlier_rate = outlier_mask.mean()  # 센서별 이상치 비율
```

### Z-Score 방법 (보조 확인)
```python
from scipy import stats
z_scores = np.abs(stats.zscore(df.dropna()))
# |z| > 3 → 이상치로 간주
```

### 이상치 처리 정책
- 이상치 비율 < 5%: IQR Clipping (whisker 값으로 대체)
- 이상치 비율 ≥ 5%: 분포 이상 센서로 표시 → 별도 피처 추가 검토

---

## 4. 센서 그룹핑 전략

SECOM은 센서 레이블이 익명이므로 **통계적 군집화**로 공정 단계 추정.

```python
from sklearn.cluster import KMeans

# 센서 프로파일 기반 클러스터링 (결측률 + 분산 + 평균)
sensor_features = profile[['missing', 'std', 'skewness']].fillna(0)
kmeans = KMeans(n_clusters=4, random_state=42)  # 4개 공정 단계 가정
profile['process_group'] = kmeans.fit_predict(sensor_features)
```

### 그룹 라벨 (추정)
| 그룹 | 특성 | 추정 공정 |
|------|------|-----------|
| A | 낮은 결측률, 안정적 분포 | 입력/원자재 |
| B | 중간 결측률, 높은 분산 | 가공 공정 |
| C | 높은 결측률 | 선택적 측정 공정 |
| D | 낮은 분산 (상수에 가까움) | 제거 대상 후보 |

---

## 5. 프로파일링 출력 형식

```python
# 최종 센서 프로파일 DataFrame 저장
profile.to_csv('sensor_profile.csv', index=True)
# 컬럼: sensor_id, mean, std, skewness, kurtosis, missing_rate,
#        outlier_rate_iqr, process_group, drop_flag
```

### Streamlit 시각화 (dashboard 연계)
- 결측률 히트맵: `px.imshow(missing_rate.values.reshape(...))`
- 분포 히스토그램: 상위 10개 이상 센서 선택 표시
