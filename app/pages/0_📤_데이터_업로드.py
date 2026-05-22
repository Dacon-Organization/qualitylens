"""📤 데이터 업로드 — 사용자가 자기 공장 CSV로 즉시 추론.

MVP 핵심 갭 해결 (P-B/PR-19):
- 591개 sensor_NNN 컬럼 형식 (sample_id 선택)
- 누락 컬럼 0 자동 채움
- 즉시 추론 → pred_proba + 위험 등급
- 결과 CSV 다운로드
"""

from __future__ import annotations

import streamlit as st

from lib.data_loader import load_model, sidebar_badge
from lib.demo import demo_sidebar
from lib.onboarding import reopen_button_sidebar
from lib.upload import (
    build_sample_template,
    expected_columns,
    parse_uploaded_csv,
    predict_uploaded,
    validate_and_align,
)

st.set_page_config(
    page_title="QualityLens — 데이터 업로드",
    page_icon="📤",
    layout="wide",
)

sidebar_badge()
demo_sidebar()
reopen_button_sidebar()

st.title("📤 데이터 업로드")
st.caption(
    "자기 공장의 센서 데이터를 업로드해 **즉시 이상 확률 + 위험 등급**을 받아보세요. "
    "QualityLens MVP는 591개 sensor_NNN 컬럼 형식을 따릅니다."
)

# -----------------------------------------------------------------------------
# 1. 안내 + 샘플 다운로드
# -----------------------------------------------------------------------------

with st.expander("📋 데이터 형식 안내 (처음이라면 펼쳐서 확인)", expanded=False):
    st.markdown(
        """
        **필수 컬럼**:
        - `sensor_000` ~ `sensor_590` 중 일부 또는 전부 (591개 표준)
        - 누락된 컬럼은 자동으로 0 처리 (z-score 정규화 가정)

        **선택 컬럼**:
        - `sample_id` (없으면 행 번호 자동 할당)

        **인코딩**: UTF-8 / UTF-8-sig / CP949 자동 감지

        **권장**: SECOM 데이터셋과 동일한 z-score 정규화된 값을 사용하세요.
        다른 정규화 방식이면 결과 해석에 주의.
        """
    )
    col_dl1, col_dl2 = st.columns([1, 3])
    col_dl1.download_button(
        label="📥 샘플 CSV 다운로드",
        data=build_sample_template(),
        file_name="QualityLens_sample_template.csv",
        mime="text/csv",
        help="3행 × 592컬럼(sample_id + 591 센서) 템플릿",
        use_container_width=True,
    )
    col_dl2.caption(
        f"📐 기대 형식: **{len(expected_columns())}개 센서 컬럼** "
        f"(`sensor_000` ~ `sensor_590`) + 선택 `sample_id`"
    )

st.divider()

# -----------------------------------------------------------------------------
# 2. 파일 업로드
# -----------------------------------------------------------------------------

uploaded = st.file_uploader(
    "공장 센서 CSV 업로드",
    type=["csv"],
    help="최대 200MB. 1개 파일만.",
)

if not uploaded:
    st.info("👆 CSV 파일을 업로드하면 즉시 추론 결과가 표시됩니다.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. 파싱 + 검증
# -----------------------------------------------------------------------------

try:
    raw_df = parse_uploaded_csv(uploaded)
except (ValueError, Exception) as exc:  # noqa: BLE001
    st.error(f"❌ 파일 파싱 실패: {exc}")
    st.stop()

st.success(f"✅ 업로드 성공 — {len(raw_df):,}행 × {len(raw_df.columns):,}컬럼")

with st.expander("🔍 원본 데이터 미리보기 (상위 5행)", expanded=False):
    st.dataframe(raw_df.head(), use_container_width=True)

try:
    X_aligned, sample_ids, report = validate_and_align(raw_df)
except ValueError as exc:
    st.error(f"❌ 검증 실패: {exc}")
    st.stop()

# 검증 리포트
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
col_r1.metric("총 행 수", f"{report.n_rows:,}")
col_r2.metric(
    "유효 sensor 컬럼",
    f"{report.n_cols_present} / 591",
    f"{report.n_cols_present / 591 * 100:.1f}%",
)
col_r3.metric("0으로 채움", f"{report.n_cols_filled}")
col_r4.metric("sample_id", "있음" if report.has_sample_id else "자동 할당")

for w in report.warnings:
    st.warning(f"⚠️ {w}")

# -----------------------------------------------------------------------------
# 4. 모델 추론
# -----------------------------------------------------------------------------

model = load_model()
if model is None:
    st.error(
        "❌ 모델 산출물이 없습니다. "
        "관리자에게 `scripts/02_train.py --source dummy` 실행을 요청하세요."
    )
    st.stop()

st.divider()
st.subheader("🔬 추론 결과")

with st.spinner("추론 중..."):
    result_df = predict_uploaded(X_aligned, sample_ids, model)

# KPI 요약
total = len(result_df)
n_fail = int(result_df["pred_label"].sum())
fail_rate = n_fail / total * 100 if total else 0.0
high_risk = int((result_df["risk_tier"] == "🔴 위험").sum())

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
col_k1.metric("총 샘플", f"{total:,}")
col_k2.metric(
    "이상 판정",
    f"{n_fail:,}",
    f"{fail_rate:.1f}%",
    delta_color="inverse",
)
col_k3.metric("🔴 위험", f"{high_risk:,}")
col_k4.metric("평균 이상 확률", f"{result_df['pred_proba'].mean():.3f}")

# 결과 테이블
st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "pred_proba": st.column_config.ProgressColumn(
            "이상 확률",
            help="모델 출력 확률 (0~1)",
            format="%.4f",
            min_value=0.0,
            max_value=1.0,
        ),
        "pred_label": st.column_config.NumberColumn(
            "라벨 (0=정상, 1=이상)",
            format="%d",
        ),
    },
)

# 결과 다운로드
st.download_button(
    label="📥 추론 결과 CSV 다운로드",
    data=result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="QualityLens_upload_result.csv",
    mime="text/csv",
    use_container_width=False,
)

# -----------------------------------------------------------------------------
# 5. 다음 액션 안내
# -----------------------------------------------------------------------------

st.divider()
st.markdown(
    "**다음 단계**:\n"
    "- 🔍 **P2 원인 분석**: 위험 등급 샘플의 SHAP 기여 센서 확인\n"
    "- 🛠 **P3 조치 가이드**: 임계값 위반 센서에 원클릭 수용\n"
    "- 📜 **P4 이력 조회**: 누적 추론 + 조치 기록\n\n"
    "*업로드 결과는 세션 메모리에만 보관됩니다. 영구 저장은 다운로드 CSV로.*"
)
