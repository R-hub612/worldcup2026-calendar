import requests
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone

API_KEY = "123"  # 替换成你的TheSportsDB API Key
LEAGUE_ID = "4429"
SEASON = "2026"
ICS_FILE = "worldcup2026_schedule.ics"

COUNTRIES = {
    "Mexico": ("墨西哥", "MX"), "South Africa": ("南非", "ZA"),
    "South Korea": ("韩国", "KR"), "Korea Republic": ("韩国", "KR"),
    "Czech Republic": ("捷克", "CZ"), "Czechia": ("捷克", "CZ"),
    "Canada": ("加拿大", "CA"), "Bosnia-Herzegovina": ("波黑", "BA"),
    "Bosnia and Herzegovina": ("波黑", "BA"),
    "United States": ("美国", "US"), "USA": ("美国", "US"),
    "Paraguay": ("巴拉圭", "PY"), "Qatar": ("卡塔尔", "QA"),
    "Switzerland": ("瑞士", "CH"), "Brazil": ("巴西", "BR"),
    "Morocco": ("摩洛哥", "MA"), "Haiti": ("海地", "HT"),
    "Scotland": ("苏格兰", "GB"), "Australia": ("澳大利亚", "AU"),
    "Turkey": ("土耳其", "TR"), "Germany": ("德国", "DE"),
    "Curaçao": ("库拉索", "CW"), "Curacao": ("库拉索", "CW"),
    "Netherlands": ("荷兰", "NL"), "Japan": ("日本", "JP"),
    "Ivory Coast": ("科特迪瓦", "CI"), "Côte d’Ivoire": ("科特迪瓦", "CI"),
    "Ecuador": ("厄瓜多尔", "EC"), "Portugal": ("葡萄牙", "PT"),
    "DR Congo": ("刚果（金）", "CD"), "Congo DR": ("刚果（金）", "CD"),
    "England": ("英格兰", "GB"), "Croatia": ("克罗地亚", "HR"),
    "Ghana": ("加纳", "GH"), "Panama": ("巴拿马", "PA"),
    "Argentina": ("阿根廷", "AR"), "France": ("法国", "FR"),
    "Spain": ("西班牙", "ES"), "Belgium": ("比利时", "BE"),
    "Uruguay": ("乌拉圭", "UY"), "Colombia": ("哥伦比亚", "CO"),
    "Egypt": ("埃及", "EG"), "Iran": ("伊朗", "IR"),
    "Jordan": ("约旦", "JO"), "Tunisia": ("突尼斯", "TN"),
    "Sweden": ("瑞典", "SE"), "Norway": ("挪威", "NO"),
    "Poland": ("波兰", "PL"), "Serbia": ("塞尔维亚", "RS"),
    "Denmark": ("丹麦", "DK"), "Senegal": ("塞内加尔", "SN"),
    "Nigeria": ("尼日利亚", "NG"), "Cameroon": ("喀麦隆", "CM"),
    "Saudi Arabia": ("沙特", "SA"), "New Zealand": ("新西兰", "NZ"),
}

CITIES = {
    "Los Angeles": "洛杉矶", "Inglewood": "洛杉矶",
    "New York": "纽约", "East Rutherford": "纽约",
    "Dallas": "达拉斯", "Arlington": "达拉斯",
    "Houston": "休斯敦", "Kansas City": "堪萨斯城",
    "Miami": "迈阿密", "Atlanta": "亚特兰大",
    "Philadelphia": "费城", "Boston": "波士顿", "Foxborough": "波士顿",
    "Seattle": "西雅图", "San Francisco": "旧金山",
    "Santa Clara": "旧金山",
    "Toronto": "多伦多", "Vancouver": "温哥华",
    "Mexico City": "墨西哥城", "Guadalajara": "瓜达拉哈拉",
    "Monterrey": "蒙特雷",
}

HOST_COUNTRIES = {
    "United States": "美国", "USA": "美国",
    "Canada": "加拿大", "Mexico": "墨西哥",
}

def emoji(code):
    if not code or len(code) < 2:
        return ""
    code = code[:2].upper()
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

def team_cn(name):
    if not name:
        return "待定"
    cn, code = COUNTRIES.get(name, (name, ""))
    flag = emoji(code)
    return f"{flag} {cn}".strip()

def stage_text(event):
    group = event.get("strGroup") or event.get("strGroupName")
    if group:
        mapping = {
            "Group A": "A组", "Group B": "B组", "Group C": "C组", "Group D": "D组",
            "Group E": "E组", "Group F": "F组", "Group G": "G组", "Group H": "H组",
            "Group I": "I组", "Group J": "J组", "Group K": "K组", "Group L": "L组",
        }
        return mapping.get(group, group)

    stage = event.get("strStage") or ""
    mapping = {
        "Round of 16": "16强", "Quarter-finals": "8强",
        "Semi-finals": "半决赛", "Final": "决赛",
        "Third-place play-off": "三四名决赛",
    }
    return mapping.get(stage, stage)

def score(event):
    hs = event.get("intHomeScore")
    aw = event.get("intAwayScore")
    if hs in [None, ""] or aw in [None, ""]:
        return None
    return f"{hs}-{aw}"

def is_live(event):
    start = parse_time(event)
    if not start:
        return False
    now = datetime.now(timezone.utc)
    elapsed = (now - start).total_seconds()
    return 0 <= elapsed <= 7200

def title(event):
    home = team_cn(event.get("strHomeTeam"))
    away = team_cn(event.get("strAwayTeam"))
    s = score(event)
    stage = stage_text(event)

    if s:
        line = f"{home} {s} {away}"
    else:
        line = f"{home} vs {away}"

    if stage:
        line += f"｜{stage}"

    if is_live(event):
        return f"比赛中\n{line}"

    return line

def location(event):
    venue = event.get("strVenue") or ""
    city_raw = event.get("strCity") or ""
    country_raw = event.get("strCountry") or ""
    city_cn = CITIES.get(city_raw, city_raw)
    country_cn = HOST_COUNTRIES.get(country_raw, country_raw)
    prefix = f"{country_cn}{city_cn}".strip()
    if prefix and venue:
        return f"{prefix} · {venue}"
    if venue:
        return venue
    return prefix

def parse_time(event):
    date_str = event.get("dateEvent")
    time_str = event.get("strTime") or "00:00:00"
    if not date_str:
        return None
    time_str = time_str.replace("Z", "").replace("+00:00", "")[:8]
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=timezone.utc)

def fetch_matches():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsseason.php"
    params = {"id": LEAGUE_ID, "s": SEASON}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("events") or []

def create_calendar(matches):
    cal = Calendar()
    for m in matches:
        start = parse_time(m)
        if not start:
            continue
        e = Event()
        e.name = title(m)
        e.begin = start
        e.end = start + timedelta(hours=2)
        e.location = location(m)
        e.description = location(m)
        event_id = m.get("idEvent")
        if event_id:
            e.uid = f"worldcup2026-{event_id}@github"
        cal.events.add(e)
    return cal

def main():
    matches = fetch_matches()
    cal = create_calendar(matches)
    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)

if __name__ == "__main__":
    main()
