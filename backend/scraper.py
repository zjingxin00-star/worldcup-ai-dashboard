"""
2026 世界杯真实数据爬虫
========================
数据来源: OpenFootball/worldcup.json (GitHub, 公共领域)
GitHub: https://github.com/openfootball/worldcup.json
原始 JSON: https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json

- 104 场完整赛程（48 队，12 小组 A-L）
- 无 API Key 要求，数据公共领域
"""

import json
import math
import os
import random
from urllib.request import urlopen, Request

# 加载手工采集的真实 H2H 数据库
_H2H_DB = {}
_H2H_DB_PATH = os.path.join(os.path.dirname(__file__), "h2h_database.json")
try:
    if os.path.exists(_H2H_DB_PATH):
        with open(_H2H_DB_PATH, "r", encoding="utf-8") as f:
            _H2H_DB = json.loads(f.read())
        print(f"[scraper] Loaded H2H database: {len(_H2H_DB)} matchups")
except Exception as e:
    print(f"[scraper] H2H database load failed: {e}")

OPENFOOTBALL_URL = (
    "https://raw.githubusercontent.com/openfootball/worldcup.json/"
    "master/2026/worldcup.json"
)
# GitHub API 备用（raw 域名偶尔 DNS 失败）
OPENFOOTBALL_FALLBACK = (
    "https://api.github.com/repos/openfootball/worldcup.json/"
    "contents/2026/worldcup.json"
)

# ---------------------------------------------------------------------------
# 队名中英文映射 (48 支参赛队)
# ---------------------------------------------------------------------------
TEAM_NAME_CN = {
    "Mexico": "墨西哥",          "South Africa": "南非",
    "South Korea": "韩国",       "Czech Republic": "捷克",
    "Canada": "加拿大",           "Bosnia & Herzegovina": "波黑",
    "Qatar": "卡塔尔",            "Switzerland": "瑞士",
    "Brazil": "巴西",             "Morocco": "摩洛哥",
    "Haiti": "海地",              "Scotland": "苏格兰",
    "USA": "美国",               "Paraguay": "巴拉圭",
    "Australia": "澳大利亚",       "Turkey": "土耳其",
    "Germany": "德国",            "Curaçao": "库拉索",
    "Ivory Coast": "科特迪瓦",     "Ecuador": "厄瓜多尔",
    "Netherlands": "荷兰",        "Japan": "日本",
    "Sweden": "瑞典",             "Tunisia": "突尼斯",
    "France": "法国",             "Denmark": "丹麦",
    "Argentina": "阿根廷",        "Saudi Arabia": "沙特阿拉伯",
    "England": "英格兰",          "Norway": "挪威",
    "Spain": "西班牙",            "Portugal": "葡萄牙",
    "Italy": "意大利",            "United Arab Emirates": "阿联酋",
    "Belgium": "比利时",          "Egypt": "埃及",
    "Uruguay": "乌拉圭",          "Iran": "伊朗",
    "Colombia": "哥伦比亚",       "New Zealand": "新西兰",
    "Chile": "智利",              "Panama": "巴拿马",
    "Croatia": "克罗地亚",        "Nigeria": "尼日利亚",
    "Peru": "秘鲁",               "Iraq": "伊拉克",
    "Senegal": "塞内加尔",        "Costa Rica": "哥斯达黎加",
    "Austria": "奥地利",          "Cameroon": "喀麦隆",
    "Algeria": "阿尔及利亚",      "Ukraine": "乌克兰",
    "Poland": "波兰",             "Serbia": "塞尔维亚",
    "Greece": "希腊",             "Venezuela": "委内瑞拉",
    "Romania": "罗马尼亚",        "Mali": "马里",
    "Slovakia": "斯洛伐克",       "Jamaica": "牙买加",
    "Hungary": "匈牙利",          "Bolivia": "玻利维亚",
    "Wales": "威尔士",            "Finland": "芬兰",
    "Russia": "俄罗斯",           "Ireland": "爱尔兰",
    "Ghana": "加纳",              "Burkina Faso": "布基纳法索",
    "DR Congo": "刚果(金)",       "Slovenia": "斯洛文尼亚",
    "Guinea": "几内亚",           "North Macedonia": "北马其顿",
    "Albania": "阿尔巴尼亚",      "South Sudan": "南苏丹",
    "Iceland": "冰岛",            "Zambia": "赞比亚",
    "Cape Verde": "佛得角",       "Honduras": "洪都拉斯",
    "El Salvador": "萨尔瓦多",    "Bulgaria": "保加利亚",
    "Montenegro": "黑山",         "Northern Ireland": "北爱尔兰",
    "Kosovo": "科索沃",           "Georgia": "格鲁吉亚",
    "Luxembourg": "卢森堡",       "Equatorial Guinea": "赤道几内亚",
    "Gabon": "加蓬",              "Angola": "安哥拉",
    "Benin": "贝宁",              "Uganda": "乌干达",
    "Madagascar": "马达加斯加",    "Kenya": "肯尼亚",
    "Mozambique": "莫桑比克",     "Congo": "刚果(布)",
    "Togo": "多哥",               "Guinea-Bissau": "几内亚比绍",
    "Namibia": "纳米比亚",         "Mauritania": "毛里塔尼亚",
    "Libya": "利比亚",             "Niger": "尼日尔",
    "Zimbabwe": "津巴布韦",        "Malawi": "马拉维",
    "Sudan": "苏丹",               "Tanzania": "坦桑尼亚",
    "Rwanda": "卢旺达",            "Ethiopia": "埃塞俄比亚",
    "Eswatini": "斯威士兰",        "Lesotho": "莱索托",
    "Botswana": "博茨瓦纳",        "Liberia": "利比里亚",
    "Sierra Leone": "塞拉利昂",    "Central African Republic": "中非",
    "Burundi": "布隆迪",           "Gambia": "冈比亚",
    "Mauritius": "毛里求斯",       "Comoros": "科摩罗",
    "São Tomé and Príncipe": "圣多美和普林西比",
    "Seychelles": "塞舌尔",       "Chad": "乍得",
    "Djibouti": "吉布提",         "Somalia": "索马里",
    "Eritrea": "厄立特里亚",
}

