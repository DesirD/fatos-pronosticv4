"""
Fatos Pronostic — Moteur NBA / NHL / AHL
"""
import requests
import math
from datetime import datetime

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"

# ─── NBA ──────────────────────────────────────────────────────────────────────
NBA_LEAGUES = [
    {"id": "basketball_nba",         "label": "🏀 NBA",                  "group": "NBA"},
    {"id": "basketball_nba_preseason","label": "🏀 NBA Pré-saison",       "group": "NBA"},
    {"id": "basketball_ncaab",        "label": "🏀 NCAA Basketball",      "group": "NCAA"},
]

# Pace / offensive rating par équipe (points marqués pour 100 possessions)
NBA_TEAM_STATS = {
    "Boston Celtics":        {"off": 119.8, "def": 108.1, "pace": 99.2, "home_adv": 3.2},
    "Oklahoma City Thunder": {"off": 118.5, "def": 107.2, "pace": 100.1,"home_adv": 3.5},
    "Cleveland Cavaliers":   {"off": 117.2, "def": 107.8, "pace": 97.8, "home_adv": 3.1},
    "Denver Nuggets":        {"off": 118.0, "def": 110.5, "pace": 96.5, "home_adv": 4.0},
    "Minnesota Timberwolves":{"off": 113.2, "def": 107.5, "pace": 97.0, "home_adv": 3.0},
    "New York Knicks":       {"off": 114.5, "def": 109.8, "pace": 95.5, "home_adv": 3.5},
    "Indiana Pacers":        {"off": 121.5, "def": 115.2, "pace": 103.8,"home_adv": 2.8},
    "Memphis Grizzlies":     {"off": 112.8, "def": 110.5, "pace": 98.5, "home_adv": 3.0},
    "LA Clippers":           {"off": 115.5, "def": 111.2, "pace": 97.5, "home_adv": 2.5},
    "Orlando Magic":         {"off": 109.8, "def": 108.5, "pace": 96.0, "home_adv": 3.0},
    "Miami Heat":            {"off": 112.5, "def": 109.5, "pace": 95.8, "home_adv": 3.2},
    "Milwaukee Bucks":       {"off": 116.8, "def": 111.8, "pace": 99.5, "home_adv": 3.3},
    "Phoenix Suns":          {"off": 113.5, "def": 112.5, "pace": 97.2, "home_adv": 3.0},
    "Golden State Warriors": {"off": 115.8, "def": 113.5, "pace": 99.8, "home_adv": 3.8},
    "Los Angeles Lakers":    {"off": 116.2, "def": 113.0, "pace": 100.2,"home_adv": 3.5},
    "Dallas Mavericks":      {"off": 117.5, "def": 110.8, "pace": 97.0, "home_adv": 3.2},
    "Sacramento Kings":      {"off": 116.5, "def": 115.5, "pace": 101.5,"home_adv": 3.0},
    "Philadelphia 76ers":    {"off": 114.2, "def": 113.2, "pace": 97.5, "home_adv": 3.2},
    "Chicago Bulls":         {"off": 111.5, "def": 113.5, "pace": 97.8, "home_adv": 2.8},
    "Atlanta Hawks":         {"off": 115.8, "def": 116.2, "pace": 100.5,"home_adv": 2.5},
    "Toronto Raptors":       {"off": 107.5, "def": 115.8, "pace": 97.2, "home_adv": 3.0},
    "Houston Rockets":       {"off": 114.5, "def": 112.5, "pace": 99.5, "home_adv": 3.0},
    "Utah Jazz":             {"off": 110.5, "def": 116.8, "pace": 98.8, "home_adv": 2.8},
    "Detroit Pistons":       {"off": 109.5, "def": 117.5, "pace": 99.2, "home_adv": 2.5},
    "San Antonio Spurs":     {"off": 109.2, "def": 118.5, "pace": 98.5, "home_adv": 2.5},
    "Charlotte Hornets":     {"off": 108.5, "def": 118.8, "pace": 100.2,"home_adv": 2.5},
    "Washington Wizards":    {"off": 108.8, "def": 119.5, "pace": 99.8, "home_adv": 2.5},
    "New Orleans Pelicans":  {"off": 111.5, "def": 111.0, "pace": 98.0, "home_adv": 2.8},
    "Portland Trail Blazers":{"off": 110.5, "def": 116.5, "pace": 99.5, "home_adv": 2.8},
    "Brooklyn Nets":         {"off": 108.2, "def": 119.2, "pace": 100.5,"home_adv": 2.5},
}
NBA_DEFAULT = {"off": 113.0, "def": 113.0, "pace": 98.5, "home_adv": 3.0}
NBA_LEAGUE_AVG_OFF = 113.0

