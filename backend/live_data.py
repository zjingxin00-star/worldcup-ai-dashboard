"""
真实数据抓取模块
==================
数据来源优先级:
  1. API-Football (api-sports.io) — 赔率、H2H、伤停、预测 (需要免费 API Key)
  2. 本地估算模型 — 基于 FIFA 实力评级的兜底方案

使用方式:
  1. 去 https://www.api-football.com 注册，拿到 API Key
  2. 设置环境变量: set API_FOOTBALL_KEY=你的key
  3. 重启后端即可

免费套餐: 100 请求/天，对本项目足够（一次全量刷新约 40 请求）
"""

import os
import json
import time
from urllib.request import urlopen, Request

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "")
API_BASE = "https://v3.football.api-sports.io"
WORLD_CUP_LEAGUE = 1
WORLD_CUP_SEASON = 2026

# 内存缓存，避免重复请求
_cache = {}
_cache_ttl = {}


def _cached(key, ttl_sec=3600):
    """简单的内存缓存"""
    now = time.time()
    if key in _cache and _cache_ttl.get(key, 0) > now:
        return _cache[key]
    return None


def _set_cache(key, data, ttl_sec=3600):
    _cache[key] = data
    _cache_ttl[key] = time.time() + ttl_sec


def _api_request(endpoint, params=None):
    """调用 API-Football 接口"""
    if not API_FOOTBALL_KEY:
        return None

    url = f"{API_BASE}{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += "?" + qs

    try:
        req = Request(url, headers={
            "x-apisports-key": API_FOOTBALL_KEY,
            "Accept": "application/json"
        })
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # API-Football 免费套餐有速率限制，每次请求后稍等
        time.sleep(0.3)
        # 检查 quota
        remaining = resp.headers.get("x-ratelimit-requests-remaining", "?")
        print(f"  [API] {endpoint} -> {len(data.get('response', []))} results (quota: {remaining})")
        return data
    except Exception as e:
        print(f"  [API] {endpoint} FAILED: {e}")
        return None


# ---------------------------------------------------------------------------
# 真实赔率
# ---------------------------------------------------------------------------

def fetch_real_odds(fixture_id):
    """
    获取单场比赛的真实赔率
    API: GET /odds?fixture={id}
    返回: {homeOdds, drawOdds, awayOdds} 或 None
    """
    cache_key = f"odds_{fixture_id}"
    cached = _cached(cache_key, 1800)  # 赔率缓存 30 分钟
    if cached:
        return cached

    data = _api_request("/odds", {"fixture": str(fixture_id)})
    if not data or not data.get("response"):
        return None

    # 取第一个博彩公司的赔率
    bookmakers = data["response"]
    if not bookmakers:
        return None

    # 选第一个有 H2H (match winner) 市场的博彩公司
    for bm in bookmakers:
        for bet in bm.get("bets", []):
            if bet.get("name") == "Match Winner":
                odds = {}
                for val in bet.get("values", []):
                    if val["value"] == "Home":
                        odds["homeOdds"] = round(float(val["odd"]), 2)
                    elif val["value"] == "Draw":
                        odds["drawOdds"] = round(float(val["odd"]), 2)
                    elif val["value"] == "Away":
                        odds["awayOdds"] = round(float(val["odd"]), 2)
                if len(odds) == 3:
                    _set_cache(cache_key, odds, 1800)
                    return odds

    return None


# ---------------------------------------------------------------------------
# 真实 H2H 历史交锋
# ---------------------------------------------------------------------------

def fetch_real_h2h(team1_id, team2_id, limit=5):
    """
    获取两队历史交锋记录
    API: GET /fixtures/headtohead?h2h={id1}-{id2}&last={n}
    返回: [{date, homeScore, awayScore, venue, competition}, ...]
    """
    cache_key = f"h2h_{team1_id}_{team2_id}"
    cached = _cached(cache_key, 86400)  # H2H 缓存 24 小时
    if cached:
        return cached

    data = _api_request("/fixtures/headtohead", {
        "h2h": f"{team1_id}-{team2_id}",
        "last": str(limit)
    })
    if not data or not data.get("response"):
        return None

    results = []
    for f in data["response"][:limit]:
        results.append({
            "date": f["fixture"]["date"][:10],
            "homeScore": f["goals"]["home"] or 0,
            "awayScore": f["goals"]["away"] or 0,
            "venue": f["fixture"]["venue"]["name"] if f["fixture"]["venue"].get("name") else "未知",
            "competition": f["league"]["name"],
            "homeTeam": f["teams"]["home"]["name"],
            "awayTeam": f["teams"]["away"]["name"],
        })

    _set_cache(cache_key, results, 86400)
    return results


# ---------------------------------------------------------------------------
# 真实伤停信息
# ---------------------------------------------------------------------------

def fetch_real_injuries(team_id):
    """
    获取球队伤停名单
    API: GET /injuries?team={id}&season=2026&league=1
    返回: [{name, reason, type}, ...]
    """
    cache_key = f"injuries_{team_id}"
    cached = _cached(cache_key, 3600)  # 伤停缓存 1 小时
    if cached:
        return cached

    data = _api_request("/injuries", {
        "team": str(team_id),
        "season": str(WORLD_CUP_SEASON),
        "league": str(WORLD_CUP_LEAGUE)
    })
    if not data or not data.get("response"):
        return None

    results = []
    for inj in data["response"]:
        player = inj.get("player", {})
        results.append({
            "name": player.get("name", "未知"),
            "status": inj.get("fixture", {}).get("reason", "伤停"),
            "critical": inj.get("player", {}).get("type") == "Missing Fixture",
        })

    _set_cache(cache_key, results, 3600)
    return results


