import requests
from ics import Calendar, Event
from datetime import datetime, timedelta

# 你的 football-data.org token
TOKEN = "a5507e9b27da40b9a0f49744f268d163"
ICS_FILE = "2026世界杯赛程_中文北京时间_iPhone_iPad.ics"

def fetch_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": TOKEN}
    params = {
        "competitions": "WC",
        "dateFrom": "2026-06-12",
        "dateTo": "2026-07-20"
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()["matches"]

def create_calendar(matches):
    cal = Calendar()
    for m in matches:
        e = Event()
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        utc = datetime.fromisoformat(m["utcDate"].replace("Z","+00:00"))

        # 北京时间 UTC+8
        start = utc + timedelta(hours=8)
        e.begin = start
        e.end = start + timedelta(hours=2)

        # 比分显示
        if m["status"] == "FINISHED":
            score = f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"
            e.name = f"{home} {score} vs {away}｜{m['group']}"
        else:
            e.name = f"{home} vs {away}｜{m['group']}"

        cal.events.add(e)
    return cal

def main():
    matches = fetch_matches()
    cal = create_calendar(matches)
    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)

if __name__ == "__main__":
    main()