def get_nba_team(name):
    if name in NBA_TEAM_STATS:
        return NBA_TEAM_STATS[name]
    nl = name.lower()
    for k, v in NBA_TEAM_STATS.items():
        if any(w in nl for w in k.lower().split() if len(w) > 4):
            return v
    return NBA_DEFAULT.copy()

def compute_nba(home, away, home_odds=None, away_odds=None):
    hs = get_nba_team(home)
    as_ = get_nba_team(away)
    # Expected points using adjusted efficiency
    pace = (hs["pace"] + as_["pace"]) / 2
    home_pts = round((hs["off"] * as_["def"] / NBA_LEAGUE_AVG_OFF) * (pace / 98.5) + hs["home_adv"], 1)
    away_pts = round((as_["off"] * hs["def"] / NBA_LEAGUE_AVG_OFF) * (pace / 98.5), 1)
    total_pts = round(home_pts + away_pts, 1)

    # Win probability via logistic model
    margin = home_pts - away_pts
    p_home = round(1 / (1 + math.exp(-margin / 7)) * 100, 1)
    p_away = round(100 - p_home, 1)

    # Blend with market odds if available
    if home_odds and away_odds:
        ip_h = 1 / home_odds
        ip_a = 1 / away_odds
        s = ip_h + ip_a
        ip_h, ip_a = ip_h/s*100, ip_a/s*100
        p_home = round(p_home * 0.55 + ip_h * 0.45, 1)
        p_away = round(100 - p_home, 1)

    # Over/under lines
    def ou(line):
        spread = total_pts - line
        p_over = round(min(max(50 + spread * 3.5, 5), 95), 1)
        return p_over, round(100 - p_over, 1)

    o205, u205 = ou(205)
    o215, u215 = ou(215)
    o220, u220 = ou(220)
    o225, u225 = ou(225)
    o230, u230 = ou(230)
    o235, u235 = ou(235)

    # Quarter prediction (each quarter ~25% of total)
    q_avg = round(total_pts / 4, 1)
    home_q1 = round(home_pts / 4, 1)
    away_q1 = round(away_pts / 4, 1)

    return {
        "sport": "basketball",
        "home_pts": home_pts,
        "away_pts": away_pts,
        "total_pts": total_pts,
        "v1": p_home, "v2": p_away,
        "margin": round(abs(margin), 1),
        "home_favored": margin > 0,
        "o205": o205, "u205": u205,
        "o215": o215, "u215": u215,
        "o220": o220, "u220": u220,
        "o225": o225, "u225": u225,
        "o230": o230, "u230": u230,
        "o235": o235, "u235": u235,
        "home_q1": home_q1, "away_q1": away_q1, "q_avg": q_avg,
    }

# ─── NHL / AHL ────────────────────────────────────────────────────────────────
NHL_LEAGUES = [
    {"id": "icehockey_nhl",      "label": "🏒 NHL",             "group": "NHL"},
    {"id": "icehockey_nhl_championship_division", "label": "🏒 NHL Playoffs", "group": "NHL"},
    {"id": "icehockey_ahl",      "label": "🏒 AHL",             "group": "AHL"},
]