# 国旗 emoji 映射（国家代码 → 国旗）
COUNTRY_FLAG = {
    "MEX": "🇲🇽", "RSA": "🇿🇦", "KOR": "🇰🇷", "CZE": "🇨🇿",
    "CAN": "🇨🇦", "BIH": "🇧🇦", "QAT": "🇶🇦", "SUI": "🇨🇭",
    "BRA": "🇧🇷", "MAR": "🇲🇦", "HAI": "🇭🇹", "SCO": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA": "🇺🇸", "PAR": "🇵🇾", "AUS": "🇦🇺", "TUR": "🇹🇷",
    "GER": "🇩🇪", "CUW": "🇨🇼", "CIV": "🇨🇮", "ECU": "🇪🇨",
    "NED": "🇳🇱", "JPN": "🇯🇵", "SWE": "🇸🇪", "TUN": "🇹🇳",
    "FRA": "🇫🇷", "DEN": "🇩🇰", "ARG": "🇦🇷", "KSA": "🇸🇦",
    "ENG": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "NOR": "🇳🇴", "ESP": "🇪🇸", "POR": "🇵🇹",
    "ITA": "🇮🇹", "UAE": "🇦🇪", "BEL": "🇧🇪", "EGY": "🇪🇬",
    "URU": "🇺🇾", "IRN": "🇮🇷", "COL": "🇨🇴", "NZL": "🇳🇿",
    "CHI": "🇨🇱", "PAN": "🇵🇦", "CRO": "🇭🇷", "NGA": "🇳🇬",
    "PER": "🇵🇪", "IRQ": "🇮🇶", "SEN": "🇸🇳", "CRC": "🇨🇷",
    "AUT": "🇦🇹", "CMR": "🇨🇲", "ALG": "🇩🇿", "UKR": "🇺🇦",
    "POL": "🇵🇱", "SRB": "🇷🇸", "GRE": "🇬🇷", "VEN": "🇻🇪",
    "ROU": "🇷🇴", "MLI": "🇲🇱", "SVK": "🇸🇰", "JAM": "🇯🇲",
    "HUN": "🇭🇺", "BOL": "🇧🇴", "WAL": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "FIN": "🇫🇮",
}

