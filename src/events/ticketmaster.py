"""Fetch events from the Ticketmaster Discovery API."""

import requests
from datetime import datetime
from typing import Optional
import config


CATEGORY_MAP = {
    "Music": "music",
    "Sports": "sports",
    "Arts & Theatre": "arts",
    "Film": "arts",
    "Miscellaneous": "other",
    "Family": "family",
    "Comedy": "comedy",
    "Food & Drink": "food",
}


def fetch_ticketmaster_events(
    start_date: datetime,
    end_date: datetime,
    page_size: int = 100,
) -> list[dict]:
    if not config.TICKETMASTER_KEY:
        print("  [Ticketmaster] No API key — skipping.")
        return []

    params = {
        "apikey": config.TICKETMASTER_KEY,
        "latlong": f"{config.CENTER_LAT},{config.CENTER_LON}",
        "radius": config.RADIUS_MILES,
        "unit": "miles",
        "countryCode": "US",
        "startDateTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": page_size,
        "sort": "relevance,desc",
    }

    try:
        resp = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Ticketmaster] Error: {e}")
        return []

    raw_events = data.get("_embedded", {}).get("events", [])
    return [_normalize(e) for e in raw_events if _normalize(e)]


def _normalize(raw: dict) -> Optional[dict]:
    try:
        # Date/time
        dates = raw.get("dates", {}).get("start", {})
        date_str = dates.get("dateTime") or dates.get("localDate")
        if not date_str:
            return None
        try:
            event_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            event_date = datetime.strptime(date_str[:10], "%Y-%m-%d")

        # Venue
        venues = raw.get("_embedded", {}).get("venues", [{}])
        venue = venues[0] if venues else {}
        venue_name = venue.get("name", "")
        city = venue.get("city", {}).get("name", "")
        state = venue.get("state", {}).get("stateCode", "")

        # Price
        price_ranges = raw.get("priceRanges", [])
        price_min = price_ranges[0].get("min") if price_ranges else None
        price_max = price_ranges[0].get("max") if price_ranges else None

        # Category
        classifications = raw.get("classifications", [{}])
        segment = classifications[0].get("segment", {}).get("name", "other") if classifications else "other"
        category = CATEGORY_MAP.get(segment, "other")

        # Family friendly
        tags = []
        if category == "family":
            tags.append("family-friendly")
        age_restriction = raw.get("ageRestrictions", {}).get("legalAgeEnforced")
        min_age = 21 if age_restriction else None

        # Image
        images = raw.get("images", [])
        image_url = next(
            (img["url"] for img in images if img.get("ratio") == "16_9" and img.get("width", 0) >= 640),
            images[0]["url"] if images else None,
        )

        return {
            "id": f"tm_{raw['id']}",
            "source": "Ticketmaster",
            "title": raw.get("name", ""),
            "description": raw.get("info") or raw.get("pleaseNote") or "",
            "date": event_date,
            "venue": venue_name,
            "city": city,
            "state": state,
            "url": raw.get("url", ""),
            "image_url": image_url,
            "price_min": price_min,
            "price_max": price_max,
            "category": category,
            "tags": tags,
            "min_age": min_age,
            "score": 0.0,
        }
    except Exception:
        return None
