import requests
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone

API_KEY = "123"
LEAGUE_ID = "4429"
SEASON = "2026"
ICS_FILE = "worldcup2026_schedule.ics"


# =========================================================
# 🔥 48队封闭世界模型（核心稳定层）
# =========================================================
TEAM_DB = {
    "mexico": {"cn": "墨西哥", "code": "MX", "emoji": "🇲🇽"},
    "south africa": {"cn": "南非", "code": "RSA", "emoji": "🇿🇦"},
    "korea republic": {"cn": "韩国", "code": "KOR", "emoji": "🇰🇷"},
    "south korea": {"cn": "韩国", "code": "KOR", "emoji": "🇰🇷"},
    "czechia": {"cn": "捷克", "code": "CZE", "emoji": "🇨🇿"},
    "czech republic": {"cn": "捷克", "code": "CZE", "emoji": "🇨🇿"},

    "canada": {"cn": "加拿大", "code": "CAN", "emoji": "🇨🇦"},
    "bosnia and herzegovina": {"cn": "波黑", "code": "BIH", "emoji": "🇧🇦"},
    "bosnia-herzegovina": {"cn": "波黑", "code": "BIH", "emoji": "🇧🇦"},
    "qatar": {"cn": "卡塔尔", "code": "QAT", "emoji": "🇶🇦"},
    "switzerland": {"cn": "瑞士", "code": "SUI", "emoji": "🇨🇭"},

    "brazil": {"cn": "巴西", "code": "BRA", "emoji": "🇧🇷"},
    "morocco": {"cn": "摩洛哥", "code": "MAR", "emoji": "🇲🇦"},
    "haiti": {"cn": "海地", "code": "HTI", "emoji": "🇭🇹"},
    "scotland": {"cn": "苏格兰", "code": "SCO", "emoji": "🏴"},

    "united states": {"cn": "美国", "code": "USA", "emoji": "🇺🇸"},
    "usa": {"cn": "美国", "code": "USA", "emoji": "🇺🇸"},
    "paraguay": {"cn": "巴拉圭", "code": "PAR", "emoji": "🇵🇾"},
    "australia": {"cn": "澳大利亚", "code": "AUS", "emoji": "🇦🇺"},
    "turkey": {"cn": "土耳其", "code": "TUR", "emoji": "🇹🇷"},

    "germany": {"cn": "德国", "code": "GER", "emoji": "🇩🇪"},
    "curacao": {"cn": "库拉索", "code": "CUW", "emoji": "🇨🇼"},
    "cote d'ivoire": {"cn": "科特迪瓦", "code": "CIV", "emoji": "🇨🇮"},
    "côte d’ivoire": {"cn": "科特迪瓦", "code": "CIV", "emoji": "🇨🇮"},
    "ecuador": {"cn": "厄瓜多尔", "code": "ECU", "emoji": "🇪🇨"},

    "netherlands": {"cn": "荷兰", "code": "NED", "emoji": "🇳🇱"},
    "japan": {"cn": "日本", "code": "JPN", "emoji": "🇯🇵"},
    "sweden": {"cn": "瑞典", "code": "SWE", "emoji": "🇸🇪"},
    "tunisia": {"cn": "突尼斯", "code": "TUN", "emoji": "🇹🇳"},

    "belgium": {"cn": "比利时", "code": "BEL", "emoji": "🇧🇪"},
    "egypt": {"cn": "埃及", "code": "EGY", "emoji": "🇪🇬"},
    "iran": {"cn": "伊朗", "code": "IRN", "emoji": "🇮🇷"},
    "new zealand": {"cn": "新西兰", "code": "NZL", "emoji": "🇳🇿"},

    "spain": {"cn": "西班牙", "code": "ESP", "emoji": "🇪🇸"},
    "cape verde": {"cn": "佛得角", "code": "CPV", "emoji": "🇨🇻"},
    "saudi arabia": {"cn": "沙特阿拉伯", "code": "KSA", "emoji": "🇸🇦"},
    "uruguay": {"cn": "乌拉圭", "code": "URU", "emoji": "🇺🇾"},

    "france": {"cn": "法国", "code": "FRA", "emoji": "🇫🇷"},
    "senegal": {"cn": "塞内加尔", "code": "SEN", "emoji": "🇸🇳"},
    "iraq": {"cn": "伊拉克", "code": "IRQ", "emoji": "🇮🇶"},
    "norway": {"cn": "挪威", "code": "NOR", "emoji": "🇳🇴"},

    "argentina": {"cn": "阿根廷", "code": "ARG", "emoji": "🇦🇷"},
    "algeria": {"cn": "阿尔及利亚", "code": "DZA", "emoji": "🇩🇿"},
    "austria": {"cn": "奥地利", "code": "AUT", "emoji": "🇦🇹"},
    "jordan": {"cn": "约旦", "code": "JOR", "emoji": "🇯🇴"},

    "portugal": {"cn": "葡萄牙", "code": "POR", "emoji": "🇵🇹"},
    "dr congo": {"cn": "刚果（金）", "code": "COD", "emoji": "🇨🇩"},
    "uzbekistan": {"cn": "乌兹别克斯坦", "code": "UZB", "emoji": "🇺🇿"},
    "colombia": {"cn": "哥伦比亚", "code": "COL", "emoji": "🇨🇴"},

    "england": {"cn": "英格兰", "code": "ENG", "emoji": "🏴"},
    "croatia": {"cn": "克罗地亚", "code": "CRO", "emoji": "🇭🇷"},
    "ghana": {"cn": "加纳", "code": "GHA", "emoji": "🇬🇭"},
    "panama": {"cn": "巴拿马", "code": "PAN", "emoji": "🇵🇦"},
}


