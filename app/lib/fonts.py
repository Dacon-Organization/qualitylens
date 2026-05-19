"""한글 폰트 통합 — matplotlib, plotly, HTML CSS 3중 적용.

scripts·앱·HTML 리포트 모두 같은 헬퍼를 사용해 일관된 한글 렌더링을 보장한다.
"""

from __future__ import annotations

import platform


def _detect_matplotlib_font() -> str:
    system = platform.system()
    if system == "Windows":
        return "Malgun Gothic"
    if system == "Darwin":
        return "AppleGothic"
    return "NanumGothic"  # Linux / Streamlit Cloud — fonts-nanum apt 패키지 의존


def setup_matplotlib() -> str:
    """matplotlib rcParams 에 한글 폰트 적용. 사용된 폰트명 반환."""
    import matplotlib.pyplot as plt

    font = _detect_matplotlib_font()
    plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False
    return font


def plotly_template_with_korean() -> dict:
    """plotly 차트에 적용할 layout 템플릿 — font family 한글 폰트 강제.

    사용 예::

        fig.update_layout(**plotly_template_with_korean())
    """
    return {
        "font": {"family": '"Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif'},
        "title": {"font": {"family": '"Noto Sans KR", "Malgun Gothic", sans-serif'}},
    }


def html_font_face_css() -> str:
    """HTML 리포트 <style> 블록에 삽입할 한글 폰트 선언."""
    return """
    body, html {
        font-family: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    }
    """
