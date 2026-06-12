import requests
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone

API_KEY = "123"
LEAGUE_ID = "4429"
SEASON = "2026"
ICS_FILE = "worldcup2026_schedule.ics"

COUNTRY_CODES = {
    "Argentina": "AR", "Australia": "AU", "Belgium": "BE", "Brazil": "BR",
    "Canada": "CA", "Czech Republic": "CZ", "Czechia": "CZ",
    "France": "FR", "Germany": "DE", "Japan": "JP", "Mexico": "MX",
    "Morocco": "MA", "Netherlands": "NL", "Paraguay": "PY",
    "Portugal": "PT", "Qatar": "QA", "South Africa": "ZA",
    "South Korea": "KR", "Korea Republic": "KR", "Spain": "ES",
    "Switzerland": "CH", "Turkey": "TR", "USA": "US",
    "United States": "US", "Bosnia-Herzegovina": "BA",
    "Haiti": "HT", "Scotland": "GB", "Ivory Coast": "CI",
    "Ecuador": "EC", "Sweden": "SE", "Tunisia": "TN",
    "Curaçao": "CW", "Egypt": "EG", "Iran": "IR",
    "Jordan": "JO"
}

def flag(name):
    code = COUNTRY_CODES.get(name)
    if not code:
        return ""
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

def team_name(name):
    if not name:
        return "TBD"
    return f"{flag(name)} {name}".strip()

def fetch_matches():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsseason.php"
    params = {
        "id": LEAGUE_ID,
        "s": SEASON
    }

    r = requests.get(url, params=params)
    print("STATUS:", r.status_code)
    print("URL:", r.url)
    r.raise_for_status()

    data = r.json()
    return data.get("events") or []

def parse_time(event):
    date_str = event.get("dateEvent")
    time_str = event.get("strTime") or "00:00:00"

    if not date_str:
        return None

    time_str = time_str.replace("+00:00", "").replace("Z", "")

    try:
        dt = datetime.fromisoformat(f"{date_str}T{time_str}")
    except ValueError:
        dt = datetime.strptime(f"{date_str} {time_str[:8]}", "%Y-%m-%d %H:%M:%S")

    return dt.replace(tzinfo=timezone.utc)

def score_text(event):
    hs = event.get("intHomeScore")
    aw = event.get("intAwayScore")

    if hs is None or aw is None or hs == "" or aw == "":
        return None

    return f"{hs}-{aw}"

def event_title(event):
    home_raw = event.get("strHomeTeam")
    away_raw = event.get("strAwayTeam")

    home = team_name(home_raw)
    away = team_name(away_raw)
    score = score_text(event)

    if score:
        return f"{home} {score} {away}"

    return f"{home} vs {away}"

def event_location(event):
    venue = event.get("strVenue") or ""
    country = event.get("strCountry") or ""
    city = event.get("strCity") or ""

    parts = [p for p in [venue, city, country] if p]
    return " | ".join(parts)

def event_description(event):
    lines = []

    status = "Finished" if score_text(event) else "Scheduled"
    lines.append(f"Status: {status}")

    venue = event.get("strVenue")
    city = event.get("strCity")
    country = event.get("strCountry")

    if venue:
        lines.append(f"Venue: {venue}")
    if city:
        lines.append(f"City: {city}")
    if country:
        lines.append(f"Country: {country}")

    round_name = event.get("intRound") or event.get("strRound")
    if round_name:
        lines.append(f"Round: {round_name}")

    return "\n".join(lines)

def create_calendar(matches):
    cal = Calendar()

    for m in matches:
        start = parse_time(m)
        if not start:
            continue

        e = Event()
        e.name = event_title(m)
        e.begin = start
        e.end = start + timedelta(hours=2)
        e.location = event_location(m)
        e.description = event_description(m)

        event_id = m.get("idEvent")
        if event_id:
            e.uid = f"worldcup2026-{event_id}@github"

        cal.events.add(e)

    return cal

def main():
    matches = fetch_matches()

    print("TOTAL MATCHES:", len(matches))

    cal = create_calendar(matches)

    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)

if __name__ == "__main__":
    main()
