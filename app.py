"""
Fatos Pronostic — Flask Web App
With authentication, user management & activity logging
"""
import os
import json
import hashlib
import secrets
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

from predictor import LEAGUES, SAFE_RANGES, RISKY_RANGES, fetch_all_games, generate_combiners
from predictor_sports import (
    NBA_LEAGUES, NHL_LEAGUES,
    fetch_nba_games, fetch_nhl_games
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ─── File paths ───────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE, "users.json")
LOGS_FILE  = os.path.join(BASE, "activity_logs.json")

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        default = {
            "admin": {
                "password": _hash("@Godofpronostic117$"),
                "role": "admin",
                "api_key": ""
            }
        }
        _save_users(default)
        return default
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def _load_logs() -> list:
    if not os.path.exists(LOGS_FILE):
        return []
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _log(username: str, action: str, detail: str = "", ip: str = "", ua: str = ""):
    logs = _load_logs()
    logs.append({
        "username": username,
        "action": action,
        "detail": detail,
        "ip": ip,
        "ua": ua,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # keep last 2000 entries
    logs = logs[-2000:]
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# ─── Auth decorators ──────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Non authentifié"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        users = _load_users()
        username = session.get("user")
        if not username or users.get(username, {}).get("role") != "admin":
            return jsonify({"success": False, "error": "Accès admin requis"}), 403
        return f(*args, **kwargs)
    return decorated

# ─── Auth routes ──────────────────────────────────────────────────────────────
@app.route("/login")
def login_page():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    users = _load_users()
    user = users.get(username)
    if not user or user["password"] != _hash(password):
        return jsonify({"success": False, "error": "Identifiants incorrects"}), 401
    session["user"] = username
    session["role"] = user.get("role", "user")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "")
    _log(username, "login", ip=ip, ua=ua)
    return jsonify({"success": True, "username": username, "role": session["role"]})

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    if session.get("user"):
        _log(session["user"], "logout")
    session.clear()
    return jsonify({"success": True})

@app.route("/api/auth/me")
def api_me():
    if not session.get("user"):
        return jsonify({"authenticated": False}), 401
    users = _load_users()
    u = users.get(session["user"], {})
    return jsonify({
        "authenticated": True,
        "username": session["user"],
        "role": session["role"],
        "api_key": u.get("api_key", "")
    })

# ─── User management ─────────────────────────────────────────────────────────
@app.route("/api/users", methods=["GET"])
@login_required
@admin_required
def api_list_users():
    users = _load_users()
    return jsonify([
        {"username": u, "role": v["role"], "api_key": v.get("api_key", "")}
        for u, v in users.items()
    ])

@app.route("/api/users", methods=["POST"])
@login_required
@admin_required
def api_create_user():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "user")
    api_key = data.get("api_key", "").strip()
    if not username or not password:
        return jsonify({"success": False, "error": "Nom d'utilisateur et mot de passe requis"}), 400
    if role not in ("admin", "user"):
        return jsonify({"success": False, "error": "Rôle invalide"}), 400
    users = _load_users()
    if username in users:
        return jsonify({"success": False, "error": "Cet utilisateur existe déjà"}), 409
    users[username] = {"password": _hash(password), "role": role, "api_key": api_key}
    _save_users(users)
    return jsonify({"success": True})

@app.route("/api/users/<username>", methods=["PUT"])
@login_required
@admin_required
def api_update_user(username):
    data = request.get_json()
    users = _load_users()
    if username not in users:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404
    if users[username]["role"] == "admin":
        admins = [u for u, v in users.items() if v["role"] == "admin"]
        new_role = data.get("role", users[username]["role"])
        if new_role != "admin" and len(admins) == 1:
            return jsonify({"success": False, "error": "Impossible de retirer le dernier admin"}), 400
    if "password" in data and data["password"]:
        users[username]["password"] = _hash(data["password"])
    if "role" in data and data["role"] in ("admin", "user"):
        users[username]["role"] = data["role"]
    if "api_key" in data:
        users[username]["api_key"] = data["api_key"].strip()
    _save_users(users)
    return jsonify({"success": True})

@app.route("/api/users/<username>", methods=["DELETE"])
@login_required
@admin_required
def api_delete_user(username):
    users = _load_users()
    if username not in users:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404
    if username == session.get("user"):
        return jsonify({"success": False, "error": "Vous ne pouvez pas vous supprimer vous-même"}), 400
    admins = [u for u, v in users.items() if v["role"] == "admin"]
    if users[username]["role"] == "admin" and len(admins) == 1:
        return jsonify({"success": False, "error": "Impossible de supprimer le dernier admin"}), 400
    del users[username]
    _save_users(users)
    return jsonify({"success": True})

@app.route("/api/users/me/password", methods=["PUT"])
@login_required
def api_change_own_password():
    data = request.get_json()
    current = data.get("current_password", "")
    new_pw = data.get("new_password", "")
    if not new_pw:
        return jsonify({"success": False, "error": "Nouveau mot de passe requis"}), 400
    users = _load_users()
    username = session["user"]
    if users[username]["password"] != _hash(current):
        return jsonify({"success": False, "error": "Mot de passe actuel incorrect"}), 401
    users[username]["password"] = _hash(new_pw)
    _save_users(users)
    return jsonify({"success": True})

