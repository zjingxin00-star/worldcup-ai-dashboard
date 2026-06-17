import json, sys
from urllib.request import urlopen, Request
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8000'

def post(path, body):
    b = json.dumps(body).encode()
    return json.loads(urlopen(Request(BASE + path, b,
        headers={'Content-Type':'application/json'}), timeout=10).read())

matches = [
    {'id':21,'H':'葡萄牙','A':'刚果(金)','ha':2.9,'hd':1.3,'aa':1.2,'ad':1.0,
     'ho':1.18,'do':6.0,'ao':13.0,'hc':'葡萄牙 -1.5','G':'K'},
    {'id':22,'H':'英格兰','A':'克罗地亚','ha':3.0,'hd':0.5,'aa':2.8,'ad':0.6,
     'ho':1.85,'do':3.3,'ao':4.2,'hc':'英格兰 -0.5','G':'L'},
    {'id':23,'H':'加纳','A':'巴拿马','ha':2.3,'hd':0.8,'aa':1.0,'ad':1.5,
     'ho':1.55,'do':3.6,'ao':5.8,'hc':'加纳 -1','G':'L'},
    {'id':24,'H':'乌兹别克斯坦','A':'哥伦比亚','ha':1.4,'hd':1.0,'aa':2.4,'ad':0.6,
     'ho':5.5,'do':3.8,'ao':1.55,'hc':'哥伦比亚 -1.5','G':'K'},
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

    print("=== Match {}: {} vs {} ({}) ===".format(m['id'], m['H'], m['A'], m['G']))
    print("攻防: {}/{} vs {}/{} | {}".format(
        m['ha'],m['hd'], m['aa'],m['ad'], m['hc']))
    print("赔率: {}/{}/{}".format(m['ho'], m['do'], m['ao']))
    print("泊松: lambda={}+{}={}".format(
        p['lambdaHome'], p['lambdaAway'], p['expectedGoals']))
    print("{} {}% | 平 {}% | {} {}%".format(m['H'], hw, dw, m['A'], aw))
    print("大2.5: {}% | 最可能: {}-{} ({}%)".format(
        round(p['over25']*100,1), top['home'], top['away'],
        round(top['prob']*100,1)))

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
