"""첫 접속 onboarding 모달 — 7슬라이드 자세한 워크스루 (PR-23).

사용자 처방 반영:
- 슬라이드 5~7 신규: 데모 따라하기 / SHAP 해설 / 조치 흐름 (실제 예시 동작 자연스럽게)
- 비전문가도 한 번에 이해할 수 있도록 SVG inline + 단계별 화살표 + 구체 예시
- st.dialog(Streamlit 1.35+) 기반, 세션 내 재표시 안 함 (`_onboarded`)
"""

from __future__ import annotations

import streamlit as st


def _ensure_state() -> None:
    st.session_state.setdefault("_onboarded", False)
    st.session_state.setdefault("_onboarding_step", 0)


# -----------------------------------------------------------------------------
# 슬라이드 5/6/7용 SVG inline 자산 (정적 — Streamlit dialog 내 plotly 회피)
# -----------------------------------------------------------------------------


_SVG_DEMO_FLOW = """
<svg viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px;">
  <rect x="10" y="40" width="140" height="100" rx="10" fill="#1f6feb15" stroke="#1f6feb" stroke-width="2"/>
  <text x="80" y="80" text-anchor="middle" font-size="14" font-weight="700" fill="#1f6feb">📊 P1 실시간 예측</text>
  <text x="80" y="105" text-anchor="middle" font-size="12" fill="#0d1117">샘플 #1305</text>
  <text x="80" y="125" text-anchor="middle" font-size="13" font-weight="700" fill="#f85149">🔴 81.2%</text>

  <path d="M 160 90 L 200 90" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="210" y="40" width="160" height="100" rx="10" fill="#d2992215" stroke="#d29922" stroke-width="2"/>
  <text x="290" y="80" text-anchor="middle" font-size="14" font-weight="700" fill="#d29922">🔍 P2 원인 분석</text>
  <text x="290" y="105" text-anchor="middle" font-size="12" fill="#0d1117">SHAP Waterfall</text>
  <text x="290" y="125" text-anchor="middle" font-size="11" fill="#0d1117">"Feature 59" 영향 78%</text>

  <path d="M 380 90 L 420 90" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="430" y="40" width="140" height="100" rx="10" fill="#3fb95015" stroke="#3fb950" stroke-width="2"/>
  <text x="500" y="80" text-anchor="middle" font-size="14" font-weight="700" fill="#3fb950">🛠 P3 조치 가이드</text>
  <text x="500" y="105" text-anchor="middle" font-size="11" fill="#0d1117">챔버 냉각 밸브</text>
  <text x="500" y="125" text-anchor="middle" font-size="13" font-weight="700" fill="#3fb950">✅ 수용</text>

  <path d="M 580 90 L 620 90" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="630" y="40" width="80" height="100" rx="10" fill="#8957e515" stroke="#8957e5" stroke-width="2"/>
  <text x="670" y="80" text-anchor="middle" font-size="14" font-weight="700" fill="#8957e5">📜 P4</text>
  <text x="670" y="105" text-anchor="middle" font-size="11" fill="#0d1117">이력 기록</text>
  <text x="670" y="125" text-anchor="middle" font-size="12" font-weight="700" fill="#3fb950">PASS</text>

  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#6e7681"/>
    </marker>
  </defs>
</svg>
"""