# ─── Activity logs ────────────────────────────────────────────────────────────
@app.route("/api/logs")
@login_required
@admin_required
def api_logs():
    username_filter = request.args.get("username", "")
    logs = _load_logs()
    if username_filter:
        logs = [l for l in logs if l["username"] == username_filter]
    return jsonify(list(reversed(logs[-500:])))

# ─── Dashboard page ───────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard_page():
    users = _load_users()
    if users.get(session["user"], {}).get("role") != "admin":
        return redirect(url_for("index"))
    return render_template("dashboard.html")

# ─── App routes ───────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def index():
    return render_template("index.html", leagues=LEAGUES)

@app.route("/api/leagues")
@login_required
def api_leagues():
    return jsonify(LEAGUES)

@app.route("/api/predictions", methods=["POST"])
@login_required
def api_predictions():
    data = request.get_json()
    users = _load_users()
    u = users.get(session["user"], {})
    api_key = u.get("api_key") or data.get("api_key", "").strip()
    league_ids = data.get("leagues", [])
    top_only = data.get("top_only", False)
    if not api_key:
        return jsonify({"success": False, "error": "Clé API manquante"}), 400
    if not league_ids:
        return jsonify({"success": False, "error": "Aucune ligue sélectionnée"}), 400
    if len(league_ids) > 5:
        return jsonify({"success": False, "error": "Maximum 5 ligues"}), 400
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        ua = request.headers.get("User-Agent", "")
        _log(session["user"], "prediction", f"football: {','.join(league_ids)}", ip=ip, ua=ua)
        games = fetch_all_games(api_key, league_ids, top_only=top_only)
        return jsonify({"success": True, "games": games, "count": len(games)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/combiner", methods=["POST"])
@login_required
def api_combiner():
    data = request.get_json()
    users = _load_users()
    u = users.get(session["user"], {})
    api_key = u.get("api_key") or data.get("api_key", "").strip()
    league_ids = data.get("leagues", [])
    target_odds = float(data.get("target_odds", 5.0))
    top_only = data.get("top_only", False)
    safe_range_keys = data.get("safe_ranges", ["range1", "range2", "range3"])
    risky_range_keys = data.get("risky_ranges", ["range1", "range2", "range3"])
    safe_ranges = [SAFE_RANGES[k] for k in safe_range_keys if k in SAFE_RANGES]
    risky_ranges = [RISKY_RANGES[k] for k in risky_range_keys if k in RISKY_RANGES]
    if not safe_ranges: safe_ranges = [(1.15, 1.40)]
    if not risky_ranges: risky_ranges = [(1.40, 2.50)]
    if not api_key or not league_ids:
        return jsonify({"success": False, "error": "Données manquantes"}), 400
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        ua = request.headers.get("User-Agent", "")
        _log(session["user"], "combiner", f"cote:{target_odds} ligues:{','.join(league_ids)}", ip=ip, ua=ua)
        games = fetch_all_games(api_key, league_ids)
        if not games:
            return jsonify({"success": False, "error": "Aucun match trouvé pour ces ligues aujourd'hui"}), 404
        result = generate_combiners(games, target_odds, safe_ranges=safe_ranges, risky_ranges=risky_ranges, top_only=top_only)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/sports/nba_leagues")
@login_required
def api_nba_leagues():
    return jsonify(NBA_LEAGUES)

@app.route("/api/sports/nhl_leagues")
@login_required
def api_nhl_leagues():
    return jsonify(NHL_LEAGUES)

@app.route("/api/sports/nba", methods=["POST"])
@login_required
def api_nba():
    data = request.get_json()
    users = _load_users()
    u = users.get(session["user"], {})
    api_key = u.get("api_key") or data.get("api_key", "").strip()
    league_ids = data.get("leagues", [])
    if not api_key:
        return jsonify({"success": False, "error": "Clé API manquante"}), 400
    if not league_ids:
        return jsonify({"success": False, "error": "Aucune ligue sélectionnée"}), 400
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        ua = request.headers.get("User-Agent", "")
        _log(session["user"], "prediction", f"nba: {','.join(league_ids)}", ip=ip, ua=ua)
        games = fetch_nba_games(api_key, league_ids)
        return jsonify({"success": True, "games": games, "count": len(games)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/sports/nhl", methods=["POST"])
@login_required
def api_nhl():
    data = request.get_json()
    users = _load_users()
    u = users.get(session["user"], {})
    api_key = u.get("api_key") or data.get("api_key", "").strip()
    league_ids = data.get("leagues", [])
    if not api_key:
        return jsonify({"success": False, "error": "Clé API manquante"}), 400
    if not league_ids:
        return jsonify({"success": False, "error": "Aucune ligue sélectionnée"}), 400
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        ua = request.headers.get("User-Agent", "")
        _log(session["user"], "prediction", f"nhl: {','.join(league_ids)}", ip=ip, ua=ua)
        games = fetch_nhl_games(api_key, league_ids)
        return jsonify({"success": True, "games": games, "count": len(games)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("\n⚽ Fatos Pronostic — Enèji")
    print("➜  Ouvre http://localhost:5000\n")
    app.run(debug=True, port=5000)
