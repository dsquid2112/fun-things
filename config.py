import os

# --- API Keys (set as GitHub Secrets, or in a local .env for testing) ---
TICKETMASTER_KEY = os.getenv("TICKETMASTER_API_KEY", "")
NPS_KEY = os.getenv("NPS_API_KEY", "")

# --- Email ---
GMAIL_USER = os.getenv("GMAIL_USER", "dan.squillaro@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "dan.squillaro@gmail.com")

# --- Voting ---
# GitHub info for the vote page to trigger the record-vote workflow
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")        # Your GitHub username
GITHUB_REPO = os.getenv("GITHUB_REPO", "fun-things")
GITHUB_VOTE_TOKEN = os.getenv("GITHUB_VOTE_TOKEN", "")  # Fine-grained PAT (actions:write only)

# Vote page URL (GitHub Pages) — used to build links in the email
VOTE_PAGE_URL = f"https://dsquid2112.github.io/fun-things/vote/" if GITHUB_OWNER else ""

# --- Family ---
FAMILY = [
    {"name": "Dan", "age": 53},
    {"name": "Wife", "age": 57},
    {"name": "Son", "age": 17},
    {"name": "Daughter", "age": 13},
]

# --- Search area (DC center, 50-mile radius) ---
CENTER_LAT = 38.9072
CENTER_LON = -77.0369
RADIUS_MILES = 50

# --- NPS parks in DMV area ---
NPS_PARK_CODES = "rocr,nace,gwmp,nama,mana,anti,hafe,choh,prwi"

# --- How many events to include in the digest ---
MAX_EVENTS = 15

# --- Lookahead window (days) ---
LOOKAHEAD_DAYS = 14