_SVG_SHAP_EXAMPLE = """
<svg viewBox="0 0 720 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px;">
  <text x="360" y="20" text-anchor="middle" font-size="13" font-weight="700" fill="#0d1117">
    예시: 샘플 #1305의 SHAP Waterfall — "왜 이상으로 판정?"
  </text>

  <line x1="60" y1="180" x2="700" y2="180" stroke="#d0d7de" stroke-width="1"/>
  <line x1="60" y1="40" x2="60" y2="180" stroke="#d0d7de" stroke-width="1"/>
  <text x="50" y="185" text-anchor="end" font-size="10" fill="#6e7681">0.0</text>
  <text x="50" y="105" text-anchor="end" font-size="10" fill="#6e7681">0.5</text>
  <text x="50" y="45" text-anchor="end" font-size="10" fill="#6e7681">1.0</text>

  <!-- base value 0.066 (6.6% 평균) -->
  <rect x="70" y="170" width="60" height="10" fill="#6e7681"/>
  <text x="100" y="200" text-anchor="middle" font-size="10" fill="#6e7681">base</text>
  <text x="100" y="213" text-anchor="middle" font-size="9" fill="#6e7681">0.066</text>

  <!-- Feature 59 → +0.45 (큰 양의 기여, 빨강) -->
  <rect x="135" y="100" width="80" height="70" fill="#f85149"/>
  <text x="175" y="200" text-anchor="middle" font-size="10" fill="#f85149">Feature_59</text>
  <text x="175" y="213" text-anchor="middle" font-size="9" fill="#f85149">+0.45 ↑</text>

  <!-- Feature 102 → +0.25 -->
  <rect x="220" y="60" width="60" height="40" fill="#f85149" fill-opacity="0.7"/>
  <text x="250" y="200" text-anchor="middle" font-size="10" fill="#f85149">Feature_102</text>
  <text x="250" y="213" text-anchor="middle" font-size="9" fill="#f85149">+0.25 ↑</text>

  <!-- Feature 24 → -0.08 (음의 기여, 초록) -->
  <rect x="285" y="60" width="50" height="15" fill="#3fb950" fill-opacity="0.7"/>
  <text x="310" y="200" text-anchor="middle" font-size="10" fill="#3fb950">Feature_24</text>
  <text x="310" y="213" text-anchor="middle" font-size="9" fill="#3fb950">-0.08 ↓</text>

  <!-- 최종 -->
  <rect x="340" y="50" width="80" height="20" fill="#1f6feb"/>
  <text x="380" y="200" text-anchor="middle" font-size="11" font-weight="700" fill="#1f6feb">final</text>
  <text x="380" y="213" text-anchor="middle" font-size="10" font-weight="700" fill="#1f6feb">0.812 (81%)</text>

  <!-- 화살표 + 해설 -->
  <text x="500" y="80" font-size="12" fill="#f85149">🔴 양수 = 이상 확률 ↑</text>
  <text x="500" y="100" font-size="12" fill="#3fb950">🟢 음수 = 정상 확률 ↑</text>
  <text x="500" y="125" font-size="11" fill="#0d1117">→ Feature_59 가 78% 기여</text>
  <text x="500" y="142" font-size="11" fill="#0d1117">  (전체 SHAP의 |+0.45| / 0.578)</text>
</svg>
"""


