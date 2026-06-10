"""Find national team IDs for missing 2026 WC teams"""
import json, sys, io
from urllib.request import urlopen, Request, quote

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KEY = "4b2c3b320e6977181410dca62d117006"
HEADERS = {"x-apisports-key": KEY}

# Missing teams: English name -> try to find
missing = [
    "Colombia", "Austria", "Turkey", "Norway", "Ukraine",
    "Czech Republic", "Hungary", "Slovakia", "Romania", "Greece",
    "Ireland", "Finland", "Iceland", "Bosnia & Herzegovina",
    "Albania", "Georgia", "Bulgaria", "Slovenia", "North Macedonia",
    "Kosovo", "Luxembourg", "Ivory Coast", "Ghana", "Algeria",
    "Mali", "Burkina Faso", "DR Congo", "South Africa",
    "Guinea", "Zambia", "Cape Verde", "Nigeria",
    "Curaçao", "Haiti", "Panama", "Jamaica", "Honduras",
    "El Salvador", "Venezuela", "Bolivia", "Paraguay",
    "New Zealand", "United Arab Emirates", "Iraq", "Scotland",
    "Chile", "Peru", "Sweden", "Egypt", "Italy",
]

# For each, search API-Football for the national team
found = {}
for team in missing:
    try:
        url = f"https://v3.football.api-sports.io/teams?search={quote(team)}"
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        teams = data.get("response", [])
        # Filter for national teams (where team name matches country, not club)
        national = [t for t in teams if t['team'].get('national', False) or t['team']['name'] == team]
        if not national:
            # If no national flag, take the one whose name matches the country
            national = [t for t in teams if team.lower() in t['team']['name'].lower() and 'country' in str(t).lower()]
        if not national and teams:
            # Just take the first one - might be a club, but check the country field
            for t in teams:
                if t['team'].get('country') == team:
                    national = [t]
                    break
        if teams and not national:
            # Print all results for debugging
            for t in teams[:3]:
                print(f"  {team}: ID={t['team']['id']} Name={t['team']['name']} Country={t['team'].get('country','?')} National={t['team'].get('national','?')}")
        if national:
            t = national[0]['team']
            found[team] = t['id']
            print(f"  OK {team}: ID={t['id']} ({t['name']})")
        elif not teams:
            print(f"  ?? {team}: no results")
    except Exception as e:
        print(f"  XX {team}: {e}")

print(f"\nFound {len(found)}/{len(missing)} teams")
print("\nTEAM_IDS updates:")
for name, tid in sorted(found.items()):
    print(f'    "{name}": {tid},')