# 球队 FIFA 实力评级 (1-10，越高越强)
TEAM_STRENGTH = {
    "阿根廷": 9.2, "巴西": 9.0, "法国": 9.1, "英格兰": 8.8,
    "西班牙": 8.7, "德国": 8.5, "葡萄牙": 8.6, "荷兰": 8.4,
    "意大利": 8.3, "比利时": 8.0, "乌拉圭": 7.8, "克罗地亚": 7.7,
    "哥伦比亚": 7.5, "摩洛哥": 7.3, "美国": 7.2, "墨西哥": 7.0,
    "日本": 7.4, "韩国": 6.8, "塞内加尔": 7.0, "丹麦": 7.5,
    "瑞士": 7.2, "奥地利": 6.8, "瑞典": 6.9, "挪威": 7.6,
    "土耳其": 6.5, "埃及": 6.2, "尼日利亚": 6.5, "喀麦隆": 6.0,
    "加拿大": 6.5, "澳大利亚": 6.3, "伊朗": 6.0, "沙特阿拉伯": 5.5,
    "卡塔尔": 5.0, "厄瓜多尔": 6.5, "巴拉圭": 5.8, "智利": 6.7,
    "秘鲁": 6.0, "威尔士": 6.3, "波兰": 6.8, "塞尔维亚": 6.7,
    "乌克兰": 6.5, "苏格兰": 6.2, "捷克": 6.5, "匈牙利": 6.0,
    "斯洛伐克": 5.8, "罗马尼亚": 5.5, "希腊": 5.8, "爱尔兰": 5.3,
    "芬兰": 5.0, "挪威": 7.6, "冰岛": 5.0, "北爱尔兰": 4.8,
    "阿尔巴尼亚": 4.5, "格鲁吉亚": 4.5, "保加利亚": 4.2,
    "斯洛文尼亚": 5.2, "波黑": 5.0, "北马其顿": 4.0,
    "科索沃": 3.5, "卢森堡": 3.0, "科特迪瓦": 6.8, "加纳": 6.3,
    "阿尔及利亚": 6.2, "马里": 5.5, "布基纳法索": 5.0,
    "刚果(金)": 4.8, "南非": 5.2, "几内亚": 4.5, "赞比亚": 4.0,
    "佛得角": 3.8, "突尼斯": 6.0, "海地": 3.5, "库拉索": 3.0,
    "阿联酋": 4.5, "新西兰": 4.2, "巴拿马": 4.5, "哥斯达黎加": 5.5,
    "牙买加": 4.8, "洪都拉斯": 4.0, "萨尔瓦多": 3.5,
    "委内瑞拉": 5.5, "玻利维亚": 4.5, "伊拉克": 4.0, "伊朗": 6.0,
}


def _cn(name_en: str) -> str:
    """英文队名 → 中文队名"""
    return TEAM_NAME_CN.get(name_en, name_en)


