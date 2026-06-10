import json, time
from urllib.request import urlopen, Request
KEY = '4b2c3b320e6977181410dca62d117006'
HEADERS = {'x-apisports-key': KEY}

team_id = 26  # Argentina
all_fixtures = []
for season in [2025, 2024]:
    url = f'https://v3.football.api-sports.io/fixtures?team={team_id}&season={season}'
    req = Request(url, headers=HEADERS)
    resp = urlopen(req, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    for f in data.get('response', []):
        hg = f['goals']['home']; ag = f['goals']['away']
        if hg is None: continue
        all_fixtures.append({
            'd': f['fixture']['date'][:10],
            'h': f['teams']['home']['name'], 'a': f['teams']['away']['name'],
            'hid': f['teams']['home']['id'], 'aid': f['teams']['away']['id'],
            'hg': hg, 'ag': ag
        })
    time.sleep(0.3)

all_fixtures.sort(key=lambda x: x['d'], reverse=True)
recent = all_fixtures[:10]
print(f'Argentina last {len(recent)} matches:')
gf = 0; ga = 0
for f in recent:
    if f['hid'] == team_id:
        gf += f['hg']; ga += f['ag']; side = 'HOME'
    else:
        gf += f['ag']; ga += f['hg']; side = 'AWAY'
    print(f'  {f["d"]} {side}: {f["h"]} {f["hg"]}-{f["ag"]} {f["a"]}')
print(f'GF={gf/len(recent):.2f} GA={ga/len(recent):.2f}')