NHL_TEAM_STATS = {
    "Florida Panthers":       {"gf": 3.45, "ga": 2.58, "pp": 25.2, "pk": 82.1, "save": 0.912, "home_adv": 0.15},
    "Colorado Avalanche":     {"gf": 3.38, "ga": 2.72, "pp": 24.1, "pk": 81.5, "save": 0.905, "home_adv": 0.18},
    "Vancouver Canucks":      {"gf": 3.22, "ga": 2.65, "pp": 22.8, "pk": 80.5, "save": 0.908, "home_adv": 0.16},
    "Dallas Stars":           {"gf": 3.18, "ga": 2.48, "pp": 21.5, "pk": 83.2, "save": 0.918, "home_adv": 0.15},
    "New York Rangers":       {"gf": 3.28, "ga": 2.55, "pp": 23.1, "pk": 82.8, "save": 0.914, "home_adv": 0.17},
    "Boston Bruins":          {"gf": 3.15, "ga": 2.52, "pp": 20.8, "pk": 83.5, "save": 0.915, "home_adv": 0.16},
    "Toronto Maple Leafs":    {"gf": 3.42, "ga": 2.88, "pp": 25.5, "pk": 78.5, "save": 0.898, "home_adv": 0.17},
    "Edmonton Oilers":        {"gf": 3.55, "ga": 3.02, "pp": 28.2, "pk": 76.5, "save": 0.891, "home_adv": 0.16},
    "Carolina Hurricanes":    {"gf": 3.12, "ga": 2.45, "pp": 19.8, "pk": 84.2, "save": 0.920, "home_adv": 0.15},
    "Winnipeg Jets":          {"gf": 3.25, "ga": 2.55, "pp": 21.2, "pk": 82.5, "save": 0.912, "home_adv": 0.15},
    "Tampa Bay Lightning":    {"gf": 3.15, "ga": 2.68, "pp": 22.5, "pk": 81.2, "save": 0.906, "home_adv": 0.15},
    "Vegas Golden Knights":   {"gf": 3.08, "ga": 2.72, "pp": 20.5, "pk": 81.8, "save": 0.904, "home_adv": 0.16},
    "Nashville Predators":    {"gf": 2.85, "ga": 2.98, "pp": 18.5, "pk": 79.5, "save": 0.896, "home_adv": 0.14},
    "Pittsburgh Penguins":    {"gf": 2.78, "ga": 3.05, "pp": 18.2, "pk": 78.8, "save": 0.893, "home_adv": 0.14},
    "Detroit Red Wings":      {"gf": 2.72, "ga": 3.15, "pp": 17.5, "pk": 78.2, "save": 0.890, "home_adv": 0.14},
    "Ottawa Senators":        {"gf": 2.95, "ga": 3.18, "pp": 19.2, "pk": 77.5, "save": 0.888, "home_adv": 0.14},
    "Montreal Canadiens":     {"gf": 2.68, "ga": 3.22, "pp": 17.2, "pk": 77.8, "save": 0.887, "home_adv": 0.15},
    "New York Islanders":     {"gf": 2.75, "ga": 2.95, "pp": 17.8, "pk": 80.5, "save": 0.898, "home_adv": 0.14},
    "New Jersey Devils":      {"gf": 2.88, "ga": 2.85, "pp": 19.5, "pk": 80.8, "save": 0.899, "home_adv": 0.14},
    "Philadelphia Flyers":    {"gf": 2.65, "ga": 3.08, "pp": 16.8, "pk": 78.5, "save": 0.892, "home_adv": 0.14},
    "Minnesota Wild":         {"gf": 2.92, "ga": 2.75, "pp": 19.8, "pk": 81.5, "save": 0.906, "home_adv": 0.15},
    "Seattle Kraken":         {"gf": 2.85, "ga": 2.82, "pp": 18.8, "pk": 80.2, "save": 0.901, "home_adv": 0.14},
    "Calgary Flames":         {"gf": 2.88, "ga": 2.88, "pp": 19.2, "pk": 80.5, "save": 0.900, "home_adv": 0.15},
    "Los Angeles Kings":      {"gf": 2.95, "ga": 2.68, "pp": 19.5, "pk": 82.2, "save": 0.910, "home_adv": 0.15},
    "St. Louis Blues":        {"gf": 2.78, "ga": 2.98, "pp": 18.2, "pk": 79.2, "save": 0.895, "home_adv": 0.14},
    "San Jose Sharks":        {"gf": 2.35, "ga": 3.55, "pp": 14.5, "pk": 74.8, "save": 0.875, "home_adv": 0.13},
    "Anaheim Ducks":          {"gf": 2.42, "ga": 3.45, "pp": 15.2, "pk": 75.5, "save": 0.878, "home_adv": 0.13},
    "Chicago Blackhawks":     {"gf": 2.38, "ga": 3.52, "pp": 14.8, "pk": 75.2, "save": 0.876, "home_adv": 0.13},
    "Buffalo Sabres":         {"gf": 2.65, "ga": 3.18, "pp": 17.5, "pk": 77.5, "save": 0.888, "home_adv": 0.14},
    "Columbus Blue Jackets":  {"gf": 2.48, "ga": 3.38, "pp": 15.5, "pk": 76.2, "save": 0.882, "home_adv": 0.13},
    "Utah Hockey Club":       {"gf": 2.72, "ga": 2.92, "pp": 18.0, "pk": 80.0, "save": 0.898, "home_adv": 0.14},
}
NHL_DEFAULT = {"gf": 2.88, "ga": 2.88, "pp": 19.0, "pk": 80.0, "save": 0.900, "home_adv": 0.14}
NHL_AVG_GF = 2.88

