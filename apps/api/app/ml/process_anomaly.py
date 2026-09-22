import math
from typing import List, Dict, Any


def extract_sequence_features(events: List[Dict[str, Any]], expected_activities: List[str]) -> Dict[str, float]:
    if not events:
        return {
            "step_count": 0.0,
            "unexpected_step_ratio": 0.0,
            "cross_system_ratio": 0.0,
            "unapproved_tool_count": 0.0,
            "avg_time_gap_seconds": 0.0,
        }

    actual_activities = [e.get("activity", "") for e in events]
    source_systems = set(e.get("source_system", "") for e in events)
    expected_set = set(expected_activities)

    unexpected_count = sum(1 for act in actual_activities if act not in expected_set)
    unexpected_ratio = unexpected_count / max(len(actual_activities), 1)

    unapproved_tools = sum(
        1 for e in events
        if "unapproved" in e.get("activity_category", "").lower()
        or "manual" in e.get("source_system", "").lower()
        or "excel" in e.get("source_system", "").lower()
    )

    # Time gaps
    timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
    time_gaps = []
    if len(timestamps) > 1:
        timestamps.sort()
        for i in range(1, len(timestamps)):
            gap = (timestamps[i] - timestamps[i - 1]).total_seconds()
            time_gaps.append(gap)

    avg_gap = sum(time_gaps) / len(time_gaps) if time_gaps else 0.0

    return {
        "step_count": float(len(events)),
        "unexpected_step_ratio": float(unexpected_ratio),
        "cross_system_ratio": float(len(source_systems) / max(len(events), 1)),
        "unapproved_tool_count": float(unapproved_tools),
        "avg_time_gap_seconds": float(avg_gap),
    }


def compute_ml_anomaly_score(events: List[Dict[str, Any]], expected_activities: List[str]) -> float:
    features = extract_sequence_features(events, expected_activities)
    
    # Heuristic statistical anomaly score model for initial rollout (0.0 to 1.0)
    score = 0.0
    score += features["unexpected_step_ratio"] * 0.45
    score += min(features["unapproved_tool_count"] * 0.20, 0.35)
    score += min(features["cross_system_ratio"] * 0.15, 0.20)

    if features["step_count"] > len(expected_activities) * 1.5:
        score += 0.15

    normalized_score = min(max(round(score, 4), 0.0), 1.0)
    return normalized_score