_SVG_ACTION_FLOW = """
<svg viewBox="0 0 720 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px;">
  <text x="360" y="20" text-anchor="middle" font-size="13" font-weight="700" fill="#0d1117">
    조치 흐름: 위반 감지 → 권고 → 수용 → 정상 복귀
  </text>

  <!-- 1. 감지 -->
  <circle cx="80" cy="100" r="30" fill="#f8514920" stroke="#f85149" stroke-width="2"/>
  <text x="80" y="106" text-anchor="middle" font-size="20">🚨</text>
  <text x="80" y="155" text-anchor="middle" font-size="12" font-weight="700" fill="#f85149">1. 감지</text>
  <text x="80" y="175" text-anchor="middle" font-size="10" fill="#0d1117">Feature_59</text>
  <text x="80" y="190" text-anchor="middle" font-size="10" fill="#0d1117">+4.2σ 초과</text>

  <path d="M 115 100 L 165 100" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow2)"/>

  <!-- 2. 권고 -->
  <circle cx="200" cy="100" r="30" fill="#d2992220" stroke="#d29922" stroke-width="2"/>
  <text x="200" y="106" text-anchor="middle" font-size="20">📋</text>
  <text x="200" y="155" text-anchor="middle" font-size="12" font-weight="700" fill="#d29922">2. 권고</text>
  <text x="200" y="175" text-anchor="middle" font-size="10" fill="#0d1117">"챔버 냉각</text>
  <text x="200" y="190" text-anchor="middle" font-size="10" fill="#0d1117">밸브 5% 개방"</text>

  <path d="M 235 100 L 285 100" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow2)"/>

  <!-- 3. 수용 (1-Click) -->
  <circle cx="320" cy="100" r="30" fill="#1f6feb20" stroke="#1f6feb" stroke-width="2"/>
  <text x="320" y="106" text-anchor="middle" font-size="20">👆</text>
  <text x="320" y="155" text-anchor="middle" font-size="12" font-weight="700" fill="#1f6feb">3. 수용</text>
  <text x="320" y="175" text-anchor="middle" font-size="10" fill="#0d1117">✅ 클릭</text>
  <text x="320" y="190" text-anchor="middle" font-size="10" fill="#0d1117">현장 작업자</text>

  <path d="M 355 100 L 405 100" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow2)"/>

  <!-- 4. 기록 -->
  <circle cx="440" cy="100" r="30" fill="#8957e520" stroke="#8957e5" stroke-width="2"/>
  <text x="440" y="106" text-anchor="middle" font-size="20">📜</text>
  <text x="440" y="155" text-anchor="middle" font-size="12" font-weight="700" fill="#8957e5">4. 기록</text>
  <text x="440" y="175" text-anchor="middle" font-size="10" fill="#0d1117">P4 자동</text>
  <text x="440" y="190" text-anchor="middle" font-size="10" fill="#0d1117">이력 추가</text>

  <path d="M 475 100 L 525 100" stroke="#6e7681" stroke-width="2" marker-end="url(#arrow2)"/>

  <!-- 5. 복귀 -->
  <circle cx="560" cy="100" r="30" fill="#3fb95020" stroke="#3fb950" stroke-width="2"/>
  <text x="560" y="106" text-anchor="middle" font-size="20">✅</text>
  <text x="560" y="155" text-anchor="middle" font-size="12" font-weight="700" fill="#3fb950">5. 복귀</text>
  <text x="560" y="175" text-anchor="middle" font-size="10" fill="#0d1117">이상 확률</text>
  <text x="560" y="190" text-anchor="middle" font-size="10" fill="#3fb950">81% → 12%</text>

  <!-- 결과 -->
  <rect x="605" y="80" width="105" height="50" rx="8" fill="#3fb95015" stroke="#3fb950" stroke-width="2"/>
  <text x="657" y="100" text-anchor="middle" font-size="11" font-weight="700" fill="#3fb950">💰 결과</text>
  <text x="657" y="118" text-anchor="middle" font-size="10" fill="#0d1117">불량 1건 예방</text>
  <text x="657" y="130" text-anchor="middle" font-size="10" fill="#0d1117">≈ 100만 원 절감</text>

  <defs>
    <marker id="arrow2" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#6e7681"/>
    </marker>
  </defs>
</svg>
"""


@st.dialog("👋 QualityLens — 처음 오셨나요? (2분 안내)", width="large")
def _onboarding_dialog() -> None:
    """7슬라이드 워크스루 — 비전문가용 자세한 안내 (PR-23)."""
    step = st.session_state.get("_onboarding_step", 0)

    # 슬라이드 1~4: 기존 (브랜딩 + 업로드 + 4영역 + 사이클)
    # 슬라이드 5~7: 신규 (데모 흐름 + SHAP 예시 + 조치 흐름) — SVG inline 시각화
    slides = [
        # 1
        {
            "title": "🏭 QualityLens — 투명한 제조 AI",
            "render": lambda: _slide_welcome(),
        },
        # 2
        {
            "title": "📤 1단계 — 자기 공장 데이터 업로드",
            "render": lambda: _slide_upload(),
        },
        # 3
        {
            "title": "🔄 2단계 — 4영역 통합 흐름",
            "render": lambda: _slide_four_domains(),
        },
        # 4
        {
            "title": "🎯 3단계 — Predict → Explain → Act 사이클",
            "render": lambda: _slide_cycle(),
        },
        # 5 신규 — 데모 따라하기
        {
            "title": "🎬 4단계 — 데모 따라하기 (P1 → P2 → P3 → P4)",
            "render": lambda: _slide_demo_walkthrough(),
        },
        # 6 신규 — SHAP 해설
        {
            "title": "💡 5단계 — SHAP이 뭐예요? (비전문가용 1분 해설)",
            "render": lambda: _slide_shap_explainer(),
        },
        # 7 신규 — 조치 흐름
        {
            "title": "🛠 6단계 — 조치 흐름: 감지 → 권고 → 수용 → 복귀",
            "render": lambda: _slide_action_flow(),
        },
    ]

    current = slides[step]
    st.subheader(current["title"])
    current["render"]()

    st.progress((step + 1) / len(slides), text=f"{step + 1} / {len(slides)}")

    col_back, col_skip, col_next = st.columns([1, 2, 1])
    if step > 0:
        if col_back.button("◀ 이전", use_container_width=True, key="ob_back"):
            st.session_state["_onboarding_step"] = step - 1
            st.rerun()
    if col_skip.button("나중에 보기 (X)", use_container_width=True, key="ob_skip"):
        st.session_state["_onboarded"] = True
        st.rerun()
    if step < len(slides) - 1:
        if col_next.button("다음 ▶", use_container_width=True, key="ob_next"):
            st.session_state["_onboarding_step"] = step + 1
            st.rerun()
    else:
        if col_next.button("✅ 시작하기", use_container_width=True, key="ob_done"):
            st.session_state["_onboarded"] = True
            st.session_state["_onboarding_step"] = 0
            st.rerun()


