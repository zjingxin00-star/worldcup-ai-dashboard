"""
2026 世界杯 AI 预测 Dashboard — FastAPI 后端
==============================================

启动方式:
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API 文档:
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)

【对接爬虫说明】
当前 data.py 使用静态 Mock 数据。对接真实爬虫后：
1. 将 data.py 中的 MOCK_MATCHES / MOCK_MATCH_DETAILS 替换为数据库查询
2. 可使用 APScheduler 定时从公开体育网站抓取最新赔率
3. 推荐爬虫方案：httpx + BeautifulSoup / Scrapy + Redis 缓存
"""

import math
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import data as db

# HTML 文件路径（与 main.py 同目录）
HTML_FILE = Path(__file__).parent / "worldcup-dashboard.html"

# ---------------------------------------------------------------------------
# FastAPI 应用初始化
# ---------------------------------------------------------------------------
app = FastAPI(
    title="2026 World Cup AI Dashboard API",
    description="泊松分布预测 + 凯利公式投注决策引擎",
    version="1.0.0"
)

# CORS: 允许前端跨域访问（生产环境应限制为具体域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic 请求/响应模型
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    """泊松分布预测请求"""
    homeAttack: float = Field(..., ge=0, description="主队场均进球（攻击力）")
    awayAttack: float = Field(..., ge=0, description="客队场均进球（攻击力）")
    homeDefense: float = Field(..., ge=0, description="主队场均失球（防守力，越高越差）")
    awayDefense: float = Field(..., ge=0, description="客队场均失球（防守力，越高越差）")


class ScoreProb(BaseModel):
    """单个比分概率"""
    home: int
    away: int
    prob: float


class PredictResponse(BaseModel):
    """泊松分布预测响应"""
    homeWin: float
    draw: float
    awayWin: float
    lambdaHome: str
    lambdaAway: str
    topScores: list[ScoreProb]
    expectedGoals: str
    over25: float
    under25: float


class KellyRequest(BaseModel):
    """凯利公式请求"""
    aiProb: float = Field(..., ge=0, le=1, description="AI 预测概率 (0~1)")
    decimalOdds: float = Field(..., gt=1, description="欧赔 (大于1)")


class KellyResponse(BaseModel):
    """凯利公式响应"""
    edge: float = Field(description="优势值（正=有价值）")
    kelly: float = Field(description="凯利比例")
    stake: float = Field(description="建议仓位（1/4凯利）")
    recommendation: str = Field(description="strong_buy / buy / pass")
    aiProb: float
    impliedProb: float
    odds: float


# ---------------------------------------------------------------------------
# 泊松分布计算引擎
# ---------------------------------------------------------------------------

MAX_GOALS = 8
LEAGUE_AVG = 1.0
KELLY_FRACTION = 0.25  # 使用 1/4 凯利控制风险


def poisson_prob(lmbda: float, k: int) -> float:
    """P(k; λ) = (λ^k * e^(-λ)) / k!"""
    if lmbda <= 0:
        return 1.0 if k == 0 else 0.0
    log_p = -lmbda + k * math.log(lmbda)
    for i in range(2, k + 1):
        log_p -= math.log(i)
    return math.exp(log_p)


def calc_match_probs(home_attack: float, away_attack: float,
                     home_defense: float, away_defense: float) -> dict:
    """
    泊松分布比分概率矩阵 → 胜/平/负汇总 + Top 5 比分预测
    """
    lambda_home = home_attack * away_defense / LEAGUE_AVG
    lambda_away = away_attack * home_defense / LEAGUE_AVG

    home_prob = 0.0
    draw_prob = 0.0
    away_prob = 0.0
    score_list = []

    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            p = poisson_prob(lambda_home, i) * poisson_prob(lambda_away, j)
            score_list.append({"home": i, "away": j, "prob": p})
            if i > j:
                home_prob += p
            elif i == j:
                draw_prob += p
            else:
                away_prob += p

    # 按概率降序排列，取 Top 5
    score_list.sort(key=lambda x: x["prob"], reverse=True)
    top_scores = score_list[:5]

    # 大 2.5 球概率
    over25 = sum(s["prob"] for s in score_list if s["home"] + s["away"] > 2.5)

    return {
        "homeWin": round(home_prob, 6),
        "draw": round(draw_prob, 6),
        "awayWin": round(away_prob, 6),
        "lambdaHome": f"{lambda_home:.2f}",
        "lambdaAway": f"{lambda_away:.2f}",
        "topScores": top_scores,
        "expectedGoals": f"{lambda_home + lambda_away:.2f}",
        "over25": round(over25, 6),
        "under25": round(1 - over25, 6),
    }


def calc_kelly(ai_prob: float, decimal_odds: float) -> dict:
    """
    凯利公式: f = (p * b - q) / b
    p = AI 预测概率, b = 净赔率, q = 1 - p
    使用 1/4 凯利降风险
    """
    b = decimal_odds - 1  # 净赔率
    if b <= 0:
        return {
            "edge": -1, "kelly": 0, "stake": 0,
            "recommendation": "invalid",
            "aiProb": ai_prob, "impliedProb": 1.0, "odds": decimal_odds
        }

    q = 1 - ai_prob
    p_implied = 1 / decimal_odds       # 赔率隐含概率
    edge = ai_prob - p_implied         # 优势值
    kelly = (ai_prob * b - q) / b      # 凯利比例
    stake = max(0.0, kelly * KELLY_FRACTION)  # 1/4 凯利仓位

    if edge > 0.03:
        recommendation = "strong_buy"
    elif edge > 0:
        recommendation = "buy"
    else:
        recommendation = "pass"

    return {
        "edge": round(edge, 6),
        "kelly": round(kelly, 6),
        "stake": round(stake, 6),
        "recommendation": recommendation,
        "aiProb": round(ai_prob, 6),
        "impliedProb": round(p_implied, 6),
        "odds": decimal_odds,
    }


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------

