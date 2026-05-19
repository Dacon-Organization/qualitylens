"""matplotlib 한글 폰트 설정 — Streamlit 앱용 사본.

scripts/_i18n.py 와 동일 로직. 두 경로에서 모두 import 가능하도록 의도적 중복.
"""

from __future__ import annotations

import platform

import matplotlib.pyplot as plt


def setup_korean_font() -> str:
    system = platform.system()
    if system == "Windows":
        font = "Malgun Gothic"
    elif system == "Darwin":
        font = "AppleGothic"
    else:
        font = "NanumGothic"

    plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False
    return font
