"""Test H2H without 'last' param"""
import json
from urllib.request import urlopen, Request

KEY = "4b2c3b320e6977181410dca62d117006"
HEADERS = {"x-apisports-key": KEY}

# H2H without last param
print("=== H2H: Argentina(26) vs France(2) ===")
url = "https://v3.football.api-sports.io/fixtures/headtohead?h2h=26-2"
req = Request(url, headers=HEADERS)
resp = urlopen(req, timeout=15)
data = json.loads(resp.read())
fixtures = data.get("response", [])
errors = data.get("errors", [])
print(f"Errors: {errors}")
print(f"Results: {len(fixtures)}")
for f in fixtures[:5]:
    print(f"  {f['fixture']['date'][:10]}: {f['teams']['home']['name']} {f['goals']['home']}-{f['goals']['away']} {f['teams']['away']['name']} ({f['league']['name']})")
print(f"Rate: {resp.headers.get('x-ratelimit-requests-remaining')}")

# H2H with league filter (World Cup only)
print("\n=== H2H in World Cup only: Argentina(26) vs France(2) ===")
url = "https://v3.football.api-sports.io/fixtures/headtohead?h2h=26-2&league=1&season=2022"
req = Request(url, headers=HEADERS)
resp = urlopen(req, timeout=15)
data = json.loads(resp.read())
fixtures = data.get("response", [])
print(f"Results: {len(fixtures)}")
for f in fixtures:
    print(f"  {f['fixture']['date'][:10]}: {f['teams']['home']['name']} {f['goals']['home']}-{f['goals']['away']} {f['teams']['away']['name']}")
print(f"Rate: {resp.headers.get('x-ratelimit-requests-remaining')}")

# Get Argentina recent fixtures (no last param)
print("\n=== Argentina recent fixtures (team=26, season=2024) ===")
url = "https://v3.football.api-sports.io/fixtures?team=26&season=2024"
req = Request(url, headers=HEADERS)
resp = urlopen(req, timeout=15)
data = json.loads(resp.read())
fixtures = data.get("response", [])
print(f"Results: {len(fixtures)}")
for f in fixtures[:5]:
    print(f"  {f['fixture']['date'][:10]}: {f['teams']['home']['name']} {f['goals']['home']}-{f['goals']['away']} {f['teams']['away']['name']} ({f['league']['name']})")
print(f"Rate: {resp.headers.get('x-ratelimit-requests-remaining')}")
