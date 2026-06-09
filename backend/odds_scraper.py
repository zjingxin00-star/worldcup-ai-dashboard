"""
中国竞彩赔率爬虫
==================
数据来源: 500彩票网 (odds.500.com / live.500.com)
竞彩官方赔率结构: 胜/平/负 (SPF) + 让球胜平负 (RQSPF)

赔率字段说明:
  homeOdds  - 主胜赔率
  drawOdds  - 平局赔率
  awayOdds  - 客胜赔率
  handicap  - 让球盘口 (如 "阿根廷 -0.5")
"""

import json
import re
import time
import gzip
from urllib.request import urlopen, Request
from io import BytesIO

# 模拟真实浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.500.com/",
}

CACHE = {}
CACHE_TTL = {}


def _get(url, try_gzip=True):
    """带缓存的 HTTP GET"""
    now = time.time()
    if url in CACHE and CACHE_TTL.get(url, 0) > now:
        return CACHE[url]

    req = Request(url, headers=HEADERS)
    try:
        resp = urlopen(req, timeout=15)
        raw = resp.read()
        # 处理 gzip
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        html = raw.decode("utf-8", errors="ignore")
        CACHE[url] = html
        CACHE_TTL[url] = now + 1800  # 缓存 30 分钟
        return html
    except Exception as e:
        print(f"[odds_scraper] GET {url[:80]}: {e}")
        return None


def _extract_json(html, pattern):
    """从 HTML 中提取 JSON 数据"""
    m = re.search(pattern, html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------------------
# 方案 1: 从 live.500.com 抓取即时赔率
# ---------------------------------------------------------------------------

def _get_worldcup_schedule_500():
    """
    从 500.com 获取世界杯赛程列表
    500.com 世界杯页面通常有比赛 ID 列表
    """
    # 尝试世界杯专题页
    html = _get("https://live.500.com/?e=2026")
    if not html:
        html = _get("https://live.500.com/")

    if not html:
        return []

    # 提取比赛数据 (live.500.com 在 JS 变量中存储比赛信息)
    matches = []
    # 尝试多种正则匹配比赛数据
    for pattern in [
        r'var\s+matchList\s*=\s*(\[.*?\]);',
        r'var\s+liveData\s*=\s*(\{.*?\});',
        r'"matchList"\s*:\s*(\[.*?\])',
        r'data-match=\\"(\d+)\\"',
    ]:
        data = _extract_json(html, pattern)
        if data:
            print(f"[odds_scraper] Found data with pattern: {pattern[:50]}...")
            break

    return matches


# ---------------------------------------------------------------------------
# 方案 2: 从 500.com 指定比赛 ID 抓取赔率详情
# ---------------------------------------------------------------------------

def fetch_jingcai_odds(match_name_home, match_name_away):
    """
    根据队名在 500.com 搜索竞彩赔率
    返回: {homeOdds, drawOdds, awayOdds, handicap} 或 None
    """
    # 搜索比赛
    search_url = f"https://odds.500.com/fenxi/shuju-{match_name_home}-vs-{match_name_away}.shtml"
    html = _get(search_url)
    if not html:
        # 尝试中文队名搜索
        import urllib.parse
        query = urllib.parse.quote(f"{match_name_home} {match_name_away}")
        search_html = _get(f"https://www.500.com/search?keyword={query}")
        if search_html:
            # 从搜索结果提取比赛链接
            pass
        return None

    odds = _parse_500_odds_page(html)
    return odds


def _parse_500_odds_page(html):
    """解析 500.com 赔率分析页面"""
    result = {}

    # 即时赔率平均指数
    avg_patterns = [
        (r'平均指数.*?<td[^>]*>\s*(\d+\.\d+)\s*</td>\s*<td[^>]*>\s*(\d+\.\d+)\s*</td>\s*<td[^>]*>\s*(\d+\.\d+)\s*</td>', False),
        (r'"avgOdds"\s*:\s*\[(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+)\]', True),
        (r'"oupei"\s*:\s*\[(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+)\]', True),
    ]

    for pattern, is_json in avg_patterns:
        if is_json:
            m = re.search(pattern, html)
        else:
            m = re.search(pattern, html)
        if m:
            try:
                result["homeOdds"] = float(m.group(1))
                result["drawOdds"] = float(m.group(2))
                result["awayOdds"] = float(m.group(3))
                break
            except (ValueError, IndexError):
                continue

    # 让球盘口
    handicap_patterns = [
        r'让球.*?<td[^>]*>\s*([-+]\d[^<]*)\s*<',
        r'"rangqiu"\s*:\s*"([^"]*)"',
        r'"handicap"\s*:\s*"([^"]*)"',
    ]
    for p in handicap_patterns:
        m = re.search(p, html)
        if m:
            result["handicap"] = m.group(1).strip()
            break

    if "homeOdds" in result:
        print(f"[odds_scraper] Found odds: {result['homeOdds']}/{result['drawOdds']}/{result['awayOdds']}")
        return result
    return None


# ---------------------------------------------------------------------------
# 方案 3: 竞彩官方 API (mobile API, 更容易访问)
# ---------------------------------------------------------------------------

def fetch_jingcai_official():
    """
    尝试访问竞彩官方 mobile API
    中国竞彩网 mobile 端 API 门槛较低
    """
    # 尝试竞彩 mobile API
    urls = [
        "https://m.sporttery.cn/api/jc/index.html",
        "https://www.sporttery.cn/api/jc/getJcData/",
    ]
    for url in urls:
        html = _get(url)
        if html and len(html) > 100:
            print(f"[odds_scraper] Got data from {url}, length={len(html)}")
            return html
    return None


# ---------------------------------------------------------------------------
# 方案 4: 使用已知的竞彩第三方 API
# ---------------------------------------------------------------------------

def fetch_jingcai_by_match_date(date_str="2026-06-11"):
    """
    按日期获取竞彩足球赛程和赔率
    部分第三方站点提供按日期的 JSON 接口
    """
    # 一些可能的数据源
    candidates = [
        f"https://trade.500.com/jczq/?date={date_str}",
        f"https://odds.500.com/fenxi/index.php?date={date_str}",
    ]
    for url in candidates:
        html = _get(url)
        if html and len(html) > 200:
            print(f"[odds_scraper] Got {len(html)} bytes from candidate URL")
    return None


# ---------------------------------------------------------------------------
# 方案 5: 使用爬虫抓取 500.com 即时数据接口
# ---------------------------------------------------------------------------

def _test_connection():
    """测试各个数据源的可访问性"""
    print("[odds_scraper] Testing connections...")
    tests = [
        ("https://live.500.com/", "500.com live"),
        ("https://odds.500.com/", "500.com odds"),
        ("https://www.sporttery.cn/", "sporttery.cn"),
    ]
    for url, name in tests:
        try:
            req = Request(url, headers=HEADERS)
            resp = urlopen(req, timeout=10)
            print(f"  {name}: HTTP {resp.status} ({len(resp.read())} bytes)")
        except Exception as e:
            print(f"  {name}: FAILED - {e}")


if __name__ == "__main__":
    _test_connection()
