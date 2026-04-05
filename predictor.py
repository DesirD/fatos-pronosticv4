"""
Fatos Pronostic — Enèji
Moteur de prédictions football multi-ligues
"""

import requests
import math
import os
from datetime import datetime

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"

# ─── LIGUES DISPONIBLES ───────────────────────────────────────────────────────
LEAGUES = [
    # Internationales
    {"id": "soccer_fifa_world_cup",              "label": "🌍 Coupe du Monde FIFA",                  "group": "International"},
    {"id": "soccer_fifa_world_cup_winner",        "label": "🏆 Coupe du Monde des Clubs FIFA",        "group": "International"},
    {"id": "soccer_international_friendlies",     "label": "🤝 International Friendly",               "group": "International"},
    {"id": "soccer_uefa_european_championship_qualification", "label": "🇪🇺 Qualifications CM UEFA",  "group": "International"},
    {"id": "soccer_uefa_nations_league",          "label": "🏴 UEFA Nations League",                  "group": "International"},
    # UEFA Clubs
    {"id": "soccer_uefa_champs_league",           "label": "⭐ UEFA Champions League",                "group": "UEFA Clubs"},
    {"id": "soccer_uefa_europa_league",           "label": "🟠 UEFA Europa League",                   "group": "UEFA Clubs"},
    {"id": "soccer_uefa_europa_conference_league","label": "🟢 UEFA Conference League",               "group": "UEFA Clubs"},
    # CONCACAF
    {"id": "soccer_concacaf_champions_cup",       "label": "🌎 CONCACAF Champions Cup",               "group": "CONCACAF"},
    # Coupes nationales
    {"id": "soccer_france_coupe_de_france",       "label": "🇫🇷 Coupe de France",                    "group": "Coupes"},
    {"id": "soccer_italy_coppa_italia",           "label": "🇮🇹 Coppa Italia",                        "group": "Coupes"},
    {"id": "soccer_spain_copa_del_rey",           "label": "🇪🇸 Copa del Rey",                        "group": "Coupes"},
    {"id": "soccer_belgium_cup",                  "label": "🇧🇪 Belgian Cup",                         "group": "Coupes"},
    # Angleterre
    {"id": "soccer_epl",                          "label": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Angleterre)",         "group": "Angleterre"},
    {"id": "soccer_efl_champ",                   "label": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship (Angleterre)",            "group": "Angleterre"},
    {"id": "soccer_england_league1",              "label": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One (Angleterre)",             "group": "Angleterre"},
    # Espagne
    {"id": "soccer_spain_la_liga",                "label": "🇪🇸 La Liga (Espagne)",                   "group": "Espagne"},
    {"id": "soccer_spain_segunda_division",       "label": "🇪🇸 La Liga 2 (Espagne)",                 "group": "Espagne"},
    # Italie
    {"id": "soccer_italy_serie_a",                "label": "🇮🇹 Serie A (Italie)",                    "group": "Italie"},
    # Allemagne
    {"id": "soccer_germany_bundesliga",           "label": "🇩🇪 Bundesliga (Allemagne)",              "group": "Allemagne"},
    {"id": "soccer_germany_bundesliga2",          "label": "🇩🇪 2. Bundesliga (Allemagne)",           "group": "Allemagne"},
    {"id": "soccer_germany_liga3",                "label": "🇩🇪 3. Liga (Allemagne)",                 "group": "Allemagne"},
    # France
    {"id": "soccer_france_ligue_1",               "label": "🇫🇷 Ligue 1 (France)",                   "group": "France"},
    # Autres ligues
    {"id": "soccer_mexico_ligamx",                "label": "🇲🇽 Liga MX Clausura (Mexique)",          "group": "Amériques"},
    {"id": "soccer_usa_mls",                      "label": "🇺🇸 Major League Soccer (USA)",           "group": "Amériques"},
    {"id": "soccer_brazil_campeonato",            "label": "🇧🇷 Brasileirão Betano (Brésil)",         "group": "Amériques"},
    {"id": "soccer_serbia_superliga",             "label": "🇷🇸 Mozzart Bet Superliga (Serbie)",      "group": "Europe Est"},
    {"id": "soccer_ukraine_premier_league",       "label": "🇺🇦 Premier League (Ukraine)",            "group": "Europe Est"},
    {"id": "soccer_slovenia_prvaliga",            "label": "🇸🇮 Prvaliga (Slovénie)",                 "group": "Europe Est"},
    {"id": "soccer_czech_republic_first_league",  "label": "🇨🇿 Czech First League",                  "group": "Europe Est"},
    {"id": "soccer_croatia_hnl",                  "label": "🇭🇷 HNL (Croatie)",                       "group": "Europe Est"},
    {"id": "soccer_turkey_super_league",          "label": "🇹🇷 Trendyol Süper Lig (Turquie)",       "group": "Europe Est"},
    {"id": "soccer_scotland_premiership",         "label": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scottish Premiership (Écosse)",      "group": "Europe"},
    {"id": "soccer_netherlands",                  "label": "🇳🇱 Eredivisie (Pays-Bas)",               "group": "Europe"},
    {"id": "soccer_montenegro_prva_liga",         "label": "🇲🇪 Montenegrin First League",            "group": "Europe Est"},
    {"id": "soccer_saudi_professional_league",    "label": "🇸🇦 Saudi Pro League",                    "group": "Moyen-Orient"},
    {"id": "soccer_saudi_division1",              "label": "🇸🇦 Saudi Division 1",                    "group": "Moyen-Orient"},
    {"id": "soccer_denmark_superliga",            "label": "🇩🇰 Danish Superliga",                    "group": "Europe"},
    {"id": "soccer_switzerland_superleague",      "label": "🇨🇭 Swiss Super League",                  "group": "Europe"},
    {"id": "soccer_norway_eliteserien",           "label": "🇳🇴 Eliteserien (Norvège)",               "group": "Europe"},
    {"id": "soccer_norway_1st_division",          "label": "🇳🇴 1st Division (Norvège)",              "group": "Europe"},
    {"id": "soccer_belgium_first_div",            "label": "🇧🇪 Pro League (Belgique)",               "group": "Europe"},
    {"id": "soccer_belgium_second_div",           "label": "🇧🇪 Challenger Pro League (Belgique)",    "group": "Europe"},
]

# ─── GROS CLUBS (filtre "Meilleurs par FATOS") ────────────────────────────────
TOP_CLUBS = {
    # Premier League
    "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United",
    "Tottenham", "Newcastle United", "Aston Villa", "West Ham", "Brighton",
    # La Liga
    "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Club", "Villarreal",
    "Real Sociedad", "Real Betis", "Sevilla",
    # Serie A
    "Inter Milan", "Napoli", "AC Milan", "Juventus", "Atalanta", "Lazio", "Roma", "Fiorentina",
    "Internazionale",
    # Bundesliga
    "Bayern Munich", "Bayer Leverkusen", "Borussia Dortmund", "RB Leipzig",
    "Eintracht Frankfurt", "Stuttgart", "Wolfsburg",
    # Ligue 1
    "Paris Saint-Germain", "Monaco", "Marseille", "Lille", "Lyon", "Nice", "Rennes",
    # Champions League + autres
    "Porto", "Benfica", "Sporting CP", "Ajax", "PSV Eindhoven", "Feyenoord",
    "Celtic", "Rangers", "Galatasaray", "Fenerbahce", "Besiktas",
    "Shakhtar Donetsk", "Dynamo Kyiv",
    "Al Hilal", "Al Nassr", "Al Ahli", "Al Ittihad",
    "Club America", "Cruz Azul", "Chivas", "Tigres UANL",
    "Flamengo", "Palmeiras", "Atletico Mineiro", "Sao Paulo", "Corinthians",
    "Red Bull New York", "LA Galaxy", "Inter Miami", "Seattle Sounders",
}

def is_top_club(name):
    """Check if a team is a top club (fuzzy match)."""
    if name in TOP_CLUBS:
        return True
    name_lower = name.lower()
    for club in TOP_CLUBS:
        if club.lower() in name_lower or name_lower in club.lower():
            return True
        # Match on significant words
        words = [w for w in club.split() if len(w) > 4]
        if any(w.lower() in name_lower for w in words):
            return True
    return False

def is_top_match(home, away):
    """True if at least one team is a top club."""
    return is_top_club(home) or is_top_club(away)

# ─── STATS ÉQUIPES PAR LIGUE ──────────────────────────────────────────────────
LEAGUE_AVG_STATS = {
    "soccer_epl":                 {"gf":1.55,"ga":1.55,"shots":13.2,"shots_a":13.2,"corners":10.1,"cards":3.2,"saves":3.8,"xg":1.55},
    "soccer_efl_champ":           {"gf":1.42,"ga":1.42,"shots":12.1,"shots_a":12.1,"corners":10.4,"cards":3.8,"saves":3.5,"xg":1.42},
    "soccer_england_league1":     {"gf":1.38,"ga":1.38,"shots":11.5,"shots_a":11.5,"corners":10.2,"cards":4.1,"saves":3.4,"xg":1.38},
    "soccer_spain_la_liga":       {"gf":1.48,"ga":1.48,"shots":12.8,"shots_a":12.8,"corners":9.8, "cards":3.9,"saves":3.6,"xg":1.48},
    "soccer_spain_segunda_division":{"gf":1.35,"ga":1.35,"shots":11.8,"shots_a":11.8,"corners":10.1,"cards":4.2,"saves":3.3,"xg":1.35},
    "soccer_italy_serie_a":       {"gf":1.52,"ga":1.52,"shots":13.5,"shots_a":13.5,"corners":9.9, "cards":3.5,"saves":3.9,"xg":1.52},
    "soccer_germany_bundesliga":  {"gf":1.72,"ga":1.72,"shots":14.1,"shots_a":14.1,"corners":10.3,"cards":3.1,"saves":4.0,"xg":1.72},
    "soccer_germany_bundesliga2": {"gf":1.58,"ga":1.58,"shots":12.9,"shots_a":12.9,"corners":10.5,"cards":3.4,"saves":3.7,"xg":1.58},
    "soccer_germany_liga3":       {"gf":1.44,"ga":1.44,"shots":11.6,"shots_a":11.6,"corners":10.2,"cards":3.9,"saves":3.4,"xg":1.44},
    "soccer_france_ligue_1":      {"gf":1.46,"ga":1.46,"shots":12.4,"shots_a":12.4,"corners":9.7, "cards":3.7,"saves":3.5,"xg":1.46},
    "soccer_uefa_champs_league":  {"gf":1.62,"ga":1.62,"shots":13.8,"shots_a":13.8,"corners":9.8, "cards":2.9,"saves":4.1,"xg":1.62},
    "soccer_uefa_europa_league":  {"gf":1.55,"ga":1.55,"shots":13.1,"shots_a":13.1,"corners":9.9, "cards":3.0,"saves":3.8,"xg":1.55},
    "soccer_uefa_europa_conference_league":{"gf":1.68,"ga":1.68,"shots":13.5,"shots_a":13.5,"corners":10.2,"cards":3.1,"saves":3.9,"xg":1.68},
    "soccer_usa_mls":             {"gf":1.58,"ga":1.58,"shots":13.0,"shots_a":13.0,"corners":9.5, "cards":3.3,"saves":3.7,"xg":1.58},
    "soccer_brazil_campeonato":   {"gf":1.44,"ga":1.44,"shots":13.3,"shots_a":13.3,"corners":9.4, "cards":4.1,"saves":3.8,"xg":1.44},
    "default":                    {"gf":1.48,"ga":1.48,"shots":12.5,"shots_a":12.5,"corners":10.0,"cards":3.5,"saves":3.6,"xg":1.48},
}

TEAM_STATS = {
    "Manchester City":   {"att":1.85,"def":0.95,"form":0.72,"home_adv":0.15,"shots":15.2,"corners":6.1,"cards":1.6,"saves":3.2},
    "Arsenal":           {"att":1.78,"def":0.88,"form":0.71,"home_adv":0.14,"shots":14.9,"corners":5.9,"cards":1.5,"saves":3.0},
    "Liverpool":         {"att":2.01,"def":1.02,"form":0.74,"home_adv":0.16,"shots":15.8,"corners":6.3,"cards":1.7,"saves":3.5},
    "Chelsea":           {"att":1.62,"def":1.18,"form":0.58,"home_adv":0.12,"shots":13.8,"corners":5.5,"cards":1.8,"saves":3.8},
    "Manchester United": {"att":1.42,"def":1.35,"form":0.48,"home_adv":0.11,"shots":12.5,"corners":5.2,"cards":1.9,"saves":4.1},
    "Tottenham":         {"att":1.68,"def":1.28,"form":0.54,"home_adv":0.12,"shots":13.5,"corners":5.4,"cards":1.7,"saves":3.9},
    "Newcastle United":  {"att":1.71,"def":1.08,"form":0.62,"home_adv":0.13,"shots":14.1,"corners":5.7,"cards":1.6,"saves":3.4},
    "Aston Villa":       {"att":1.65,"def":1.15,"form":0.60,"home_adv":0.12,"shots":13.2,"corners":5.3,"cards":1.8,"saves":3.6},
    "Real Madrid":       {"att":2.15,"def":0.85,"form":0.78,"home_adv":0.18,"shots":16.2,"corners":6.5,"cards":1.5,"saves":2.8},
    "Barcelona":         {"att":2.28,"def":0.92,"form":0.76,"home_adv":0.17,"shots":17.1,"corners":6.8,"cards":1.4,"saves":2.9},
    "Atletico Madrid":   {"att":1.58,"def":0.78,"form":0.68,"home_adv":0.14,"shots":12.8,"corners":5.1,"cards":2.1,"saves":3.2},
    "Athletic Club":     {"att":1.48,"def":1.05,"form":0.62,"home_adv":0.13,"shots":12.1,"corners":5.0,"cards":2.0,"saves":3.5},
    "Villarreal":        {"att":1.45,"def":1.18,"form":0.55,"home_adv":0.12,"shots":12.5,"corners":5.2,"cards":1.8,"saves":3.6},
    "Inter Milan":       {"att":2.05,"def":0.88,"form":0.75,"home_adv":0.16,"shots":15.5,"corners":6.2,"cards":1.6,"saves":3.1},
    "Napoli":            {"att":1.88,"def":0.95,"form":0.70,"home_adv":0.15,"shots":14.8,"corners":5.8,"cards":1.7,"saves":3.3},
    "AC Milan":          {"att":1.72,"def":1.02,"form":0.65,"home_adv":0.14,"shots":14.1,"corners":5.6,"cards":1.8,"saves":3.5},
    "Juventus":          {"att":1.58,"def":0.98,"form":0.62,"home_adv":0.13,"shots":13.2,"corners":5.4,"cards":1.9,"saves":3.4},
    "Atalanta":          {"att":2.12,"def":1.15,"form":0.71,"home_adv":0.14,"shots":15.8,"corners":6.4,"cards":1.7,"saves":3.6},
    "Lazio":             {"att":1.65,"def":1.21,"form":0.58,"home_adv":0.13,"shots":13.5,"corners":5.5,"cards":2.0,"saves":3.7},
    "Bayern Munich":     {"att":2.42,"def":0.92,"form":0.76,"home_adv":0.18,"shots":18.5,"corners":7.2,"cards":1.4,"saves":3.0},
    "Bayer Leverkusen":  {"att":2.18,"def":0.85,"form":0.78,"home_adv":0.17,"shots":16.8,"corners":6.6,"cards":1.3,"saves":2.9},
    "Borussia Dortmund": {"att":1.92,"def":1.18,"form":0.65,"home_adv":0.15,"shots":15.2,"corners":6.1,"cards":1.6,"saves":3.5},
    "RB Leipzig":        {"att":1.88,"def":1.05,"form":0.68,"home_adv":0.15,"shots":15.5,"corners":6.2,"cards":1.5,"saves":3.2},
    "Eintracht Frankfurt":{"att":1.65,"def":1.15,"form":0.60,"home_adv":0.13,"shots":13.8,"corners":5.5,"cards":1.8,"saves":3.5},
    "Paris Saint-Germain":{"att":2.35,"def":0.78,"form":0.82,"home_adv":0.20,"shots":17.8,"corners":7.0,"cards":1.4,"saves":2.5},
    "Monaco":            {"att":1.95,"def":1.05,"form":0.72,"home_adv":0.15,"shots":15.2,"corners":6.0,"cards":1.6,"saves":3.2},
    "Marseille":         {"att":1.68,"def":1.18,"form":0.62,"home_adv":0.14,"shots":13.8,"corners":5.5,"cards":1.9,"saves":3.6},
    "Lille":             {"att":1.55,"def":0.98,"form":0.64,"home_adv":0.13,"shots":13.1,"corners":5.3,"cards":1.7,"saves":3.3},
    "Lyon":              {"att":1.62,"def":1.15,"form":0.58,"home_adv":0.13,"shots":13.4,"corners":5.4,"cards":1.8,"saves":3.5},
    "Internazionale":    {"att":2.05,"def":0.88,"form":0.75,"home_adv":0.16,"shots":15.5,"corners":6.2,"cards":1.6,"saves":3.1},
    "Porto":             {"att":1.72,"def":0.98,"form":0.68,"home_adv":0.15,"shots":14.2,"corners":5.7,"cards":1.7,"saves":3.3},
    "Benfica":           {"att":1.85,"def":0.95,"form":0.70,"home_adv":0.16,"shots":14.8,"corners":5.9,"cards":1.6,"saves":3.2},
}

DEFAULT_STATS = {"att":1.48,"def":1.48,"form":0.50,"home_adv":0.10,"shots":12.5,"corners":5.0,"cards":1.8,"saves":3.5}


def get_team_stats(name):
    if name in TEAM_STATS:
        return TEAM_STATS[name]
    for key in TEAM_STATS:
        if any(w in key for w in name.split() if len(w) > 3):
            return TEAM_STATS[key]
    return DEFAULT_STATS.copy()


def get_league_avg(league_id):
    return LEAGUE_AVG_STATS.get(league_id, LEAGUE_AVG_STATS["default"])


def odds_to_prob(decimal_odds):
    if not decimal_odds or decimal_odds <= 1:
        return 0.0
    return 1.0 / decimal_odds


def normalize_probs(*probs):
    total = sum(probs)
    if total == 0:
        return probs
    return tuple(p / total for p in probs)


def compute_predictions(home, away, league_id, home_odds=None, away_odds=None, draw_odds=None):
    hs = get_team_stats(home)
    as_ = get_team_stats(away)
    lg = get_league_avg(league_id)

    home_xg = (hs["att"] * as_["def"] / lg["gf"]) * lg["gf"] * (1 + hs["home_adv"])
    away_xg = (as_["att"] * hs["def"] / lg["gf"]) * lg["gf"]
    home_xg = max(0.3, round(home_xg, 2))
    away_xg = max(0.3, round(away_xg, 2))
    total_xg = round(home_xg + away_xg, 2)

    def poisson(lam, k):
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

    max_g = 7
    score_matrix = {}
    for h in range(max_g):
        for a in range(max_g):
            score_matrix[(h, a)] = poisson(home_xg, h) * poisson(away_xg, a)

    p_home_win = sum(v for (h, a), v in score_matrix.items() if h > a)
    p_draw     = sum(v for (h, a), v in score_matrix.items() if h == a)
    p_away_win = sum(v for (h, a), v in score_matrix.items() if h < a)
    p_home_win, p_draw, p_away_win = normalize_probs(p_home_win, p_draw, p_away_win)

    if home_odds and away_odds and draw_odds:
        ip_h = odds_to_prob(home_odds)
        ip_d = odds_to_prob(draw_odds)
        ip_a = odds_to_prob(away_odds)
        ip_h, ip_d, ip_a = normalize_probs(ip_h, ip_d, ip_a)
        blend = 0.55
        p_home_win = p_home_win * blend + ip_h * (1 - blend)
        p_draw     = p_draw     * blend + ip_d * (1 - blend)
        p_away_win = p_away_win * blend + ip_a * (1 - blend)
        p_home_win, p_draw, p_away_win = normalize_probs(p_home_win, p_draw, p_away_win)

    v1 = round(p_home_win * 100, 1)
    vx = round(p_draw     * 100, 1)
    v2 = round(p_away_win * 100, 1)

    dc_x1 = round((p_home_win + p_draw) * 100, 1)
    dc_x2 = round((p_away_win + p_draw) * 100, 1)
    dc_12 = round((p_home_win + p_away_win) * 100, 1)

    p_home_scores = 1 - poisson(home_xg, 0)
    p_away_scores = 1 - poisson(away_xg, 0)
    p_btts_yes = round(p_home_scores * p_away_scores * 100, 1)
    p_btts_no  = round(100 - p_btts_yes, 1)

    def over_under(lam, line):
        p_under = sum(poisson(lam, k) for k in range(int(line + 0.5) + 1))
        return round((1 - p_under) * 100, 1), round(p_under * 100, 1)

    ho05, hu05 = over_under(home_xg, 0)
    ho15, hu15 = over_under(home_xg, 1)
    ho25, hu25 = over_under(home_xg, 2)
    ao05, au05 = over_under(away_xg, 0)
    ao15, au15 = over_under(away_xg, 1)
    ao25, au25 = over_under(away_xg, 2)
    to15, tu15 = over_under(total_xg, 1)
    to25, tu25 = over_under(total_xg, 2)
    to35, tu35 = over_under(total_xg, 3)
    to45, tu45 = over_under(total_xg, 4)

    home_shots = round((hs["shots"] + as_["shots"]) / 2 * 0.95, 1)
    away_shots = round((as_["shots"] + hs["shots"]) / 2 * 0.85, 1)
    total_shots = round(home_shots + away_shots, 1)

    home_corners = round(hs["corners"] * 1.05, 1)
    away_corners = round(as_["corners"] * 0.95, 1)
    total_corners = round(home_corners + away_corners, 1)

    home_cards = round(hs["cards"], 1)
    away_cards = round(as_["cards"] * 1.05, 1)
    total_cards = round(home_cards + away_cards, 1)

    home_saves = round(hs["saves"] * 0.95, 1)
    away_saves = round(as_["saves"] * 1.05, 1)
    total_saves = round(home_saves + away_saves, 1)

    corners_o85, corners_u85 = over_under(total_corners, 8)
    corners_o95, corners_u95 = over_under(total_corners, 9)
    corners_o105,corners_u105= over_under(total_corners, 10)
    cards_o25, cards_u25 = over_under(total_cards, 2)
    cards_o35, cards_u35 = over_under(total_cards, 3)
    cards_o45, cards_u45 = over_under(total_cards, 4)
    shots_o25, shots_u25 = over_under(total_shots, 25)
    shots_o28, shots_u28 = over_under(total_shots, 28)
    saves_o5, saves_u5 = over_under(total_saves, 5)
    saves_o7, saves_u7 = over_under(total_saves, 7)

    dc_x1_btts = round(dc_x1 * p_btts_yes / 100, 1)
    dc_x2_btts = round(dc_x2 * p_btts_yes / 100, 1)
    dc_12_btts = round(dc_12 * p_btts_yes / 100, 1)
    v1_btts = round(v1 * p_btts_yes / 100, 1)
    vx_btts = round(vx * p_btts_yes / 100, 1)
    v2_btts = round(v2 * p_btts_yes / 100, 1)
    v1_o25 = round(v1 * to25 / 100, 1)
    vx_o25 = round(vx * to25 / 100, 1)
    v2_o25 = round(v2 * to25 / 100, 1)
    v1_u25 = round(v1 * tu25 / 100, 1)
    vx_u25 = round(vx * tu25 / 100, 1)
    v2_u25 = round(v2 * tu25 / 100, 1)
    dc_x1_o25 = round(dc_x1 * to25 / 100, 1)
    dc_x2_o25 = round(dc_x2 * to25 / 100, 1)
    dc_12_o25 = round(dc_12 * to25 / 100, 1)
    btts_o25 = round(p_btts_yes * to25 / 100, 1)
    btts_u25 = round(p_btts_yes * tu25 / 100, 1)
    p_home_wins_ht = round(min(v1 * 0.65 + 10, 75), 1)
    p_away_wins_ht = round(min(v2 * 0.65 + 10, 75), 1)

    # ── Score exact (top 9 scores les plus probables via matrice Poisson) ────
    score_probs = []
    for h in range(max_g):
        for a in range(max_g):
            prob_pct = round(score_matrix[(h, a)] * 100, 2)
            if prob_pct >= 0.5:
                score_probs.append({
                    "score": f"{h}-{a}",
                    "home_goals": h,
                    "away_goals": a,
                    "prob": prob_pct
                })
    score_probs.sort(key=lambda x: -x["prob"])
    top_scores = score_probs[:12]

    return {
        "home_xg": home_xg, "away_xg": away_xg, "total_xg": total_xg,
        "v1": v1, "vx": vx, "v2": v2,
        "dc_x1": dc_x1, "dc_x2": dc_x2, "dc_12": dc_12,
        "btts_yes": p_btts_yes, "btts_no": p_btts_no,
        "to15": to15, "tu15": tu15,
        "to25": to25, "tu25": tu25,
        "to35": to35, "tu35": tu35,
        "to45": to45, "tu45": tu45,
        "ho05": ho05, "hu05": hu05, "ho15": ho15, "hu15": hu15, "ho25": ho25, "hu25": hu25,
        "ao05": ao05, "au05": au05, "ao15": ao15, "au15": au15, "ao25": ao25, "au25": au25,
        "total_corners": total_corners,
        "corners_o85": corners_o85, "corners_u85": corners_u85,
        "corners_o95": corners_o95, "corners_u95": corners_u95,
        "corners_o105": corners_o105,"corners_u105": corners_u105,
        "total_cards": total_cards,
        "cards_o25": cards_o25, "cards_u25": cards_u25,
        "cards_o35": cards_o35, "cards_u35": cards_u35,
        "cards_o45": cards_o45, "cards_u45": cards_u45,
        "total_shots": total_shots,
        "shots_o25": shots_o25, "shots_u25": shots_u25,
        "shots_o28": shots_o28, "shots_u28": shots_u28,
        "total_saves": total_saves,
        "saves_o5": saves_o5, "saves_u5": saves_u5,
        "saves_o7": saves_o7, "saves_u7": saves_u7,
        "dc_x1_btts": dc_x1_btts, "dc_x2_btts": dc_x2_btts, "dc_12_btts": dc_12_btts,
        "v1_btts": v1_btts, "vx_btts": vx_btts, "v2_btts": v2_btts,
        "v1_o25": v1_o25, "vx_o25": vx_o25, "v2_o25": v2_o25,
        "v1_u25": v1_u25, "vx_u25": vx_u25, "v2_u25": v2_u25,
        "dc_x1_o25": dc_x1_o25, "dc_x2_o25": dc_x2_o25, "dc_12_o25": dc_12_o25,
        "btts_o25": btts_o25, "btts_u25": btts_u25,
        "home_wins_ht": p_home_wins_ht, "away_wins_ht": p_away_wins_ht,
        "top_scores": top_scores,
    }


def prob_to_decimal_odds(prob_pct):
    if prob_pct <= 0:
        return 99.0
    return round(100 / prob_pct, 2)


# ─── RANGES DE COTES POUR LE COMBINÉ ─────────────────────────────────────────
SAFE_RANGES = {
    "range1": (1.15, 1.20),
    "range2": (1.21, 1.29),
    "range3": (1.31, 1.39),
}
RISKY_RANGES = {
    "range1": (1.40, 1.60),
    "range2": (1.61, 1.80),
    "range3": (1.81, 2.50),
}


def generate_combiners(games, target_odds, safe_ranges=None, risky_ranges=None, top_only=False):
    """
    Build 2 combiners (safe + risky) with configurable odds ranges.
    safe_ranges / risky_ranges: list of (min, max) tuples selected by user.
    top_only: if True, only use games involving at least one top club.
    """
    if safe_ranges is None:
        safe_ranges = [(1.15, 1.40)]
    if risky_ranges is None:
        risky_ranges = [(1.40, 2.50)]

    # Optionally filter to top clubs only
    filtered_games = games
    if top_only:
        filtered_games = [g for g in games if is_top_match(g["home"], g["away"])]
        if not filtered_games:
            filtered_games = games  # fallback if no top matches found

    PRONO_LABELS = {
        "v1":           "Victoire Domicile (1)",
        "v2":           "Victoire Extérieur (2)",
        "vx":           "Match Nul (X)",
        "dc_x1":        "Double Chance X1",
        "dc_x2":        "Double Chance X2",
        "dc_12":        "Double Chance 12",
        "btts_yes":     "Les 2 équipes marquent (Oui)",
        "btts_no":      "Les 2 équipes ne marquent pas",
        "to15":         "Total Buts Over 1.5",
        "to25":         "Total Buts Over 2.5",
        "tu25":         "Total Buts Under 2.5",
        "to35":         "Total Buts Over 3.5",
        "ho05":         "Dom. marque (Over 0.5)",
        "ho15":         "Dom. Over 1.5 buts",
        "ao05":         "Ext. marque (Over 0.5)",
        "ao15":         "Ext. Over 1.5 buts",
        "dc_x1_btts":   "X1 + Les 2 marquent",
        "dc_12_btts":   "12 + Les 2 marquent",
        "v1_btts":      "Dom. gagne + Les 2 marquent",
        "v2_btts":      "Ext. gagne + Les 2 marquent",
        "btts_o25":     "Les 2 marquent + Over 2.5",
        "home_wins_ht": "Dom. gagne ≥1 mi-temps",
    }

    all_picks = []
    for g in filtered_games:
        match_label = f"{g['away']} @ {g['home']}"
        league = g.get("league_label", "")
        for key, label in PRONO_LABELS.items():
            prob = g.get(key)
            if prob and prob >= 10:
                dec = prob_to_decimal_odds(prob)
                all_picks.append({
                    "match": match_label,
                    "league": league,
                    "time": g.get("time", "?"),
                    "prono": label,
                    "prob": prob,
                    "odds": dec,
                    "key": key,
                    "home": g["home"],
                    "away": g["away"],
                    "is_top": is_top_match(g["home"], g["away"]),
                })

    all_picks.sort(key=lambda x: -x["prob"])

    def in_ranges(odds, ranges):
        return any(lo <= odds <= hi for (lo, hi) in ranges)

    def build_combiner(picks_pool, target, prefer_high_prob):
        used_matches = set()
        selected = []
        product = 1.0
        if prefer_high_prob:
            pool = sorted(picks_pool, key=lambda x: -x["prob"])
        else:
            mid = sum(lo + hi for lo, hi in risky_ranges) / (2 * len(risky_ranges))
            pool = sorted(picks_pool, key=lambda x: abs(x["odds"] - mid))

        for pick in pool:
            if pick["match"] in used_matches:
                continue
            new_product = product * pick["odds"]
            if new_product <= target * 1.5 or len(selected) == 0:
                selected.append(pick)
                product = new_product
                used_matches.add(pick["match"])
                if product >= target * 0.85:
                    break
        return selected, round(product, 2)

    safe_pool = [p for p in all_picks if in_ranges(p["odds"], safe_ranges)]
    safe_picks, safe_odds = build_combiner(safe_pool, target_odds, prefer_high_prob=True)

    risky_pool = [p for p in all_picks if in_ranges(p["odds"], risky_ranges) and p["prob"] >= 25]
    risky_picks, risky_odds = build_combiner(risky_pool, target_odds, prefer_high_prob=False)

    return {
        "target": target_odds,
        "top_only": top_only,
        "safe": {"picks": safe_picks, "combined_odds": safe_odds, "count": len(safe_picks)},
        "risky": {"picks": risky_picks, "combined_odds": risky_odds, "count": len(risky_picks)},
    }


def get_odds_for_league(api_key, league_id):
    url = f"{ODDS_API_BASE}/{league_id}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu,uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def fetch_all_games(api_key, league_ids, top_only=False):
    all_games = []
    for lid in league_ids:
        games = get_odds_for_league(api_key, lid)
        league_label = next((l["label"] for l in LEAGUES if l["id"] == lid), lid)
        for g in games:
            home = g.get("home_team", "")
            away = g.get("away_team", "")
            commence = g.get("commence_time", "")
            try:
                dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                local_time = dt.astimezone().strftime("%d/%m %H:%M")
            except:
                local_time = "?"

            home_odds = away_odds = draw_odds = None
            for bm in g.get("bookmakers", []):
                for market in bm.get("markets", []):
                    if market["key"] == "h2h":
                        for o in market["outcomes"]:
                            if o["name"] == home:
                                home_odds = o["price"]
                            elif o["name"] == away:
                                away_odds = o["price"]
                            elif o["name"] == "Draw":
                                draw_odds = o["price"]
                        break
                if home_odds:
                    break

            top_match = is_top_match(home, away)
            if top_only and not top_match:
                continue

            preds = compute_predictions(home, away, lid, home_odds, away_odds, draw_odds)

            all_games.append({
                "league_id": lid,
                "league_label": league_label,
                "home": home, "away": away,
                "time": local_time,
                "home_odds": home_odds,
                "away_odds": away_odds,
                "draw_odds": draw_odds,
                "is_top": top_match,
                **preds,
            })
    return all_games
