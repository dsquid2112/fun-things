"""Combine events from multiple sources and deduplicate."""

from datetime import datetime


def aggregate_events(events: list[dict]) -> list[dict]:
    """Deduplicate events by title+date proximity, then sort by date."""
    seen: dict[str, dict] = {}

    for event in events:
        key = _dedup_key(event)
        if key not in seen:
            seen[key] = event
        # If duplicate exists, keep whichever has more info (image, description)
        else:
            existing = seen[key]
            if not existing.get("image_url") and event.get("image_url"):
                seen[key] = event
            elif not existing.get("description") and event.get("description"):
                seen[key]["description"] = event["description"]

    result = list(seen.values())
    result.sort(key=lambda e: e["date"])
    return result


def _dedup_key(event: dict) -> str:
    """Fuzzy key: normalized title + date (day only)."""
    title = event.get("title", "").lower().strip()
    # Remove common noise words
    for noise in ["the ", "a ", "an "]:
        if title.startswith(noise):
            title = title[len(noise):]
    date: datetime = event.get("date", datetime.min)
    return f"{title[:40]}|{date.strftime('%Y-%m-%d')}"