# -----------------------------------------------------------------------------
# 슬라이드 렌더 함수 (각 슬라이드별 분리)
# -----------------------------------------------------------------------------


def _slide_welcome() -> None:
    st.markdown(
        "기존 제조 AI는 *왜 불량인지* 알려주지 않는 블랙박스였습니다.\n\n"
        "QualityLens는 **Quality(품질)** 를 **Lens(렌즈)** 로 들여다보는 "
        "투명 AI 플랫폼입니다.\n\n"
        "- ✅ 591개 센서 데이터를 30초 안에 분석\n"
        "- ✅ SHAP 기반 설명력 — *어떤 센서가 왜 문제인지* 시각화\n"
        "- ✅ 중소 제조 현장 작업자가 첫날부터 사용 가능\n\n"
        "**대상 사용자**: 현장 작업자 · 공정팀 / QC · 생산관리자 · 경영진"
    )


def _slide_upload() -> None:
    st.markdown(
        "왼쪽 사이드바 **`📤 데이터 업로드`** 메뉴에서:\n\n"
        "1. **샘플 CSV 템플릿 다운로드** — 591개 sensor 컬럼 형식 확인\n"
        "2. **자기 공장 CSV 업로드** — `sensor_000` ~ `sensor_590` 컬럼\n"
        "   - 누락된 센서는 자동으로 0 처리 (z-score 평균)\n"
        "   - `sample_id` 컬럼 선택 사항\n"
        "3. **즉시 추론** — 행마다 이상 확률 + 위험 등급 (🟢/🟡/🔴)\n"
        "4. **데이터 프로파일링 카드** — 업로드 직후 센서 수, 결측률, 불량률 자동 표시\n\n"
        "💡 **처음에는 데모 모드** 로 둘러보세요 — 사이드바 라디오에서 전환.\n\n"
        "📌 업로드 데이터는 **세션 메모리에만 보관** (개인정보·영업비밀 보호)."
    )


def _slide_four_domains() -> None:
    st.markdown(
        "QualityLens는 단순 품질 모듈이 아닌 **통합 플랫폼 MVP** 입니다.\n\n"
        "| 영역 | 페이지 | 핵심 기능 |\n"
        "|---|---|---|\n"
        "| 🛡️ **품질** | 메인 + P1/P2 | 이상 확률 + SHAP 원인 분석 |\n"
        "| 🚨 **안전** | 메인 상단 배너 | 임계값 초과 자동 알림 (3단계) |\n"
        "| ⚙️ **설비** | P5 SPC + Pareto | Western Electric Rules 자동 감지 |\n"
        "| 📈 **생산** | P4 이력 + KPI | 누적 이력 + 비즈니스 임팩트 추적 |\n\n"
        "*대회 평가 항목 \"플랫폼 기획\" 20점이 이 4영역 통합으로 평가됩니다.*"
    )