# =========================================================
# normalize（关键稳定层）
# =========================================================
def norm(name):
    if not name:
        return ""
    return name.strip().lower()


def team(name):
    n = norm(name)
    if n in TEAM_DB:
        t = TEAM_DB[n]
        return f"{t['emoji']} {t['cn']}"
    return f"🏳️ {name}"


# =========================================================
# 状态（严格 API 驱动）
# =========================================================
def status(e):
    s = (e.get("strStatus") or "").upper()

    if s == "FT":
        return "FT"
    if s in ["1H", "2H", "LIVE", "IN PLAY"]:
        return "LIVE"
    return "NS"


# =========================================================
# 比分
# =========================================================
def score(e):
    h = e.get("intHomeScore")
    a = e.get("intAwayScore")
    if h is None or a is None:
        return None
    return f"{h}-{a}"


# =========================================================
# 标题（最终规则）
# =========================================================
def title(e):
    home = team(e.get("strHomeTeam"))
    away = team(e.get("strAwayTeam"))
    sc = score(e)

    base = f"{home} vs {away}"
    if sc:
        base = f"{home} {sc} {away}"

    if status(e) == "LIVE":
        return "▶️ 比赛中\n" + base

    return base


# =========================================================
# 时间
# =========================================================
def parse_time(e):
    if not e.get("dateEvent"):
        return None
    t = (e.get("strTime") or "00:00:00")[:8]
    dt = datetime.strptime(f"{e['dateEvent']} {t}", "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=timezone.utc)


# =========================================================
# API（单源原则！！！）
# =========================================================
def fetch():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsseason.php"
    r = requests.get(url, params={"id": LEAGUE_ID, "s": SEASON})
    return r.json().get("events") or []


# =========================================================
# ICS
# =========================================================
def build(events):
    cal = Calendar()

    for e in events:
        start = parse_time(e)
        if not start:
            continue

        ev = Event()
        ev.name = title(e)
        ev.begin = start
        ev.end = start + timedelta(hours=2)

        ev.location = f"{e.get('strCountry','')} · {e.get('strCity','')} · {e.get('strVenue','')}"

        if e.get("idEvent"):
            ev.uid = f"wc2026-{e['idEvent']}"

        cal.events.add(ev)

    return cal


def main():
    events = fetch()
    print("TOTAL:", len(events))

    cal = build(events)

    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)


if __name__ == "__main__":
    main()
