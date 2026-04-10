"""Fetch events from specific local DMV theater and music venues.

Uses the Ticketmaster Discovery API filtered by known venue IDs,
so no extra API key is needed beyond the existing TICKETMASTER_KEY.

Venues covered:
  Ford's Theatre            Washington, DC
  The National Theatre      Washington, DC
  The Birchmere             Alexandria, VA
  Kennedy Center            Washington, DC
  Strathmore                North Bethesda, MD
  Wolf Trap                 Vienna, VA
  Warner Theatre            Washington, DC
  Arena Stage               Washington, DC
  Shakespeare Theatre Co.   Washington, DC
  Signature Theatre         Arlington, VA
  Woolly Mammoth Theatre    Washington, DC
  Studio Theatre            Washington, DC
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import Optional
import config


# Ticketmaster venue IDs for DMV local theaters.
# Format: (display_name, ticketmaster_venue_id)
LOCAL_THEATER_VENUES = [
    ("Ford's Theatre",               "KovZpZAE6lIA"),
    ("The National Theatre",         "KovZpZA7AAEA"),
    ("The Birchmere",                "KovZpZAakvdA"),
    ("Kennedy Center",               "KovZpZA6knIA"),
    ("Strathmore",                   "KovZpZAE6aeA"),
    ("Wolf Trap",                    "KovZpZA6k1eA"),
    ("Warner Theatre",               "KovZpZAE6atA"),
    ("Arena Stage",                  "KovZpZAE6a6A"),
    ("Shakespeare Theatre Company",  "KovZpZAE6a1A"),
    ("Signature Theatre",            "KovZpZA76knA"),
    ("Woolly Mammoth Theatre",       "KovZpZAE6aJA"),
    ("Studio Theatre",               "KovZpZAE6alA"),
]


def fetch_local_theater_events(start_date: datetime, end_date: datetime) -> list[dict]:
    """Query each local venue by ID and aggregate results."""
    if not config.TICKETMASTER_KEY:
        print("  [Local Theaters] No Ticketmaster key — skipping.")
        return []

    all_events: list[dict] = []
    for venue_name, venue_id in LOCAL_THEATER_VENUES:
        events = _fetch_venue(venue_name, venue_id, start_date, end_date)
        if events:
            print(f"    {venue_name}: {len(events)} events")
        all_events.extend(events)

    return all_events


def _fetch_venue(
    venue_name: str,
    venue_id: str,
    start_date: datetime,
    end_date: datetime,
) -> list[dict]:
    params = {
        "apikey": config.TICKETMASTER_KEY,
        "venueId": venue_id,
        "startDateTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": 50,
    }

    url = (
        "https://app.ticketmaster.com/discovery/v2/events.json?"
        + urllib.parse.urlencode(params)
    )

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    [{venue_name}] Error: {e}")
        return []

    raw_events = data.get("_embedded", {}).get("events", [])
    return [e for e in (_normalize(r, venue_name) for r in raw_events) if e]


def _normalize(raw: dict, fallback_venue: str) -> Optional[dict]:
    try:
        # Date
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
        venue_name = venue.get("name", fallback_venue)
        city = venue.get("city", {}).get("name", "")
        state = venue.get("state", {}).get("stateCode", "")

        # Category — local theaters default to "arts"
        classifications = raw.get("classifications", [{}])
        segment = (classifications[0].get("segment", {}).get("name", "")
                   if classifications else "")
        category = {
            "Music": "music",
            "Arts & Theatre": "arts",
            "Family": "family",
            "Comedy": "comedy",
        }.get(segment, "arts")   # default arts for local theaters

        # Price
        price_ranges = raw.get("priceRanges", [])
        price_min = price_ranges[0].get("min") if price_ranges else None
        price_max = price_ranges[0].get("max") if price_ranges else None

        # Image
        images = raw.get("images", [])
        image_url = next(
            (img["url"] for img in images
             if img.get("ratio") == "16_9" and img.get("width", 0) >= 640),
            images[0]["url"] if images else None,
        )

        # Age restriction
        age_restriction = raw.get("ageRestrictions", {}).get("legalAgeEnforced")
        min_age = 21 if age_restriction else None

        return {
            "id": f"tm_{raw['id']}",
            "source": f"Local Theater ({venue_name})",
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
            "tags": ["local-theater"],
            "min_age": min_age,
            "score": 0.0,
        }
    except Exception:
        return None