def get_nhl_team(name):
    if name in NHL_TEAM_STATS:
        return NHL_TEAM_STATS[name]
    nl = name.lower()
    for k, v in NHL_TEAM_STATS.items():
        kl = k.lower()
        if nl in kl or any(w in nl for w in kl.split() if len(w) > 4):
            return v
    return NHL_DEFAULT.copy()

def poisson_p(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def compute_nhl(home, away, home_odds=None, away_odds=None):
    hs = get_nhl_team(home)
    as_ = get_nhl_team(away)

    # Expected goals (Poisson model)
    home_xg = round((hs["gf"] * as_["ga"] / NHL_AVG_GF) * (1 + hs["home_adv"]), 2)
    away_xg = round((as_["gf"] * hs["ga"] / NHL_AVG_GF), 2)
    home_xg = max(0.8, home_xg)
    away_xg = max(0.8, away_xg)
    total_xg = round(home_xg + away_xg, 2)

    # Score matrix (0-8 goals per team)
    max_g = 9
    score_matrix = {}
    for h in range(max_g):
        for a in range(max_g):
            score_matrix[(h, a)] = poisson_p(home_xg, h) * poisson_p(away_xg, a)

    p_home_reg = sum(v for (h, a), v in score_matrix.items() if h > a)
    p_draw_reg  = sum(v for (h, a), v in score_matrix.items() if h == a)
    p_away_reg  = sum(v for (h, a), v in score_matrix.items() if h < a)

    # OT/SO: ties split roughly 50/50
    p_home_win = round((p_home_reg + p_draw_reg * 0.5) * 100, 1)
    p_away_win = round((p_away_reg + p_draw_reg * 0.5) * 100, 1)
    p_ot        = round(p_draw_reg * 100, 1)

    if home_odds and away_odds:
        ip_h = 1/home_odds; ip_a = 1/away_odds
        s = ip_h+ip_a; ip_h,ip_a = ip_h/s*100, ip_a/s*100
        p_home_win = round(p_home_win*0.55 + ip_h*0.45, 1)
        p_away_win = round(100 - p_home_win, 1)

    # Over/under
    def ou(line):
        p_under = sum(poisson_p(total_xg, k) for k in range(int(line+0.5)+1))
        return round((1-p_under)*100,1), round(p_under*100,1)

    o45, u45 = ou(4)
    o55, u55 = ou(5)
    o65, u65 = ou(6)

    # BTTS (both teams score)
    p_home_scores = 1 - poisson_p(home_xg, 0)
    p_away_scores = 1 - poisson_p(away_xg, 0)
    btts = round(p_home_scores * p_away_scores * 100, 1)

    # Top scores
    score_probs = []
    for h in range(max_g):
        for a in range(max_g):
            p = round(score_matrix[(h,a)]*100, 2)
            if p >= 0.5:
                score_probs.append({"score":f"{h}-{a}","home_goals":h,"away_goals":a,"prob":p})
    score_probs.sort(key=lambda x:-x["prob"])

    return {
        "sport": "hockey",
        "home_xg": home_xg, "away_xg": away_xg, "total_xg": total_xg,
        "v1": p_home_win, "v2": p_away_win, "p_ot": p_ot,
        "btts": btts,
        "o45": o45, "u45": u45,
        "o55": o55, "u55": u55,
        "o65": o65, "u65": u65,
        "pp_home": hs["pp"], "pp_away": as_["pp"],
        "pk_home": hs["pk"], "pk_away": as_["pk"],
        "save_home": round(hs["save"]*100, 1),
        "save_away": round(as_["save"]*100, 1),
        "top_scores": score_probs[:10],
    }

# ─── Fetch helpers ─────────────────────────────────────────────────────────────
def _get_odds(api_key, league_id):
    url = f"{ODDS_API_BASE}/{league_id}/odds"
    params = {"apiKey": api_key, "regions": "us,eu", "markets": "h2h",
              "oddsFormat": "decimal", "dateFormat": "iso"}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 404: return []
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

def _parse_time(commence):
    try:
        dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d/%m %H:%M")
    except:
        return "?"

def _extract_h2h(game, home, away):
    home_odds = away_odds = None
    for bm in game.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] == "h2h":
                for o in mkt["outcomes"]:
                    if o["name"] == home: home_odds = o["price"]
                    elif o["name"] == away: away_odds = o["price"]
                break
        if home_odds: break
    return home_odds, away_odds

