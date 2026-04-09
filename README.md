# Fun Things

Weekly event digest for the DMV area — delivered to your inbox every Sunday.
Pulls from Ticketmaster and the National Park Service, scores events based on
your family's upvotes/downvotes, and learns your preferences over time.

---

## One-Time Setup (~15 minutes)

### 1. Get API Keys

**Ticketmaster (free)**
1. Go to https://developer.ticketmaster.com/
2. Click **Get Your API Key** → create a free account
3. Copy your **Consumer Key**

**National Park Service (free)**
1. Go to https://www.nps.gov/subjects/developer/get-started.htm
2. Fill out the short form → you get the key instantly via email

**Gmail App Password**
1. Go to your Google Account → Security → 2-Step Verification (must be ON)
2. At the bottom, click **App passwords**
3. Select app: **Mail** → device: **Other** → name it "Fun Things"
4. Copy the 16-character password

---

### 2. Create the GitHub Repo

```bash
# In Terminal, from your Documents folder:
cd ~/Documents/fun-things
git init
git add .
git commit -m "Initial commit"
```

Then:
1. Go to https://github.com/new
2. Name it `fun-things` (keep it **Private** — your vote token will live here)
3. Don't initialize with README (you already have one)
4. Follow GitHub's instructions to push your existing repo

---

### 3. Add GitHub Secrets

In your repo on GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Add these 5 secrets:

| Name | Value |
|------|-------|
| `TICKETMASTER_API_KEY` | Your Ticketmaster Consumer Key |
| `NPS_API_KEY` | Your NPS API key |
| `GMAIL_USER` | `dan.squillaro@gmail.com` |
| `GMAIL_APP_PASSWORD` | The 16-character Gmail app password |
| `RECIPIENT_EMAIL` | `dan.squillaro@gmail.com` |

---

### 4. Enable GitHub Pages (for the vote page)

1. In your repo: **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/vote`
4. Click **Save**

GitHub will give you a URL like `https://YOUR_USERNAME.github.io/fun-things/vote/`

---

### 5. Create a Vote Token

This lets the vote page record your clicks back to the repo.

1. Go to https://github.com/settings/personal-access-tokens/new
2. Name: `fun-things-vote`
3. Expiration: 1 year
4. Repository access: **Only select repositories** → `fun-things`
5. Permissions: **Actions** → Read and write
6. Click **Generate token** → copy it

Then open `vote/index.html` and replace:
```
const GITHUB_OWNER = "YOUR_GITHUB_USERNAME";
const GITHUB_TOKEN = "YOUR_VOTE_TOKEN_HERE";
```

Commit and push the change.

---

### 6. Test It

Go to your repo on GitHub → **Actions → Weekly Fun Things Digest → Run workflow**

You should get an email within ~30 seconds!

---

## How It Works

```
Every Sunday 8 AM
       │
       ▼
GitHub Actions runs main.py
       │
       ├── Ticketmaster API  ─┐
       └── NPS API           ─┴─► aggregate + deduplicate
                                          │
                                    score & rank
                                    (votes.json + preferences.json)
                                          │
                                   build HTML email
                                          │
                                  send via Gmail SMTP
                                          │
                                    📬 Your inbox

When you click "Love it" or "Pass":
  Email link → GitHub Pages vote page → GitHub API
  → record-vote workflow → appends to data/votes.json
  → next Sunday's scores are smarter
```

---

## Customizing

**Change the schedule:** Edit `.github/workflows/weekly-digest.yml`, the `cron` line.
Format: `"minute hour * * day"` (day 0=Sunday). All times are UTC (subtract 4-5h for Eastern).

**Adjust category weights:** Edit `data/preferences.json`.
Higher number = shown more often. Negative = suppressed.

**Add family members:** Edit `FAMILY` in `config.py` and add their emails to `RECIPIENT_EMAIL`
(comma-separated — update `sender.py` to split and send to multiple addresses).

**Expand search radius:** Change `RADIUS_MILES` in `config.py`.
