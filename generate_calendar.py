import requests
from ics import Calendar, Event
from datetime import datetime, timedelta

TOKEN = "a5507e9b27da40b9a0f49744f268d163"

ICS_FILE = "worldcup2026_schedule.ics"


def fetch_matches():
    url = "https://api.football-data.org/v4/matches"

    headers = {
        "X-Auth-Token": TOKEN
    }

    params = {
        "competitions": "WC",
        "dateFrom": "2026-06-12",
        "dateTo": "2026-07-20"
    }

    r = requests.get(url, headers=headers, params=params)

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()

    return r.json()["matches"]


def create_calendar(matches):
    cal = Calendar()

    for m in matches:
        e = Event()

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        utc = datetime.fromisoformat(
            m["utcDate"].replace("Z", "+00:00")
        )

        start = utc + timedelta(hours=8)

        e.name = f"{home} vs {away}"
        e.begin = start

        cal.events.add(e)

    return cal


def main():
    matches = fetch_matches()

    cal = create_calendar(matches)

    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)


if __name__ == "__main__":
    main()
