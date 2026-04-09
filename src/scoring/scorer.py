"""Score and rank events based on preferences and past votes."""

import json
import os
from datetime import datetime

VOTES_FILE = os.path.join(os.path.dirname(__file__), "../../data/votes.json")
PREFS_FILE = os.path.join(os.path.dirname(__file__), "../../data/preferences.json")


def score_and_sort(events: list[dict]) -> list[dict]:
    prefs = _load_json(PREFS_FILE)
    votes = _load_json(VOTES_FILE)

    vote_map = _build_vote_map(votes)
    category_scores = _build_category_scores(votes, prefs)

    for event in events:
        event["score"] = _score_event(event, prefs, vote_map, category_scores)

    events.sort(key=lambda e: e["score"], reverse=True)
    return events


def _score_event(
    event: dict,
    prefs: dict,
    vote_map: dict[str, int],
    category_scores: dict[str, float],
) -> float:
    score = 0.0
    category = event.get("category", "other")

    # Base score from category weight
    cat_weights = prefs.get("category_weights", {})
    score += cat_weights.get(category, 0.7)

    # Boost from learned category preferences (from vote history)
    score += category_scores.get(category, 0.0)

    # Direct vote on this exact event
    event_id = event.get("id", "")
    if event_id in vote_map:
        v = vote_map[event_id]
        if v > 0:
            score += prefs.get("vote_up_weight", 0.8) * v
        else:
            score += prefs.get("vote_down_weight", -1.2) * abs(v)

    # Free event bonus
    if event.get("price_min", None) == 0.0:
        score += prefs.get("free_event_bonus", 0.3)

    # Age-appropriate for 13-year-old (exclude 21+ events)
    if event.get("min_age") and event["min_age"] >= 21:
        score -= 5.0  # Strongly penalize — not a family event

    # Small recency bonus: sooner events score slightly higher
    days_away = max(0, (event["date"] - datetime.now()).days)
    score += max(0, (14 - days_away) * 0.03)

    return round(score, 3)


def _build_vote_map(votes: list[dict]) -> dict[str, int]:
    """Sum all votes per event_id: +1 per up, -1 per down."""
    vote_map: dict[str, int] = {}
    for v in votes:
        eid = v.get("event_id", "")
        val = 1 if v.get("vote") == "up" else -1
        vote_map[eid] = vote_map.get(eid, 0) + val
    return vote_map


def _build_category_scores(votes: list[dict], prefs: dict) -> dict[str, float]:
    """Accumulate vote signals by category to learn preferences over time."""
    cat_counts: dict[str, float] = {}
    up_w = prefs.get("vote_up_weight", 0.8)
    down_w = prefs.get("vote_down_weight", -1.2)

    for v in votes:
        cat = v.get("category", "other")
        val = up_w if v.get("vote") == "up" else down_w
        cat_counts[cat] = cat_counts.get(cat, 0.0) + val

    # Normalize: cap at +/- 1.5 so one bad category doesn't dominate
    return {k: max(-1.5, min(1.5, v * 0.1)) for k, v in cat_counts.items()}


def _load_json(path: str) -> any:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if "preferences" in path else []
