"""
世界杯 Mock 数据集
====================
【此处对接 Python 爬虫接口】
当前使用静态 Mock 数据。后续替换方案：
1. 使用 httpx + BeautifulSoup 从公开体育网站抓取赛程/赔率
2. 使用 scrapy 定期爬取并存入 SQLite/Redis
3. 替换此文件中的 MOCK_MATCHES / MOCK_MATCH_DETAILS 为数据库查询

数据结构与前端 MOCK_MATCHES / MOCK_MATCH_DETAILS 完全一致，不可修改字段名。
"""

MOCK_MATCHES = [
    {
        "id": 1, "time": "2026-06-10 21:00",
        "homeTeam": "阿根廷", "awayTeam": "巴西",
        "homeFlag": "🇦🇷", "awayFlag": "🇧🇷",
        "group": "H组", "handicap": "阿根廷 -0.5",
        "homeOdds": 2.45, "drawOdds": 3.10, "awayOdds": 2.90
    },
    {
        "id": 2, "time": "2026-06-10 23:30",
        "homeTeam": "美国", "awayTeam": "英格兰",
        "homeFlag": "🇺🇸", "awayFlag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "group": "B组", "handicap": "英格兰 -0.5/1",
        "homeOdds": 3.80, "drawOdds": 3.40, "awayOdds": 1.95
    },
    {
        "id": 3, "time": "2026-06-11 03:00",
        "homeTeam": "西班牙", "awayTeam": "德国",
        "homeFlag": "🇪🇸", "awayFlag": "🇩🇪",
        "group": "E组", "handicap": "平手",
        "homeOdds": 2.60, "drawOdds": 3.20, "awayOdds": 2.70
    },
    {
        "id": 4, "time": "2026-06-11 06:00",
        "homeTeam": "墨西哥", "awayTeam": "法国",
        "homeFlag": "🇲🇽", "awayFlag": "🇫🇷",
        "group": "C组", "handicap": "法国 -1",
        "homeOdds": 5.50, "drawOdds": 4.00, "awayOdds": 1.55
    },
    {
        "id": 5, "time": "2026-06-11 09:00",
        "homeTeam": "日本", "awayTeam": "塞内加尔",
        "homeFlag": "🇯🇵", "awayFlag": "🇸🇳",
        "group": "F组", "handicap": "日本 -0/0.5",
        "homeOdds": 2.20, "drawOdds": 3.00, "awayOdds": 3.50
    },
    {
        "id": 6, "time": "2026-06-11 12:00",
        "homeTeam": "葡萄牙", "awayTeam": "荷兰",
        "homeFlag": "🇵🇹", "awayFlag": "🇳🇱",
        "group": "G组", "handicap": "葡萄牙 -0/0.5",
        "homeOdds": 2.35, "drawOdds": 3.25, "awayOdds": 2.95
    }
]