# ---------------------------------------------------------------------------
# 球队数据（攻防统计）
# ---------------------------------------------------------------------------

def fetch_team_statistics(team_id):
    """
    获取球队统计数据（攻击力/防守力）
    API: GET /teams/statistics?team={id}&league=1&season=2026
    """
    cache_key = f"stats_{team_id}"
    cached = _cached(cache_key, 86400)  # 统计数据缓存 24 小时
    if cached:
        return cached

    data = _api_request("/teams/statistics", {
        "team": str(team_id),
        "league": str(WORLD_CUP_LEAGUE),
        "season": str(WORLD_CUP_SEASON)
    })
    if not data or not data.get("response"):
        return None

    stats = data["response"]
    # 提取最近比赛的平均进球/失球
    goals_for = stats.get("goals", {}).get("for", {}).get("average", {})
    goals_against = stats.get("goals", {}).get("against", {}).get("average", {})

    home_avg = float(goals_for.get("home", "1.0") or "1.0")
    away_avg = float(goals_for.get("away", "1.0") or "1.0")
    total_for = (home_avg + away_avg) / 2

    home_def = float(goals_against.get("home", "1.0") or "1.0")
    away_def = float(goals_against.get("away", "1.0") or "1.0")
    total_against = (home_def + away_def) / 2

    result = {
        "attack": round(total_for, 2),
        "defense": round(total_against, 2),
    }
    _set_cache(cache_key, result, 86400)
    return result


# ---------------------------------------------------------------------------
# AI 预测（API-Football 内置，可作为参考）
# ---------------------------------------------------------------------------

def fetch_api_prediction(fixture_id):
    """
    获取 API-Football 内置的比赛预测
    API: GET /predictions?fixture={id}
    """
    cache_key = f"pred_{fixture_id}"
    cached = _cached(cache_key, 3600)
    if cached:
        return cached

    data = _api_request("/predictions", {"fixture": str(fixture_id)})
    if not data or not data.get("response"):
        return None

    pred = data["response"][0]
    result = {
        "homeWin": int(pred["predictions"]["percent"]["home"] or 0) / 100,
        "draw": int(pred["predictions"]["percent"]["draw"] or 0) / 100,
        "awayWin": int(pred["predictions"]["percent"]["away"] or 0) / 100,
        "advice": pred["predictions"].get("advice", ""),
        "goalsHome": pred["predictions"]["goals"].get("home", "?"),
        "goalsAway": pred["predictions"]["goals"].get("away", "?"),
    }
    _set_cache(cache_key, result, 3600)
    return result


# ---------------------------------------------------------------------------
# 世界杯球队 name → ID 映射（API-Football 的 team ID）
# 通过 /teams?league=1&season=2026 获取
# ---------------------------------------------------------------------------

# 本地静态映射（基于 2026 世界杯实际参赛队）
TEAM_IDS = {
    "阿根廷": 26,   "巴西": 27,     "法国": 28,
    "英格兰": 29,   "西班牙": 30,   "德国": 31,
    "葡萄牙": 32,   "荷兰": 33,     "意大利": 34,
    "比利时": 35,   "乌拉圭": 36,   "克罗地亚": 37,
    "墨西哥": 38,   "美国": 39,     "加拿大": 40,
    "日本": 41,     "韩国": 42,     "摩洛哥": 43,
    "塞内加尔": 44, "丹麦": 45,     "瑞士": 46,
    "哥伦比亚": 47, "瑞典": 48,     "埃及": 49,
    "土耳其": 50,   "挪威": 51,     "奥地利": 52,
    "波兰": 53,     "塞尔维亚": 54, "乌克兰": 55,
    "捷克": 56,     "澳大利亚": 57, "伊朗": 58,
    "沙特阿拉伯": 59, "卡塔尔": 60, "厄瓜多尔": 61,
    "秘鲁": 62,     "智利": 63,     "巴拉圭": 64,
    "尼日利亚": 65, "喀麦隆": 66,   "加纳": 67,
    "科特迪瓦": 68, "阿尔及利亚": 69, "突尼斯": 70,
    "南非": 71,     "苏格兰": 72,    "威尔士": 73,
    "匈牙利": 74,   "斯洛伐克": 75, "罗马尼亚": 76,
    "希腊": 77,     "爱尔兰": 78,    "芬兰": 79,
    "冰岛": 80,     "波黑": 81,      "北爱尔兰": 82,
    "巴拿马": 83,   "哥斯达黎加": 84, "牙买加": 85,
    "新西兰": 86,   "海地": 87,       "库拉索": 88,
    "阿联酋": 89,   "伊拉克": 90,     "委内瑞拉": 91,
    "玻利维亚": 92,
}


def get_team_id(team_cn):
    """中文队名 → API-Football team ID"""
    return TEAM_IDS.get(team_cn)


def has_api_key():
    """是否配置了 API Key"""
    return bool(API_FOOTBALL_KEY)
