# skytech

> Flight search platform: scrapes LATAM Airlines availability and serves it through a Flask web app with a SQLite database.

University project — runs locally only.

## What it does

- **Scraper** (`skytech/scraper.py`) — Selenium-based scraper that queries LATAM's website for round-trip flights between Peruvian cities (Arequipa, Lima, Cusco, etc.). Outputs JSON into `data/`.
- **Web app** (`skytech/database/app.py`) — Flask + Flask-RESTful + SQLAlchemy. Stores flights, users, and saved searches in SQLite. Serves Jinja templates: login, search, results.
- **Driver** (`skytech/run.py`) — orchestrates a scrape and POSTs results into the running web app.

## Stack

Python 3.8+ · Flask 1.1 · Flask-SQLAlchemy · SQLite · Selenium 4 · ChromeDriver

## Local setup

Selenium requires a Chrome/Chromium browser installed and a matching `chromedriver` on PATH.

```bash
git clone https://github.com/RayverAimar/skytech.git
cd skytech

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Run

Two processes — start the web app first, then the scraper.

**Terminal 1 — Flask app** (serves on `http://127.0.0.1:5000`):

```bash
cd skytech/database
python app.py
```

**Terminal 2 — scraper + ingest**:

```bash
cd skytech
python run.py
```

`run.py` scrapes Arequipa → Lima for the dates hardcoded inside the file, saves a JSON snapshot in `data/`, and POSTs each flight to `/flight/<id>` on the running Flask app.

## Project layout

```
skytech/
  scraper.py        # LatamScraper — Selenium driver
  run.py            # entry point: scrape + push to API
  config.py         # selenium timeouts
  definitions.py    # city → IATA code map
  utils.py          # shared helpers
  database/
    app.py          # Flask app + REST API + ORM models
    get.py          # query helpers
    templates/      # Jinja templates (login, search, results)
    static/         # CSS, images
```

## Notes

- The committed `database/database.db` is a sample SQLite file from development. Delete it for a clean run — the app will recreate it.
- Flight dates in `run.py` are hardcoded; edit the file to query different routes/dates.
- LATAM's HTML changes periodically — scraper selectors may need updates over time.

## Status

Coursework / archived. Not actively maintained.

## License

MIT
