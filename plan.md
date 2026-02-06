# João Almeida Results → Telegram Bot

## Project Plan & Full Specification

---

## 1. Objective
Create a **100% free** automated system that sends a **Telegram notification** whenever a race in which **João Almeida** participates **finishes**, including:
- Final **General Classification (GC) position** for stage races
- Final **result position** for **one-day races**

No paid APIs, no paid hosting, no manual intervention.

---

## 2. Technology Constraints

- ✅ Free APIs only
- ✅ Free hosting only
- ✅ No always-on server
- ✅ Fully automated

---

## 3. High-Level Architecture

```
GitHub Actions (cron)
        │
        ▼
Python Scraper (PCS)
        │
        ▼
Race Classification Logic
        │
        ▼
Telegram Bot API
        │
        ▼
Telegram Chat
```

---

## 4. Data Source

### Primary Source
**ProCyclingStats (PCS)** – HTML scraping

Rider page:
```
https://www.procyclingstats.com/rider/joao-almeida
```

Race page:
```
https://www.procyclingstats.com/race/<race-name>/<year>
```

---

## 5. Scraping Selectors (Exact)

### 5.1 Rider Page

| Data | Selector |
|----|---------|
| Results table | `table.results` |
| Result rows | `table.results tbody tr` |
| Race link | `td:nth-child(3) a[href]` |
| Position | `td:nth-child(4)` |

---

### 5.2 Stage Race – General Classification

Detected by presence of:
```
table.results.gc
```

Selectors:

| Data | Selector |
|----|---------|
| GC rows | `table.results.gc tbody tr` |
| João Almeida row | `tr:has(a[href*="/rider/joao-almeida"])` |
| GC position | `td.pos` |
| Time gap | `td.time` |
| Team | `td.team a` |

A race is **finished** when the GC table exists.

---

### 5.3 One-Day Race Support (NEW)

One-day races **do not have a GC table**.

#### Detection Logic
A race is classified as **one-day** when:
- `table.results.gc` ❌ does NOT exist
- `table.results` (final result table) ✅ exists

#### Result Extraction

Selectors:

| Data | Selector |
|----|---------|
| Result table | `table.results` |
| João Almeida row | `tr:has(a[href*="/rider/joao-almeida"])` |
| Final position | `td.pos` |
| Time gap | `td.time` |
| Team | `td.team a` |

#### Finished Race Rule (One-Day)

A one-day race is considered finished when:
- João Almeida appears in the main results table
- Position is numeric or `DNF`

---

## 6. Unified Race Classification Algorithm

```
For each race:

if GC table exists:
    race_type = "stage_race"
    result = GC position
elif results table exists:
    race_type = "one_day_race"
    result = final position
else:
    race not finished
```

Only **one notification per race** is allowed.

---

## 7. Telegram Message Format

### Stage Race
```
🏁 Race finished!

🚴 João Almeida
📍 Race: Volta a la Comunitat Valenciana
📊 GC Position: 2º
⏱ +14s
👕 UAE Team Emirates
```

### One-Day Race
```
🏁 Race finished!

🚴 João Almeida
📍 Race: Il Lombardia
📊 Final Position: 6º
⏱ +1:02
👕 UAE Team Emirates
```

---

## 8. State Management

Stored in `storage.json`:

```json
{
  "race_id": {
    "year": 2026,
    "type": "one_day",
    "notified": true
  }
}
```

Prevents duplicate notifications.

---

## 9. Execution Model (GitHub Actions)

- Runs every **2 hours** via cron
- Manual trigger allowed
- Stateless execution + state committed back to repo

---

## 10. GitHub Actions Workflow

`.github/workflows/scheduler.yml`

```yaml
name: João Almeida Results Bot

on:
  schedule:
    - cron: "0 */2 * * *"
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pip install -r requirements.txt

      - run: python bot.py
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}

      - name: Commit state
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add storage.json
          git commit -m "Update race state" || echo "No changes"
          git push
```

---

## 11. Project Structure

```
joao-almeida-telegram-bot/
├── bot.py
├── scraper.py
├── notifier.py
├── storage.json
├── requirements.txt
├── plan.md
└── .github/workflows/scheduler.yml
```

---

## 12. Development Phases

1. Implement scraper
2. Implement race classification logic
3. Telegram notifier
4. GitHub Actions deployment
5. Validation during live races

---

## 13. Success Criteria

- ✅ Works for stage races and one-day races
- ✅ No duplicate messages
- ✅ Zero cost
- ✅ Fully automated

---

## 14. Future Extensions (Still Free)

- Multiple riders
- Daily race summaries
- Top-10 highlights
- Telegram inline buttons

---

## 15. Final Notes

This design intentionally avoids:
- Paid APIs
- Long-running servers
- Fragile stage-detection heuristics

It is reliable, cheap, and easy to extend.