def _slide_cycle() -> None:
    st.markdown(
        "**P1 실시간 예측** → **P2 원인 분석 (SHAP)** → "
        "**P3 조치 가이드** → **P4 이력**\n\n"
        "현장 작업자가 사고하고 행동하는 표준 절차(SOP)를 그대로 따릅니다.\n\n"
        "**예시 시나리오** (다음 슬라이드에서 자세히):\n"
        "- 🔴 P1에서 이상 확률 81% 감지 → 🔍 P2 SHAP으로 \"Feature_59\" 78% 기여 확인\n"
        "- 🛠 P3에서 \"챔버 냉각 밸브 5% 개방\" 권고 → ✅ 수용 → 📜 P4 자동 기록\n\n"
        "*시연 영상 5분 30초 — `docs/presentation/demo_video_guide.md` 참조*"
    )


def _slide_demo_walkthrough() -> None:
    st.markdown(
        "**사용자 처방**: 실제 동작 흐름을 한눈에 봅니다.\n\n"
        "다음과 같이 4페이지를 순서대로 거치며 *왜 불량인지 → 어떻게 조치할지 → "
        "결과가 어땠는지* 모두 확인합니다:"
    )
    st.markdown(_SVG_DEMO_FLOW, unsafe_allow_html=True)
    st.info(
        "💡 **이대로 따라해보세요**: 메인 페이지 사이드바에서 **🎬 데모 모드** 선택 → "
        "P1 페이지 ▶ 시작 버튼 → 스트리밍 시뮬레이션 자동 재생"
    )


def _slide_shap_explainer() -> None:
    st.markdown(
        "**SHAP** (SHapley Additive exPlanations) — *어떤 센서가 이상 판정에 "
        "얼마나 기여했는지* 자동 분석.\n\n"
        "🔴 **양수** = 이상 확률 ↑ &nbsp;&nbsp; "
        "🟢 **음수** = 정상 확률 ↑"
    )
    st.markdown(_SVG_SHAP_EXAMPLE, unsafe_allow_html=True)
    st.markdown(
        "**한 줄 해석**: 위 예시에서 **Feature_59** 가 전체 SHAP 영향도의 "
        "**78% (|+0.45| / 0.578)** 를 차지 — 이 센서를 **최우선 점검** 대상으로."
    )
    st.success(
        "💡 P2 페이지에서 이 차트를 **샘플마다 자동 생성**합니다. "
        "비전문가도 \"이 센서를 보면 되겠다\" 즉시 파악 가능."
    )


def _slide_action_flow() -> None:
    st.markdown(
        "**5단계 조치 사이클** — 평균 6시간 헤매던 작업을 "
        "**3분 안에 완료**할 수 있게 합니다."
    )
    st.markdown(_SVG_ACTION_FLOW, unsafe_allow_html=True)
    st.markdown(
        "**P3 페이지에서 자동으로**:\n"
        "1. 임계값 위반 센서를 ±σ 편차 큰 순으로 정렬\n"
        "2. 룰베이스 매핑으로 **구체적인 조치 권고** 생성 "
        "(예: \"챔버 냉각 밸브 5% 개방\")\n"
        "3. ✅ **원클릭 수용** → 설비팀 알림 + P4 이력 자동 기록\n"
        "4. P1 차트가 정상으로 복귀하는 시뮬레이션 (피드백 루프)"
    )
    st.success(
        "🎯 **이제 시작하세요** — 사이드바에서 데모 모드 선택 → 메인 페이지로! "
        "또는 📤 데이터 업로드에서 자기 공장 CSV 분석."
    )


def maybe_show_onboarding() -> None:
    """앱 진입 시 호출 — 첫 접속이면 모달 자동 표시."""
    _ensure_state()
    if not st.session_state["_onboarded"]:
        _onboarding_dialog()


def reopen_button_sidebar() -> None:
    """사이드바 도움말 버튼 — 모달 재오픈."""
    if st.sidebar.button("❓ 사용 안내 다시 보기", use_container_width=True):
        st.session_state["_onboarded"] = False
        st.session_state["_onboarding_step"] = 0
        st.rerun()
