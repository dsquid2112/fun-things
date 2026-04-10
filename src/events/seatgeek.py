"""Fetch events from the SeatGeek API.

Covers many DMV venues that Ticketmaster misses, including:
  Arena Stage, Shakespeare Theatre Company, Signature Theatre,
  Woolly Mammoth, Studio Theatre, and more.

Free API key: https://seatgeek.com/account/develop
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import Optional
import config


CATEGORY_MAP = {
    "theater": "arts",
    "broadway_tickets_national": "arts",
    "classical": "arts",
    "opera": "arts",
    "dance_performance_tour": "arts",
    "comedy": "comedy",
    "concert": "music",
    "music_festival": "music",
    "sports": "sports",
    "family": "family",
    "cirque_du_soleil": "family",
}


def fetch_seatgeek_events(start_date: datetime, end_date: datetime) -> list[dict]:
    if not config.SEATGEEK_CLIENT_ID:
        print("  [SeatGeek] No client ID — skipping.")
        return []

    params = {
        "client_id": config.SEATGEEK_CLIENT_ID,
        "lat": config.CENTER_LAT,
        "lon": config.CENTER_LON,
        "range": f"{config.RADIUS_MILES}mi",
        "datetime_local.gte": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "datetime_local.lte": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "per_page": 100,
        "sort": "score.desc",
    }

    url = "https://api.seatgeek.com/2/events?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  [SeatGeek] Error: {e}")
        return []

    raw_events = data.get("events", [])
    return [e for e in (_normalize(r) for r in raw_events) if e]


def _normalize(raw: dict) -> Optional[dict]:
    try:
        # Date
        date_str = raw.get("datetime_local", "")
        if not date_str:
            return None
        event_date = datetime.fromisoformat(date_str)

        # Venue
        venue = raw.get("venue", {})
        venue_name = venue.get("name", "")
        city = venue.get("city", "")
        state = venue.get("state", "")

        # Category
        taxonomy = raw.get("taxonomies", [{}])
        sg_type = taxonomy[0].get("name", "other") if taxonomy else "other"
        category = CATEGORY_MAP.get(sg_type, "other")

        # Price
        stats = raw.get("stats", {})
        price_min = stats.get("lowest_price")
        price_max = stats.get("highest_price")

        # Image
        performers = raw.get("performers", [])
        image_url = performers[0].get("image") if performers else None

        # Tags
        tags = []
        if "family" in sg_type:
            tags.append("family-friendly")

        return {
            "id": f"sg_{raw['id']}",
            "source": "SeatGeek",
            "title": raw.get("title", ""),
            "description": raw.get("description", ""),
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
            "min_age": None,
            "score": 0.0,
        }
    except Exception:
        return None
