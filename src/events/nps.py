"""Fetch events from the National Park Service Events API."""

import requests
from datetime import datetime
from typing import Optional
import config


def fetch_nps_events(start_date: datetime, end_date: datetime) -> list[dict]:
    if not config.NPS_KEY:
        print("  [NPS] No API key — skipping.")
        return []

    params = {
        "api_key": config.NPS_KEY,
        "parkCode": config.NPS_PARK_CODES,
        "dateStart": start_date.strftime("%Y-%m-%d"),
        "dateEnd": end_date.strftime("%Y-%m-%d"),
        "limit": 100,
    }

    try:
        resp = requests.get(
            "https://developer.nps.gov/api/v1/events",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [NPS] Error: {e}")
        return []

    raw_events = data.get("data", [])
    return [e for e in (_normalize(r) for r in raw_events) if e]


def _normalize(raw: dict) -> Optional[dict]:
    try:
        date_str = raw.get("date", "")
        if not date_str:
            return None
        event_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Try to parse time
        times = raw.get("times", [])
        if times:
            time_str = times[0].get("timeStart", "")
            if time_str:
                try:
                    t = datetime.strptime(time_str, "%H:%M:%S")
                    event_date = event_date.replace(hour=t.hour, minute=t.minute)
                except ValueError:
                    pass

        park_full = raw.get("parkFullName", "National Park")
        location = raw.get("location", "")

        # Category: NPS events are mostly outdoor/family/education
        types = raw.get("types", [])
        type_names = [t.get("name", "").lower() for t in types]
        if any("family" in t or "youth" in t or "kid" in t for t in type_names):
            category = "family"
        elif any("nature" in t or "hike" in t or "walk" in t or "outdoor" in t for t in type_names):
            category = "outdoor"
        else:
            category = "outdoor"  # NPS events default to outdoor

        tags = ["free", "outdoor", "family-friendly"]

        image_url = None
        images = raw.get("images", [])
        if images:
            image_url = images[0].get("url")

        return {
            "id": f"nps_{raw.get('id', '')}",
            "source": "National Park Service",
            "title": raw.get("title", ""),
            "description": raw.get("description", ""),
            "date": event_date,
            "venue": park_full,
            "city": location or "DMV Area",
            "state": "",
            "url": raw.get("url", "https://www.nps.gov"),
            "image_url": image_url,
            "price_min": 0.0,
            "price_max": 0.0,
            "category": category,
            "tags": tags,
            "min_age": None,
            "score": 0.0,
        }
    except Exception:
        return None
