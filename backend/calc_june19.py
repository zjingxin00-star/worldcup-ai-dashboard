import json, sys
from urllib.request import urlopen, Request
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8000'

def post(path, body):
    b = json.dumps(body).encode()
    return json.loads(urlopen(Request(BASE + path, b,
        headers={'Content-Type':'application/json'}), timeout=10).read())

matches = [
    {'id':25,'H':'捷克','A':'南非','ha':2.1,'hd':1.1,'aa':1.2,'ad':1.1,
     'ho':2.1,'do':3.15,'ao':3.65,'hc':'捷克 -0.5','G':'A'},
    {'id':26,'H':'瑞士','A':'波黑','ha':1.9,'hd':1.0,'aa':1.1,'ad':1.3,
     'ho':1.69,'do':3.37,'ao':4.03,'hc':'瑞士 -1','G':'B'},
    {'id':27,'H':'加拿大','A':'卡塔尔','ha':1.3,'hd':1.0,'aa':1.7,'ad':0.9,
     'ho':2.0,'do':3.2,'ao':3.76,'hc':'加拿大 -0.5','G':'B'},
    {'id':28,'H':'墨西哥','A':'韩国','ha':1.4,'hd':0.4,'aa':2.3,'ad':1.0,
     'ho':2.72,'do':2.87,'ao':2.98,'hc':'墨西哥 -0/0.5','G':'A'},
]

for m in matches:
    p = post('/api/predict', {
        'homeAttack': m['ha'], 'awayAttack': m['aa'],
        'homeDefense': m['hd'], 'awayDefense': m['ad']
    })
    hw = round(p['homeWin']*100, 1)
    dw = round(p['draw']*100, 1)
    aw = round(p['awayWin']*100, 1)
    top = p['topScores'][0]
    ov = round(p['over25']*100, 1)

    print("=== Match {}: {} vs {} ({}) ===".format(m['id'], m['H'], m['A'], m['G']))
    print("攻防: {}/{} vs {}/{} | {}".format(m['ha'],m['hd'],m['aa'],m['ad'],m['hc']))
    print("赔率: {}/{}/{}".format(m['ho'],m['do'],m['ao']))
    print("泊松: L={}+{}={} | 大2.5: {}%".format(
        p['lambdaHome'],p['lambdaAway'],p['expectedGoals'], ov))
    print("{} {}% | 平 {}% | {} {}% | Top: {}-{}({}%)".format(
        m['H'],hw, dw, m['A'],aw, top['home'],top['away'],round(top['prob']*100,1)))

    for lbl, pr, od in [
        (m['H']+'胜', p['homeWin'], m['ho']),
        ('平局', p['draw'], m['do']),
        (m['A']+'胜', p['awayWin'], m['ao'])
    ]:
        k = post('/api/kelly', {'aiProb': pr, 'decimalOdds': od})
        e = round(k['edge']*100, 1)
        s = round(k['stake']*100, 1)
        flag = 'BUY' if k['recommendation'] != 'pass' else '-'
        print("  {}: Edge={}% 仓位={}% [{}]".format(lbl, e, s, flag))
    print()