def _flag(name_en: str) -> str:
    """英文队名 → 国旗 emoji（简易映射，基于常见参赛队）"""
    flag_map = {
        "Mexico": "🇲🇽", "South Africa": "🇿🇦", "South Korea": "🇰🇷",
        "Czech Republic": "🇨🇿", "Canada": "🇨🇦", "Bosnia & Herzegovina": "🇧🇦",
        "Qatar": "🇶🇦", "Switzerland": "🇨🇭", "Brazil": "🇧🇷",
        "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "USA": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺",
        "Turkey": "🇹🇷", "Germany": "🇩🇪", "Curaçao": "🇨🇼",
        "Ivory Coast": "🇨🇮", "Ecuador": "🇪🇨", "Netherlands": "🇳🇱",
        "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
        "France": "🇫🇷", "Denmark": "🇩🇰", "Argentina": "🇦🇷",
        "Saudi Arabia": "🇸🇦", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Norway": "🇳🇴",
        "Spain": "🇪🇸", "Portugal": "🇵🇹", "Italy": "🇮🇹",
        "United Arab Emirates": "🇦🇪", "Belgium": "🇧🇪", "Egypt": "🇪🇬",
        "Uruguay": "🇺🇾", "Iran": "🇮🇷", "Colombia": "🇨🇴",
        "New Zealand": "🇳🇿", "Chile": "🇨🇱", "Panama": "🇵🇦",
        "Croatia": "🇭🇷", "Nigeria": "🇳🇬", "Peru": "🇵🇪",
        "Iraq": "🇮🇶", "Senegal": "🇸🇳", "Costa Rica": "🇨🇷",
        "Austria": "🇦🇹", "Cameroon": "🇨🇲", "Algeria": "🇩🇿",
        "Ukraine": "🇺🇦", "Poland": "🇵🇱", "Serbia": "🇷🇸",
        "Greece": "🇬🇷", "Venezuela": "🇻🇪", "Romania": "🇷🇴",
        "Mali": "🇲🇱", "Slovakia": "🇸🇰", "Jamaica": "🇯🇲",
        "Hungary": "🇭🇺", "Bolivia": "🇧🇴", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
        "Finland": "🇫🇮", "Ghana": "🇬🇭", "Russia": "🇷🇺",
        "Ireland": "🇮🇪", "Burkina Faso": "🇧🇫", "DR Congo": "🇨🇩",
        "Slovenia": "🇸🇮", "Guinea": "🇬🇳", "North Macedonia": "🇲🇰",
        "Albania": "🇦🇱", "South Sudan": "🇸🇸", "Iceland": "🇮🇸",
        "Zambia": "🇿🇲", "Cape Verde": "🇨🇻", "Honduras": "🇭🇳",
        "El Salvador": "🇸🇻", "Bulgaria": "🇧🇬", "Montenegro": "🇲🇪",
        "Northern Ireland": "🏴󠁧󠁢󠁮󠁩󠁲󠁿", "Kosovo": "🇽🇰", "Georgia": "🇬🇪",
        "Luxembourg": "🇱🇺", "Equatorial Guinea": "🇬🇶",
        "Gabon": "🇬🇦", "Angola": "🇦🇴", "Benin": "🇧🇯", "Uganda": "🇺🇬",
        "Congo": "🇨🇬", "Togo": "🇹🇬",
    }
    return flag_map.get(name_en, "🏳️")


def _strength(team_cn: str) -> float:
    """获取球队实力评级，未知球队默认 5.0"""
    return TEAM_STRENGTH.get(team_cn, 5.0)


def _calc_odds(home_strength: float, away_strength: float) -> dict:
    """
    基于球队实力差计算模拟赔率
    实力差越大 → 强队赔率越低 → 弱队赔率越高
    加入庄家抽水 (margin ~6%)
    """
    diff = (home_strength - away_strength) / 3.0  # 实力差归一化
    home_fair = 1.0 / (0.33 + 0.22 * diff + 0.12 * diff * diff)
    draw_fair = 3.0 + abs(diff) * 0.8
    away_fair = 1.0 / (0.33 - 0.22 * diff + 0.12 * diff * diff)

    # 限制范围
    home_fair = max(1.15, min(12.0, home_fair))
    away_fair = max(1.15, min(12.0, away_fair))
    draw_fair = max(2.50, min(5.50, draw_fair))

    # 庄家抽水 6%
    margin = 0.94
    return {
        "homeOdds": round(home_fair * margin, 2),
        "drawOdds": round(draw_fair * margin, 2),
        "awayOdds": round(away_fair * margin, 2),
    }


def _calc_attack_defense(strength: float) -> tuple:
    """
    基于实力评级计算攻击力 & 防守力
    强队: 攻击高(1.5-2.5), 防守低(0.3-0.8)
    弱队: 攻击低(0.5-1.2), 防守高(1.0-1.8)
    """
    attack = 0.6 + strength * 0.18
    defense = 2.0 - strength * 0.18
    # 加入少许随机波动
    attack += random.uniform(-0.15, 0.15)
    defense += random.uniform(-0.15, 0.15)
    return round(max(0.3, attack), 2), round(max(0.2, defense), 2)