@app.get("/api/matches")
def get_matches():
    """获取今日比赛列表（真实赛程 / Mock 兜底）"""
    return db.get_matches()


@app.get("/api/match/{match_id}")
def get_match_detail(match_id: int):
    """获取单场比赛详情"""
    detail = db.get_detail(match_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"比赛 {match_id} 不存在")
    return detail


@app.get("/api/status")
def get_status():
    """数据源状态"""
    return {"source": db.DATA_SOURCE, "matches": len(db.get_matches()),
            "odds_source": db.ODDS_SOURCE}


@app.get("/api/admin/odds")
def get_odds_config():
    """获取当前赔率配置"""
    return db.load_odds_config()


@app.post("/api/admin/odds")
def save_odds_config(data: dict):
    """保存赔率配置 (POST body: {matchId: {homeOdds, drawOdds, awayOdds, handicap}})"""
    db.save_odds_config(data)
    return {"status": "ok", "saved": len(data)}


@app.get("/admin", response_class=HTMLResponse)
def admin_panel():
    """赔率管理页面"""
    import json
    matches = db.get_matches()
    config = db.load_odds_config()
    rows = []
    for m in matches:
        mid = str(m["id"])
        o = config.get(mid, {})
        rows.append(f"""
        <tr>
          <td style='padding:8px'>{m['homeFlag']} {m['homeTeam']} vs {m['awayTeam']} {m['awayFlag']}</td>
          <td style='padding:4px'>{m['group']} {m['time']}</td>
          <td><input id='h{mid}' value='{o.get('homeOdds', m['homeOdds'])}' size='5' style='padding:4px;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:4px'></td>
          <td><input id='d{mid}' value='{o.get('drawOdds', m['drawOdds'])}' size='5' style='padding:4px;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:4px'></td>
          <td><input id='a{mid}' value='{o.get('awayOdds', m['awayOdds'])}' size='5' style='padding:4px;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:4px'></td>
          <td><input id='p{mid}' value='{o.get('handicap', m['handicap'])}' size='10' style='padding:4px;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:4px'></td>
        </tr>""")
    html = f"""<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>赔率管理</title>
<style>body{{background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:24px}}
table{{border-collapse:collapse;width:100%}}th{{background:#1e293b;padding:10px;text-align:left}}
tr:hover{{background:#1e293b}}button{{padding:10px 24px;background:#10b981;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:16px}}
#msg{{color:#34d399;margin-left:16px}}</style></head><body>
<h1 style='color:#34d399'>赔率配置</h1><p style='color:#94a3b8'>从 sporttery.cn 查到竞彩赔率后填入下表，点保存即可</p>
<table><thead><tr><th>比赛</th><th>时间/小组</th><th>主胜</th><th>平局</th><th>客胜</th><th>让球盘口</th></tr></thead><tbody>
{''.join(rows)}
</tbody></table>
<button onclick='save()' style='margin-top:16px'>保存赔率</button><span id='msg'></span>
<script>
function save() {{
  var data = {{}};
  { 'var ids = [' + ','.join([f"'{m['id']}'" for m in matches]) + '];' }
  ids.forEach(function(id) {{
    data[id] = {{
      homeOdds: parseFloat(document.getElementById('h'+id).value),
      drawOdds: parseFloat(document.getElementById('d'+id).value),
      awayOdds: parseFloat(document.getElementById('a'+id).value),
      handicap: document.getElementById('p'+id).value
    }};
  }});
  fetch('/api/admin/odds', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}})
    .then(function(r){{ return r.json(); }})
    .then(function(d){{ document.getElementById('msg').textContent='已保存 '+d.saved+' 场比赛赔率! 刷新主页即可看到'; }})
    .catch(function(e){{ document.getElementById('msg').textContent='保存失败: '+e; }});
}}
</script></body></html>"""
    return HTMLResponse(content=html)


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    AI 泊松分布预测
    输入两队攻防数据 → 返回胜平负概率 + Top 5 比分 + 大小球
    """
    result = calc_match_probs(
        req.homeAttack, req.awayAttack,
        req.homeDefense, req.awayDefense
    )
    return result


@app.post("/api/kelly", response_model=KellyResponse)
def kelly_bet(req: KellyRequest):
    """
    凯利公式投注决策
    输入 AI 概率 + 欧赔 → 返回 Edge 优势值 + 建议仓位
    """
    result = calc_kelly(req.aiProb, req.decimalOdds)
    return result


# ---------------------------------------------------------------------------
# 前端首页
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """
    返回 2026 世界杯 Dashboard 前端页面
    启动后端后直接访问 http://localhost:8000 即可使用
    """
    if not HTML_FILE.exists():
        raise HTTPException(status_code=404, detail="worldcup-dashboard.html 未找到，请确保文件在 backend 上级目录")
    return HTML_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 启动事件（预留爬虫定时任务入口）
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    服务启动时执行
    【此处可对接 APScheduler 定时爬取任务】
    示例:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(scraper.fetch_all, 'interval', minutes=30)
        scheduler.start()
    """
    port = os.environ.get("PORT", "8000")
    db.load_data()
    print("2026 World Cup AI Dashboard API started")
    print(f"Data source: {db.DATA_SOURCE}")
    print(f"Local:   http://localhost:{port}")
    print(f"API Doc: http://localhost:{port}/docs")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
