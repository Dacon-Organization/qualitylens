# Raw Data

원본 데이터셋 배치 위치. git에 포함하지 않음.

## UCI SECOM

- 출처: <https://archive.ics.uci.edu/dataset/179/secom>
- 파일:
  - `secom.data` — 1567 × 591 float (공백 구분)
  - `secom_labels.data` — 1567 × 2 (label, timestamp)
- 다운로드 후 이 폴더에 그대로 배치

```
data/raw/
├── secom.data
└── secom_labels.data
```

## 더미 모드

원본 데이터가 없으면 `scripts/01_preprocess.py` 가 자동으로 더미 데이터를 생성해
파이프라인 전체가 동작하도록 폴백합니다. 데모·개발용으로는 더미 모드로 충분합니다.