def _group_label(group_name: str) -> str:
    """Group A → A组"""
    return group_name.replace("Group ", "") + "组"


def _parse_utc_time(date_str: str, time_str: str) -> str:
    """
    将 OpenFootball 的日期+UTC时间 转换为北京时间字符串
    例如: "2026-06-11" + "13:00 UTC-6" → "2026-06-12 03:00"
    """
    try:
        parts = date_str.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

        # 解析 UTC 偏移
        tparts = time_str.split(" ")
        hm = tparts[0].split(":")
        hour, minute = int(hm[0]), int(hm[1])

        utc_part = tparts[1] if len(tparts) > 1 else "UTC+0"
        offset_str = utc_part.replace("UTC", "")
        offset_hours = int(offset_str) if offset_str else 0

        # UTC → 北京时间 (UTC+8)
        beijing_hour = hour - offset_hours + 8

        # 处理跨日
        if beijing_hour >= 24:
            beijing_hour -= 24
            day += 1
        elif beijing_hour < 0:
            beijing_hour += 24
            day -= 1

        return f"{year:04d}-{month:02d}-{day:02d} {beijing_hour:02d}:{minute:02d}"
    except Exception:
        return f"{date_str} {time_str}"


def fetch_real_matches(limit: int = 20) -> list:
    """
    从 OpenFootball 抓取真实 2026 世界杯赛程
    返回前 `limit` 场比赛（按日期排序，优先小组赛第一轮）
    """
    raw_data = None
    for url in [OPENFOOTBALL_URL, OPENFOOTBALL_FALLBACK]:
        try:
            hdrs = {"User-Agent": "WorldCupDashboard/1.0"}
            if "api.github.com" in url:
                hdrs["Accept"] = "application/vnd.github.v3.raw"
            req = Request(url, headers=hdrs)
            with urlopen(req, timeout=20) as resp:
                raw_data = resp.read().decode("utf-8")
            break
        except Exception as e:
            print(f"[scraper] {url[:50]}... failed: {e}")

    if not raw_data:
        print("[scraper] All OpenFootball sources failed")
        return []

    data = json.loads(raw_data)

    matches_raw = data.get("matches", [])
    if not matches_raw:
        return []

    # 过滤掉淘汰赛占位符（team1 包含 "W" 或 "L" 开头的）
    real_matches = [
        m for m in matches_raw
        if not (m.get("team1", "").startswith(("W", "L", "R")))
        and not (m.get("team2", "").startswith(("W", "L", "R")))
    ]

    results = []
    for i, m in enumerate(real_matches[:limit]):
        home_en = m.get("team1", "Unknown")
        away_en = m.get("team2", "Unknown")
        home_cn = _cn(home_en)
        away_cn = _cn(away_en)
        group = _group_label(m.get("group", "?组"))
        date_str = m.get("date", "")
        time_str = m.get("time", "")

        home_str = _strength(home_cn)
        away_str = _strength(away_cn)
        odds = _calc_odds(home_str, away_str)

        # 优先使用真实近期数据，否则用实力估算
        try:
            from team_stats import STATS_CACHE
            from live_data import get_team_id
            home_id = get_team_id(home_cn)
            away_id = get_team_id(away_cn)
            home_stats = STATS_CACHE.get(str(home_id)) if home_id else None
            away_stats = STATS_CACHE.get(str(away_id)) if away_id else None
            if home_stats and home_stats.get('matches', 0) >= 5:
                home_atk = home_stats['goalsFor']
                home_def = home_stats['goalsAgainst']
            else:
                home_atk, home_def = _calc_attack_defense(home_str)
            if away_stats and away_stats.get('matches', 0) >= 5:
                away_atk = away_stats['goalsFor']
                away_def = away_stats['goalsAgainst']
            else:
                away_atk, away_def = _calc_attack_defense(away_str)
        except Exception:
            home_atk, home_def = _calc_attack_defense(home_str)
            away_atk, away_def = _calc_attack_defense(away_str)

        # 让球盘口（基于实力差 or 真实赔率折算）
        diff = home_str - away_str
        if diff > 2.5:
            handicap = f"{home_cn} -1.5"
        elif diff > 1.5:
            handicap = f"{home_cn} -1"
        elif diff > 0.7:
            handicap = f"{home_cn} -0.5"
        elif diff > 0.2:
            handicap = f"{home_cn} -0/0.5"
        elif diff > -0.2:
            handicap = "平手"
        elif diff > -0.7:
            handicap = f"{away_cn} -0/0.5"
        elif diff > -1.5:
            handicap = f"{away_cn} -0.5"
        elif diff > -2.5:
            handicap = f"{away_cn} -1"
        else:
            handicap = f"{away_cn} -1.5"

        venue = m.get("ground", "")

        results.append({
            "id": i + 1,
            "time": _parse_utc_time(date_str, time_str),
            "homeTeam": home_cn,
            "awayTeam": away_cn,
            "homeFlag": _flag(home_en),
            "awayFlag": _flag(away_en),
            "group": group,
            "handicap": handicap,
            "homeOdds": odds["homeOdds"],
            "drawOdds": odds["drawOdds"],
            "awayOdds": odds["awayOdds"],
            "venue": venue,
            "homeLineup": _mock_lineup(home_cn),
            "awayLineup": _mock_lineup(away_cn),
            "homeInjuries": [],
            "awayInjuries": [],
            "h2h": _mock_h2h(home_cn, away_cn),
            "homeAttack": home_atk,
            "awayAttack": away_atk,
            "homeDefense": home_def,
            "awayDefense": away_def,
        })

    return results


