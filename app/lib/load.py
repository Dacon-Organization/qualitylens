"""모델·데이터 로드 — data_loader 로 위임.

기존 호출자(``app/app.py``, ``app/pages/*.py``)의 import 호환성을 위해
함수 시그니처를 유지하면서 내부 구현을 ``data_loader`` 로 위임한다.
"""

from __future__ import annotations

from . import data_loader

load_model = data_loader.load_model
load_explainer = data_loader.load_explainer
load_test_set = data_loader.load_test_set
load_demo_sample = data_loader.load_demo_sample
load_demo_result = data_loader.load_demo_result
load_thresholds = data_loader.load_thresholds
load_shap_top20 = data_loader.load_shap_top20
load_shap_per_sample = data_loader.load_shap_per_sample
load_shap_waterfall_demo = data_loader.load_shap_waterfall_demo
load_shap_values_test = data_loader.load_shap_values_test
status_banner = data_loader.status_banner
