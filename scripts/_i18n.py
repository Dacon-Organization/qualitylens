"""matplotlib 한글 폰트 설정 — scripts 진입점에서 한 줄 import.

사용 예::

    from _i18n import setup_korean_font
    setup_korean_font()
"""

from __future__ import annotations

import platform

import matplotlib
import matplotlib.pyplot as plt


def setup_korean_font() -> str:
    """OS에 맞는 한글 폰트를 설정하고 사용된 폰트명을 반환."""
    system = platform.system()
    if system == "Windows":
        font = "Malgun Gothic"
    elif system == "Darwin":
        font = "AppleGothic"
    else:  # Linux (Streamlit Cloud 포함) — packages.txt 의 fonts-nanum 의존
        font = "NanumGothic"

    plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False  # 음수 부호 깨짐 방지
    return font