# ---------------------------------------------------------------------------
# 模拟数据（阵容/伤停/H2H — 暂时无法从公开 API 稳定获取）
# ---------------------------------------------------------------------------

_GENERIC_LINEUPS = {
    "阿根廷": ["埃·马丁内斯","莫利纳","罗梅罗","奥塔门迪","塔利亚菲科","德保罗","恩佐","麦卡利斯特","阿尔瓦雷斯","劳塔罗","迪马利亚"],
    "巴西": ["阿利松","达尼洛","马尔基尼奥斯","加布里埃尔","阿拉纳","卡塞米罗","吉马良斯","帕奎塔","拉菲尼亚","维尼修斯","罗德里戈"],
    "法国": ["迈尼昂","孔德","萨利巴","于帕梅卡诺","特奥","楚阿梅尼","卡马文加","格列兹曼","登贝莱","姆巴佩","图拉姆"],
    "英格兰": ["皮克福德","阿诺德","斯通斯","格伊","卢克·肖","赖斯","贝林厄姆","萨卡","福登","帕尔默","凯恩"],
    "德国": ["特尔施特根","基米希","吕迪格","施洛特贝克","劳姆","京多安","穆西亚拉","维尔茨","萨内","哈弗茨","菲尔克鲁格"],
    "西班牙": ["西蒙","卡瓦哈尔","勒诺尔芒","拉波尔特","加亚","罗德里","佩德里","加维","亚马尔","莫拉塔","威廉姆斯"],
    "葡萄牙": ["科斯塔","坎塞洛","迪亚斯","席尔瓦","门德斯","帕利尼亚","维蒂尼亚","B费","B席","莱奥","拉莫斯"],
    "荷兰": ["弗莱肯","邓弗里斯","德里赫特","范戴克","阿克","德容","赫拉芬贝赫","西蒙斯","弗林蓬","加克波","德佩"],
    "意大利": ["多纳鲁马","迪洛伦佐","巴斯托尼","阿切尔比","迪马尔科","巴雷拉","托纳利","佩莱格里尼","基耶萨","斯卡马卡","拉斯帕多里"],
    "日本": ["铃木彩艳","菅原由势","板仓滉","富安健洋","伊藤洋辉","远藤航","守田英正","三笘薰","久保建英","堂安律","上田绮世"],
    "韩国": ["金承奎","金纹奂","金玟哉","金英权","李记帝","黄仁范","李在城","李刚仁","孙兴慜","黄喜灿","曹圭成"],
    "美国": ["特纳","德斯特","理查兹","里姆","罗宾逊","亚当斯","麦肯尼","穆萨","普利西奇","巴洛贡","维阿"],
    "墨西哥": ["奥乔亚","桑切斯","蒙特斯","巴斯克斯","阿特亚加","阿尔瓦雷斯","查韦斯","洛萨诺","皮内达","希门尼斯","韦尔塔"],
    "乌拉圭": ["罗切特","南德斯","阿劳霍","希门尼斯","奥利维拉","乌加特","巴尔韦德","本坦库尔","佩利斯特里","努涅斯","阿劳霍"],
    "克罗地亚": ["利瓦科维奇","尤拉诺维奇","舒塔洛","格瓦迪奥尔","索萨","莫德里奇","布罗佐维奇","科瓦契奇","帕萨利奇","克拉马里奇","佩里西奇"],
    "摩洛哥": ["布努","哈基米","阿盖尔德","赛斯","马兹拉维","阿姆拉巴特","奥纳希","齐耶赫","布法尔","恩内斯里","阿德利"],
    "塞内加尔": ["门迪","雅各布斯","库利巴利","迪亚洛","巴洛图雷","格耶","库亚特","萨尔","马内","杰克逊","迪亚"],
    "比利时": ["库尔图瓦","卡斯塔涅","费斯","维尔通亨","卡拉斯科","奥纳纳","蒂勒曼斯","德布劳内","多库","卢卡库","特罗萨德"],
    "哥伦比亚": ["巴尔加斯","穆尼奥斯","桑切斯","卢库米","莫希卡","莱尔马","乌里韦","J罗","迪亚斯","博雷","西尼斯特拉"],
    "埃及": ["谢纳维","哈尼","赫加齐","阿卜杜勒莫内姆","法图","阿舒尔","阿特亚","萨拉赫","马尔穆什","特雷泽盖","穆罕默德"],
}

