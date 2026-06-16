import json, sys
from urllib.request import urlopen, Request
sys.stdout.reconfigure(encoding='utf-8')

def post(path, body):
    b = json.dumps(body).encode()
    req = Request(f'http://localhost:8000{path}', b, headers={'Content-Type':'application/json'})
    return json.loads(urlopen(req, timeout=10).read())

matches = [
    {'id':17, 'home':'法国', 'away':'塞内加尔', 'ha':2.4, 'hd':1.1, 'aa':1.8, 'ad':0.8,
     'ho':1.73, 'do':3.35, 'ao':4.0, 'hc':'法国 -1'},
    {'id':18, 'home':'伊拉克', 'away':'挪威', 'ha':1.2, 'hd':1.4, 'aa':5.0, 'ad':0.6,
     'ho':3.94, 'do':3.72, 'ao':1.23, 'hc':'挪威 -1.5'},
    {'id':19, 'home':'阿根廷', 'away':'阿尔及利亚', 'ha':2.0, 'hd':0.3, 'aa':2.4, 'ad':1.0,
     'ho':1.4, 'do':3.57, 'ao':4.09, 'hc':'阿根廷 -1.5'},
    {'id':20, 'home':'奥地利', 'away':'约旦', 'ha':2.3, 'hd':0.7, 'aa':1.4, 'ad':1.2,
     'ho':1.86, 'do':3.27, 'ao':3.9, 'hc':'奥地利 -1'},
]

for m in matches:
    p = post('/api/predict', {'homeAttack':m['ha'],'awayAttack':m['aa'],
                               'homeDefense':m['hd'],'awayDefense':m['ad']})
    hw = round(p['homeWin']*100,1)
    dw = round(p['draw']*100,1)
    aw = round(p['awayWin']*100,1)

    print(f"=== Match {m['id']}: {m['home']} vs {m['away']} ===")
    print(f"攻防: {m['ha']}/{m['hd']} vs {m['aa']}/{m['ad']} | {m['hc']}")
    print(f"赔率: {m['ho']}/{m['do']}/{m['ao']}")
    print(f"泊松: lambda={p['lambdaHome']}+{p['lambdaAway']}={p['expectedGoals']}")
    print(f"{m['home']} {hw}% | 平 {dw}% | {m['away']} {aw}%")
    print(f"大2.5: {round(p['over25']*100,1)}% | 最可能: {p['topScores'][0]['home']}-{p['topScores'][0]['away']}({round(p['topScores'][0]['prob']*100,1)}%)")

    for label, prob, odds in [
        (m['home'], p['homeWin'], m['ho']),
        ('平局', p['draw'], m['do']),
        (m['away'], p['awayWin'], m['ao'])
    ]:
        k = post('/api/kelly', {'aiProb': prob, 'decimalOdds': odds})
        e = round(k['edge']*100, 1)
        s = round(k['stake']*100, 1)
        flag = 'BUY' if k['recommendation'] != 'pass' else 'X'
        print(f"  {label}: Edge={e}% 仓位={s}% [{flag}]")
    print()
