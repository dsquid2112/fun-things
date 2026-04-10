#!/usr/bin/env python3
"""Fun Things — weekly DMV family event digest."""

from datetime import datetime, timedelta
import sys

import config
from src.events.ticketmaster import fetch_ticketmaster_events
from src.events.nps import fetch_nps_events
from src.events.seatgeek import fetch_seatgeek_events
from src.events.local_theaters import fetch_local_theater_events
from src.events.aggregator import aggregate_events
from src.scoring.scorer import score_and_sort
from src.email.builder import build_email
from src.email.sender import send_email


def main() -> None:
    now = datetime.now()
    end = now + timedelta(days=config.LOOKAHEAD_DAYS)
    print(f"Fun Things digest — {now.strftime('%B %d, %Y')}")
    print(f"Looking for events: {now.strftime('%b %-d')} → {end.strftime('%b %-d')}\n")

    # --- Fetch ---
    events: list[dict] = []

    tm_events = fetch_ticketmaster_events(now, end)
    events.extend(tm_events)
    print(f"  Ticketmaster (general): {len(tm_events)} events")

    print("  Local Theaters (by venue):")
    theater_events = fetch_local_theater_events(now, end)
    events.extend(theater_events)
    print(f"  Local Theaters total: {len(theater_events)} events")

    sg_events = fetch_seatgeek_events(now, end)
    events.extend(sg_events)
    print(f"  SeatGeek: {len(sg_events)} events")

    nps_events = fetch_nps_events(now, end)
    events.extend(nps_events)
    print(f"  NPS (parks/outdoor): {len(nps_events)} events")

    if not events:
        print("\nNo events found — check your API keys. Exiting.")
        sys.exit(1)

    # --- Aggregate + deduplicate ---
    events = aggregate_events(events)
    print(f"\n  After dedup: {len(events)} unique events")

    # --- Score and rank ---
    ranked = score_and_sort(events)
    top = ranked[: config.MAX_EVENTS]
    print(f"  Sending top {len(top)} events")

    # --- Build email ---
    html = build_email(top, now, end)

    # --- Send ---
    subject = f"Fun Things This Week — {now.strftime('%B %-d')} in DC/MD/VA"
    send_email(subject, html)
    print(f"\n  Email sent to {config.RECIPIENT_EMAIL}")


if __name__ == "__main__":
    main()
