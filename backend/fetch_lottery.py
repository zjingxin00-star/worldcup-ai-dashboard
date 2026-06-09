"""Fetch Chinese sports lottery odds from m.sporttery.cn"""
import re, json, gzip
from urllib.request import urlopen, Request
from io import BytesIO

HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://m.sporttery.cn/",
}

def fetch_url(url):
    req = Request(url, headers=HEADERS_MOBILE)
    try:
        resp = urlopen(req, timeout=15)
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        elif resp.headers.get("Content-Encoding") == "br":
            try:
                import brotli
                raw = brotli.decompress(raw)
            except ImportError:
                pass
        return raw.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Try multiple URLs
urls = [
    "https://m.sporttery.cn/mjc/jsq/zqspf/",
    "https://m.sporttery.cn/api/mjc/jsq/zqspf/",
    "https://m.sporttery.cn/mjc/jsq/",
]

for url in urls:
    print(f"\n=== Trying: {url} ===")
    html = fetch_url(url)
    if html:
        print(f"Got {len(html)} bytes")
        # Look for data
        for pattern in [r'var\s+(\w+)\s*=\s*(\[.*?\]);', r'window\.(\w+)\s*=\s*(\{.*?\});',
                        r'src="([^"]+?\.js)"', r'data-url="([^"]*)"',
                        r'api[^"]*["\']([^"\']*?)["\']']:
            matches = re.findall(pattern, html[:100000])
            for m in matches[:5]:
                s = str(m)[:200]
                if any(k in s.lower() for k in ['odds','match','game','data','spf','zq','json']):
                    print(f"  FOUND: {s}")
        # Show HTML structure hints
        print(f"  Title: {re.findall(r'<title>([^<]+)</title>', html)}")
        apis = re.findall(r'https?://[^"\'\s]+?(?:api|json|data)[^"\'\s]*', html)
        for a in apis[:5]:
            print(f"  API URL: {a}")
    else:
        print("  FAILED")

# Also try the desktop API
print("\n=== Trying desktop API ===")
api_urls = [
    "https://www.sporttery.cn/api/mjc/jsq/getJcData/",
    "https://webapi.sporttery.cn/gateway/lottery/getFootballList.qry",
]
for url in api_urls:
    print(f"Trying: {url}")
    html = fetch_url(url)
    if html:
        print(f"  Got {len(html)} bytes: {html[:300]}")
    else:
        print("  FAILED")