# 中文队名作为默认占位
_DEFAULT_LINEUP = ["门将","右后卫","中后卫","中后卫","左后卫","后腰","中场","中场","边锋","前锋","前锋"]


def _mock_lineup(team_cn: str) -> list:
    """返回该队的预计首发 11 人（模拟数据）"""
    return _GENERIC_LINEUPS.get(team_cn, [f"{team_cn}{i}号" for i in range(1, 12)])


def _mock_h2h(home_cn: str, away_cn: str) -> list:
    """返回两队近 5 场历史交锋（模拟数据）"""
    hs = _strength(home_cn)
    aws = _strength(away_cn)
    results = []
    base_year = 2021
    for i in range(5):
        diff = hs - aws
        home_goals = max(0, int(random.gauss(1.2 + diff * 0.3, 0.9)))
        away_goals = max(0, int(random.gauss(1.0 - diff * 0.2, 0.8)))
        results.append({
            "date": f"{base_year + i}-06-{10 + i:02d}",
            "homeScore": home_goals,
            "awayScore": away_goals,
            "venue": "国际赛事"
        })
    return results


# ---------------------------------------------------------------------------
# 按需加载真实数据（H2H / 伤停 / 统计）
# ---------------------------------------------------------------------------

def enrich_match_detail(match_id: int) -> dict | None:
    """
    为指定比赛获取真实 H2H、伤停、统计数据
    从 API-Football 实时抓取（带缓存）
    """
    from live_data import (
        get_team_id, fetch_real_h2h,
        fetch_real_injuries, fetch_team_statistics, has_api_key
    )

    matches = fetch_real_matches(104)
    match_data = None
    for m in matches:
        if m["id"] == match_id:
            match_data = m
            break

    if not match_data:
        return None

    if not has_api_key():
        return None  # 无 API Key，保持 mock 数据

    home_cn = match_data["homeTeam"]
    away_cn = match_data["awayTeam"]
    home_id = get_team_id(home_cn)
    away_id = get_team_id(away_cn)

    if not home_id or not away_id:
        return None

    updates = {}
    try:
        # H2H: 优先查手工数据库，其次 API-Football
        h2h_key1 = home_cn + "-" + away_cn
        h2h_key2 = away_cn + "-" + home_cn
        if h2h_key1 in _H2H_DB:
            updates["h2h"] = _H2H_DB[h2h_key1]
        elif h2h_key2 in _H2H_DB:
            updates["h2h"] = _H2H_DB[h2h_key2]
        elif has_api_key():
            api_h2h = fetch_real_h2h(home_id, away_id, 5)
            if api_h2h and len(api_h2h) >= 1:
                updates["h2h"] = api_h2h

        # 伤停
        injuries_home = fetch_real_injuries(home_id)
        injuries_away = fetch_real_injuries(away_id)
        if injuries_home is not None:
            updates["homeInjuries"] = injuries_home
        if injuries_away is not None:
            updates["awayInjuries"] = injuries_away

        # 统计数据
        stats_home = fetch_team_statistics(home_id)
        stats_away = fetch_team_statistics(away_id)
        if stats_home:
            updates["homeAttack"] = stats_home["attack"]
            updates["homeDefense"] = stats_home["defense"]
        if stats_away:
            updates["awayAttack"] = stats_away["attack"]
            updates["awayDefense"] = stats_away["defense"]

        return updates
    except Exception as e:
        print(f"[enrich] Failed for match {match_id}: {e}")
        return None


