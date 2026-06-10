"""
球队近期战绩统计
==================
从 API-Football 抓取每队最近 10 场比赛的进球/失球数据
用于泊松分布模型的真实攻防参数计算
"""
import json, os, time
from urllib.request import urlopen, Request

KEY = os.environ.get("API_FOOTBALL_KEY", "4b2c3b320e6977181410dca62d117006")
HEADERS = {"x-apisports-key": KEY}
STATS_FILE = os.path.join(os.path.dirname(__file__), "team_recent_stats.json")

# 先加载已有的缓存
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        STATS_CACHE = json.loads(f.read())
else:
    STATS_CACHE = {}

def save_cache():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(STATS_CACHE, ensure_ascii=False, indent=2))

def fetch_team_recent(team_id, team_name, count=10):
    """获取一支球队最近 N 场比赛的进球数据"""
    cache_key = str(team_id)
    if cache_key in STATS_CACHE and STATS_CACHE[cache_key].get("matches", 0) >= count:
        return STATS_CACHE[cache_key]

    # 搜索最近几个赛季的 fixtures
    all_fixtures = []
    for season in [2026, 2025, 2024]:
        if len(all_fixtures) >= count:
            break
        try:
            url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season={season}"
            req = Request(url, headers=HEADERS)
            resp = urlopen(req, timeout=15)
            data = json.loads(resp.read().decode("utf-8"))
            fixtures = data.get("response", [])
            for f in fixtures:
                home = f["teams"]["home"]
                away = f["teams"]["away"]
                goals_home = f["goals"]["home"]
                goals_away = f["goals"]["away"]
                if goals_home is None or goals_away is None:
                    continue  # skip unplayed matches
                all_fixtures.append({
                    "date": f["fixture"]["date"][:10],
                    "home": home["name"],
                    "away": away["name"],
                    "homeId": home["id"],
                    "awayId": away["id"],
                    "homeGoals": goals_home,
                    "awayGoals": goals_away,
                    "league": f["league"]["name"],
                })
            # API 限流: 每次请求间隔
            time.sleep(0.4)
        except Exception as e:
            print(f"  [team_stats] season={season} for {team_name} (ID={team_id}): {e}")
            # 429 Too Many Requests → 停更久
            if "429" in str(e) or "Too Many" in str(e):
                time.sleep(5)

    # 取最近 N 场
    all_fixtures.sort(key=lambda x: x["date"], reverse=True)
    recent = all_fixtures[:count]

    if not recent:
        return None

    # 计算场均进球 / 失球 — 用 Team ID 精确匹配主客场
    goals_for = 0
    goals_against = 0
    for f in recent:
        # fixtures 返回中有 teams.home.id 和 teams.away.id
        home_id = f.get("homeId", 0)
        away_id = f.get("awayId", 0)
        if home_id == team_id:
            goals_for += f["homeGoals"]
            goals_against += f["awayGoals"]
        elif away_id == team_id:
            goals_for += f["awayGoals"]
            goals_against += f["homeGoals"]
        else:
            # 回退到名字匹配
            if team_name.lower() in f["home"].lower():
                goals_for += f["homeGoals"]
                goals_against += f["awayGoals"]
            else:
                goals_for += f["awayGoals"]
                goals_against += f["homeGoals"]

    n = len(recent)
    result = {
        "team": team_name,
        "matches": n,
        "goalsFor": round(goals_for / n, 2),
        "goalsAgainst": round(goals_against / n, 2),
        "recent": recent[:5],  # 最近 5 场明细
    }
    STATS_CACHE[cache_key] = result
    save_cache()
    print(f"  [team_stats] {team_name}: {n} matches, GF={result['goalsFor']}, GA={result['goalsAgainst']}")
    return result


def get_team_stats(team_id, team_name):
    """获取球队统计数据（优先缓存）"""
    cache_key = str(team_id)
    if cache_key in STATS_CACHE and STATS_CACHE[cache_key].get("matches", 0) >= 5:
        return STATS_CACHE[cache_key]
    return fetch_team_recent(team_id, team_name)


def build_all_stats():
    """为所有已知 ID 的球队拉取统计数据"""
    from live_data import TEAM_IDS

    total = sum(1 for tid in TEAM_IDS.values() if tid > 0)
    done = 0
    for name_cn, team_id in TEAM_IDS.items():
        if team_id <= 0:
            continue
        key = str(team_id)
        if key in STATS_CACHE and STATS_CACHE[key].get("matches", 0) >= 10:
            continue  # 已有足够数据
        fetch_team_recent(team_id, name_cn)
        done += 1
        if done >= 8:  # 每次限跑 8 支球队，避免超 API 限额
            print(f"[team_stats] Paused after {done} teams (API quota conservation)")
            break

    print(f"[team_stats] Total cached: {len(STATS_CACHE)} teams")
    save_cache()


if __name__ == "__main__":
    build_all_stats()
    # 打印当前缓存的球队
    print("\n=== Cached team stats ===")
    for tid, stats in sorted(STATS_CACHE.items()):
        print(f"  ID={tid}: {stats['team']} | GF={stats['goalsFor']} GA={stats['goalsAgainst']} ({stats['matches']} matches)")
