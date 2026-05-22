"""SHAP top sensor → 구체적 조치 권고 룰베이스 (PR-26 Step 9).

사용자 처방: "Step 8에서 '챔버 온도'가 원인으로 지목되었다면,
3번 탭에서는 반드시 '챔버 냉각 밸브 5% 개방'이라는 맞춤형 솔루션이 떠야 합니다.
(Rule-base로 매핑해두면 됩니다.)"

P3 조치 가이드에서 SHAP top 3 sensor → 자동 권고 매칭.
매핑 없는 센서는 graceful — 일반 권고 ("현장 점검 요청").
"""

from __future__ import annotations

# === 룰베이스 매핑 ========================================================
ACTION_RULES: dict[str, dict] = {
    "sensor_003": {
        "name": "식각 챔버 온도",
        "action": "챔버 냉각 밸브 5% 개방 · 냉각수 유량 +10% 증가",
        "priority": "high",
        "estimated_minutes": 3,
        "category": "온도 제어",
    },
    "sensor_017": {
        "name": "증착 두께",
        "action": "증착 시간 -2초 조정 · 가스 유량 캘리브레이션",
        "priority": "high",
        "estimated_minutes": 5,
        "category": "박막 두께",
    },
    "sensor_042": {
        "name": "에칭 가스 유량",
        "action": "MFC(질량유량 컨트롤러) 재캘리브레이션 · 가스 라인 점검",
        "priority": "high",
        "estimated_minutes": 10,
        "category": "가스 제어",
    },
    "sensor_056": {
        "name": "플라즈마 전력",
        "action": "RF 매칭 박스 점검 · 전극 청소",
        "priority": "medium",
        "estimated_minutes": 15,
        "category": "RF 시스템",
    },
    "sensor_146": {
        "name": "진공도",
        "action": "터보 펌프 점검 · O-링 누설 확인",
        "priority": "high",
        "estimated_minutes": 20,
        "category": "진공 시스템",
    },
    "sensor_184": {
        "name": "웨이퍼 회전속도",
        "action": "스핀 코터 모터 점검 · 베어링 윤활",
        "priority": "medium",
        "estimated_minutes": 8,
        "category": "기계 구동",
    },
    "sensor_308": {
        "name": "온도 변화율",
        "action": "히터 PID 튜닝 · 온도 센서 캘리브레이션",
        "priority": "medium",
        "estimated_minutes": 5,
        "category": "온도 제어",
    },
    "sensor_488": {
        "name": "냉각수 유량",
        "action": "냉각수 필터 교체 · 펌프 압력 확인",
        "priority": "medium",
        "estimated_minutes": 12,
        "category": "냉각 시스템",
    },
    "sensor_533": {
        "name": "압력 차이",
        "action": "챔버 간 격벽 누설 점검 · 게이지 캘리브레이션",
        "priority": "high",
        "estimated_minutes": 18,
        "category": "압력 시스템",
    },
    "sensor_021": {
        "name": "RF 매칭률",
        "action": "매칭 박스 자동 튜닝 실행 · 전극 청소",
        "priority": "medium",
        "estimated_minutes": 10,
        "category": "RF 시스템",
    },
}


_DEFAULT_ACTION = {
    "name": "(매핑 미정 센서)",
    "action": "현장 점검 요청 — 도메인 전문가 확인 권고",
    "priority": "low",
    "estimated_minutes": 30,
    "category": "기타",
}


def get_action(feature_id: str) -> dict:
    """센서 ID → 구체적 조치 권고. 매핑 없으면 일반 권고."""
    if feature_id in ACTION_RULES:
        return ACTION_RULES[feature_id]
    return {**_DEFAULT_ACTION, "name": feature_id}


def has_rule(feature_id: str) -> bool:
    """룰 매핑 존재 여부."""
    return feature_id in ACTION_RULES


def get_top_actions(feature_ids: list[str], n: int = 3) -> list[dict]:
    """상위 N개 센서의 조치 권고 리스트 (P3에서 SHAP top N과 결합)."""
    return [{"sensor": fid, **get_action(fid)} for fid in feature_ids[:n]]


def priority_badge(priority: str) -> str:
    """우선순위 → 이모지 + 한글 (시각 표시용)."""
    return {
        "high": "🔴 긴급",
        "medium": "🟡 보통",
        "low": "🔵 낮음",
    }.get(priority, "⚪ 미정")