def get_match_list(limit: int = 50) -> list:
    """获取比赛列表（按北京时间排序，轻量无 API 调用）"""
    # 多抓一些确保覆盖所有日期，然后按时间排序
    matches = fetch_real_matches(80)
    matches.sort(key=lambda m: m["time"])
    matches = matches[:limit]
    # 重新分配 ID（按时间顺序）
    result = []
    for i, m in enumerate(matches):
        result.append({
            "id": i + 1,
            "time": m["time"],
            "homeTeam": m["homeTeam"],
            "awayTeam": m["awayTeam"],
            "homeFlag": m["homeFlag"],
            "awayFlag": m["awayFlag"],
            "group": m["group"],
            "handicap": m["handicap"],
            "homeOdds": m["homeOdds"],
            "drawOdds": m["drawOdds"],
            "awayOdds": m["awayOdds"],
            "_orig_id": m["id"],  # 保留原始 ID 用于查详情
        })
    return result


def get_match_detail(match_id: int) -> dict | None:
    """获取单场详情（通过排序后的 ID 或原始 ID 查找）"""
    # 先尝试从排序列表中查找（新 ID 系统）
    sorted_list = get_match_list(80)
    orig_id = None
    for m in sorted_list:
        if m["id"] == match_id:
            orig_id = m.get("_orig_id", match_id)
            break

    if orig_id is None:
        orig_id = match_id

    matches = fetch_real_matches(104)
    base = None
    for m in matches:
        if m["id"] == orig_id:
            base = m
            break
    if not base:
        return None

    detail = {
        "homeLineup": base["homeLineup"],
        "awayLineup": base["awayLineup"],
        "homeInjuries": base["homeInjuries"],
        "awayInjuries": base["awayInjuries"],
        "h2h": base["h2h"],
        "homeAttack": base["homeAttack"],
        "awayAttack": base["awayAttack"],
        "homeDefense": base["homeDefense"],
        "awayDefense": base["awayDefense"],
    }

    # 尝试注入真实数据（用原始 ID 或队名查找）
    enriched = enrich_match_detail(orig_id)
    if not enriched:
        # 如果原始 ID 查找失败，直接用队名查找
        enriched = _enrich_by_teams(base["homeTeam"], base["awayTeam"])
    if enriched:
        detail.update(enriched)

    return detail


def _enrich_by_teams(home_cn, away_cn):
    """直接用队名从 H2H 数据库查找"""
    key1 = home_cn + "-" + away_cn
    key2 = away_cn + "-" + home_cn
    # 区分"找到但为空"和"未找到"
    if key1 in _H2H_DB:
        return {"h2h": _H2H_DB[key1]}
    if key2 in _H2H_DB:
        return {"h2h": _H2H_DB[key2]}
    return None