MOCK_MATCH_DETAILS = {
    1: {
        "homeLineup": [
            "埃米利亚诺·马丁内斯", "莫利纳", "克里斯蒂安·罗梅罗", "奥塔门迪",
            "塔利亚菲科", "德保罗", "恩佐·费尔南德斯", "麦卡利斯特",
            "阿尔瓦雷斯", "劳塔罗·马丁内斯", "迪马利亚"
        ],
        "awayLineup": [
            "阿利松", "达尼洛", "马尔基尼奥斯", "加布里埃尔",
            "阿拉纳", "卡塞米罗", "吉马良斯", "帕奎塔",
            "拉菲尼亚", "维尼修斯", "罗德里戈"
        ],
        "homeInjuries": [
            {"name": "梅西", "status": "肌肉拉伤，出战成疑", "critical": True}
        ],
        "awayInjuries": [
            {"name": "内马尔", "status": "十字韧带断裂，赛季报销", "critical": True},
            {"name": "米利唐", "status": "累计黄牌停赛", "critical": False}
        ],
        "h2h": [
            {"date": "2025-11-18", "homeScore": 1, "awayScore": 0, "venue": "世预赛"},
            {"date": "2024-07-10", "homeScore": 0, "awayScore": 2, "venue": "美洲杯半决赛"},
            {"date": "2023-09-05", "homeScore": 0, "awayScore": 0, "venue": "世预赛"},
            {"date": "2022-06-01", "homeScore": 3, "awayScore": 1, "venue": "南美超级德比"},
            {"date": "2021-07-11", "homeScore": 1, "awayScore": 0, "venue": "美洲杯决赛"}
        ],
        "homeAttack": 1.8, "awayAttack": 1.6,
        "homeDefense": 0.7, "awayDefense": 0.8
    },
    2: {
        "homeLineup": [
            "马特·特纳", "德斯特", "克里斯·理查兹", "蒂姆·里姆",
            "安东尼·罗宾逊", "泰勒·亚当斯", "麦肯尼", "穆萨",
            "普利西奇", "巴洛贡", "维阿"
        ],
        "awayLineup": [
            "皮克福德", "阿诺德", "斯通斯", "格伊", "卢克·肖",
            "赖斯", "贝林厄姆", "萨卡", "福登", "帕尔默", "凯恩"
        ],
        "homeInjuries": [
            {"name": "雷纳", "status": "脚踝扭伤，每日观察", "critical": False}
        ],
        "awayInjuries": [
            {"name": "里斯·詹姆斯", "status": "腿筋拉伤，预计缺席", "critical": True}
        ],
        "h2h": [
            {"date": "2025-06-15", "homeScore": 1, "awayScore": 3, "venue": "友谊赛"},
            {"date": "2022-11-25", "homeScore": 0, "awayScore": 0, "venue": "世界杯小组赛"},
            {"date": "2019-07-04", "homeScore": 2, "awayScore": 1, "venue": "友谊赛"},
            {"date": "2018-06-07", "homeScore": 1, "awayScore": 1, "venue": "友谊赛"},
            {"date": "2010-06-12", "homeScore": 1, "awayScore": 1, "venue": "世界杯小组赛"}
        ],
        "homeAttack": 1.3, "awayAttack": 2.0,
        "homeDefense": 1.2, "awayDefense": 0.6
    },
    3: {
        "homeLineup": [
            "乌奈·西蒙", "卡瓦哈尔", "勒诺尔芒", "拉波尔特", "加亚",
            "罗德里", "佩德里", "加维", "亚马尔", "莫拉塔", "尼科·威廉姆斯"
        ],
        "awayLineup": [
            "特尔施特根", "基米希", "吕迪格", "施洛特贝克", "劳姆",
            "京多安", "穆西亚拉", "维尔茨", "萨内", "哈弗茨", "菲尔克鲁格"
        ],
        "homeInjuries": [
            {"name": "奥尔莫", "status": "轻微肌肉不适，可出战", "critical": False}
        ],
        "awayInjuries": [
            {"name": "诺伊尔", "status": "退役（国家队）", "critical": False},
            {"name": "克罗斯", "status": "退役（国家队）", "critical": True}
        ],
        "h2h": [
            {"date": "2025-10-14", "homeScore": 2, "awayScore": 2, "venue": "欧国联"},
            {"date": "2024-07-05", "homeScore": 2, "awayScore": 1, "venue": "欧洲杯1/4决赛"},
            {"date": "2022-11-27", "homeScore": 1, "awayScore": 1, "venue": "世界杯小组赛"},
            {"date": "2020-11-17", "homeScore": 6, "awayScore": 0, "venue": "欧国联"},
            {"date": "2018-10-13", "homeScore": 1, "awayScore": 1, "venue": "欧国联"}
        ],
        "homeAttack": 1.9, "awayAttack": 1.8,
        "homeDefense": 0.7, "awayDefense": 0.9
    },
    4: {
        "homeLineup": [
            "奥乔亚", "豪尔赫·桑切斯", "蒙特斯", "巴斯克斯", "阿特亚加",
            "埃德松·阿尔瓦雷斯", "查韦斯", "洛萨诺", "皮内达", "希门尼斯", "韦尔塔"
        ],
        "awayLineup": [
            "迈尼昂", "孔德", "萨利巴", "于帕梅卡诺", "特奥·埃尔南德斯",
            "楚阿梅尼", "卡马文加", "格列兹曼", "登贝莱", "姆巴佩", "图拉姆"
        ],
        "homeInjuries": [
            {"name": "劳尔·希门尼斯", "status": "腹股沟伤势，出战存疑", "critical": True}
        ],
        "awayInjuries": [
            {"name": "卢卡斯·埃尔南德斯", "status": "ACL术后恢复中", "critical": True}
        ],
        "h2h": [
            {"date": "2024-03-23", "homeScore": 0, "awayScore": 2, "venue": "友谊赛"},
            {"date": "2022-01-27", "homeScore": 0, "awayScore": 1, "venue": "友谊赛"},
            {"date": "2018-07-01", "homeScore": 0, "awayScore": 2, "venue": "世界杯1/8决赛"},
            {"date": "2010-06-17", "homeScore": 2, "awayScore": 0, "venue": "世界杯小组赛"},
            {"date": "2006-05-27", "homeScore": 0, "awayScore": 1, "venue": "友谊赛"}
        ],
        "homeAttack": 1.0, "awayAttack": 2.2,
        "homeDefense": 1.3, "awayDefense": 0.5
    },
    5: {
        "homeLineup": [
            "铃木彩艳", "菅原由势", "板仓滉", "富安健洋", "伊藤洋辉",
            "远藤航", "守田英正", "三笘薰", "久保建英", "堂安律", "上田绮世"
        ],
        "awayLineup": [
            "爱德华·门迪", "雅各布斯", "库利巴利", "迪亚洛", "巴洛-图雷",
            "格耶", "库亚特", "伊斯梅拉·萨尔", "马内", "杰克逊", "迪亚"
        ],
        "homeInjuries": [],
        "awayInjuries": [
            {"name": "库利巴利", "status": "膝盖不适，每日观察", "critical": False}
        ],
        "h2h": [
            {"date": "2023-10-17", "homeScore": 2, "awayScore": 0, "venue": "友谊赛"},
            {"date": "2022-06-10", "homeScore": 4, "awayScore": 1, "venue": "麒麟杯"},
            {"date": "2019-06-14", "homeScore": 1, "awayScore": 2, "venue": "友谊赛"},
            {"date": "2018-06-24", "homeScore": 2, "awayScore": 2, "venue": "世界杯小组赛"},
            {"date": "2002-06-04", "homeScore": 2, "awayScore": 2, "venue": "友谊赛"}
        ],
        "homeAttack": 1.5, "awayAttack": 1.1,
        "homeDefense": 0.9, "awayDefense": 1.0
    },
    6: {
        "homeLineup": [
            "迪奥戈·科斯塔", "坎塞洛", "鲁本·迪亚斯", "安东尼奥·席尔瓦", "努诺·门德斯",
            "帕利尼亚", "维蒂尼亚", "布鲁诺·费尔南德斯", "贝尔纳多·席尔瓦", "莱奥", "贡萨洛·拉莫斯"
        ],
        "awayLineup": [
            "弗莱肯", "邓弗里斯", "德里赫特", "范戴克", "阿克",
            "德容", "赫拉芬贝赫", "西蒙斯", "弗林蓬", "加克波", "德佩"
        ],
        "homeInjuries": [
            {"name": "C罗", "status": "肌肉疲劳，可能替补", "critical": True}
        ],
        "awayInjuries": [
            {"name": "德佩", "status": "恢复训练，状态未达100%", "critical": False}
        ],
        "h2h": [
            {"date": "2025-06-05", "homeScore": 2, "awayScore": 1, "venue": "欧国联"},
            {"date": "2024-03-21", "homeScore": 0, "awayScore": 1, "venue": "友谊赛"},
            {"date": "2022-12-09", "homeScore": 1, "awayScore": 2, "venue": "世界杯1/4决赛"},
            {"date": "2019-06-09", "homeScore": 1, "awayScore": 0, "venue": "欧国联决赛"},
            {"date": "2018-03-26", "homeScore": 0, "awayScore": 3, "venue": "友谊赛"}
        ],
        "homeAttack": 1.7, "awayAttack": 1.6,
        "homeDefense": 0.6, "awayDefense": 0.7
    }
}
