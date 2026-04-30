# Dataset Specs

## 1. UCI SECOM Dataset

### 기본 스펙
- **샘플 수**: 1,567 rows
- **피처 수**: 591 (모두 센서 측정값, 익명 처리됨)
- **타겟 컬럼**: `Pass/Fail` — Pass = -1, Fail = 1
- **타임스탬프**: `Time` 컬럼 (datetime 형식)
- **불량률**: 6.6% (104 Fail / 1,567 total)
- **결측치**: 다수 센서에 결측 존재 (일부 센서 >80%)

### 파일 구조
```
secom.data      → 센서값 (space-delimited, 591 columns)
secom_labels.data → 레이블 (Pass/Fail + Timestamp)
```

### 로딩 규칙
```python
# secom.data — 헤더 없음, NaN은 공백 또는 'NaN'
df_sensors = pd.read_csv('secom.data', sep=' ', header=None)
df_labels  = pd.read_csv('secom_labels.data', sep=' ', header=None,
                          names=['label', 'timestamp'])
df = pd.concat([df_sensors, df_labels], axis=1)
```

---

## 2. Kaggle Smart Manufacturing Dataset

### 기본 스펙
- **주요 컬럼**: temperature, pressure, vibration, flow_rate, humidity, rpm, voltage, current
- **타겟 컬럼**: `failure` (0/1) 또는 `quality` (0/1)
- **타임스탬프**: `datetime` 또는 `timestamp`

### 로딩 규칙
```python
df_kaggle = pd.read_csv('smart_manufacturing.csv', parse_dates=['datetime'])
```

---

## 3. 컬럼 매핑 전략

### 레이블 통일
| 원본 값 | 통일 값 | 의미 |
|---------|---------|------|
| SECOM: -1 | 0 | 정상 (Pass) |
| SECOM: 1  | 1 | 불량 (Fail) |
| Kaggle: 0 | 0 | 정상 |
| Kaggle: 1 | 1 | 불량 |

```python
# SECOM 레이블 변환
df['label'] = df['label'].map({-1: 0, 1: 1})
```

### 공통 스키마 (merged 사용 시)
| 통합 컬럼명 | SECOM 원본 | Kaggle 원본 |
|-------------|------------|-------------|
| `label` | Pass/Fail (변환) | failure |
| `timestamp` | Time | datetime |
| `sensor_*` | 0~590 (rename) | temperature 등 |

---

## 4. Data Dictionary 형식

```python
data_dict = {
    'sensor_id':    'int — 센서 번호 (0~590)',
    'missing_rate': 'float — 결측률 (0.0~1.0)',
    'process_stage':'str — 공정 단계 (A/B/C/D)',
    'unit':         'str — 측정 단위 (추정)',
    'label':        'int — 0=정상, 1=불량',
}
```

---

## 주의사항
- SECOM 센서 컬럼은 익명 처리 → 도메인 해석 불가, 통계적 접근 위주
- 두 데이터셋 병합 시 피처 공간이 다름 → 개별 모델 또는 공통 피처만 추출
- 타임스탬프는 streaming-sim.md에서 재활용