def fetch_nba_games(api_key, league_ids):
    all_games = []
    valid_ids = {l["id"] for l in NBA_LEAGUES}
    for lid in league_ids:
        if lid not in valid_ids: continue
        label = next((l["label"] for l in NBA_LEAGUES if l["id"]==lid), lid)
        for g in _get_odds(api_key, lid):
            home = g.get("home_team","")
            away = g.get("away_team","")
            ho, ao = _extract_h2h(g, home, away)
            preds = compute_nba(home, away, ho, ao)
            all_games.append({
                "league_id": lid, "league_label": label,
                "home": home, "away": away,
                "time": _parse_time(g.get("commence_time","")),
                "home_odds": ho, "away_odds": ao,
                **preds
            })
    return all_games

def fetch_nhl_games(api_key, league_ids):
    all_games = []
    valid_ids = {l["id"] for l in NHL_LEAGUES}
    for lid in league_ids:
        if lid not in valid_ids: continue
        label = next((l["label"] for l in NHL_LEAGUES if l["id"]==lid), lid)
        for g in _get_odds(api_key, lid):
            home = g.get("home_team","")
            away = g.get("away_team","")
            ho, ao = _extract_h2h(g, home, away)
            preds = compute_nhl(home, away, ho, ao)
            all_games.append({
                "league_id": lid, "league_label": label,
                "home": home, "away": away,
                "time": _parse_time(g.get("commence_time","")),
                "home_odds": ho, "away_odds": ao,
                **preds
            })
    return all_games
