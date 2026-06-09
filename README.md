# 2026 美洲世界杯 AI 预测 & 体彩决策 Dashboard

深色极客风格的世界杯 AI 预测网页，使用**泊松分布**计算胜平负概率，**凯利公式**给出最优投注仓位建议。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | HTML5 + CSS3 + 纯 JavaScript + Chart.js |
| 后端 | Python FastAPI |
| AI 模型 | 泊松分布（比分概率矩阵） |
| 决策引擎 | 凯利公式（1/4 Fractional Kelly） |

## 快速启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

浏览器访问 `http://localhost:8000`

## 一键部署到 Render (免费)

1. Fork 此仓库到你的 GitHub
2. 打开 [render.com](https://render.com) → New Web Service
3. 连接 GitHub 仓库，配置：
   - **Root Directory**: `backend`
- **Environment Variable**: `PYTHON_VERSION` = `3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 点击 Deploy → 获得 `https://xxx.onrender.com` 公网链接

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | Dashboard 网页 |
| `GET` | `/api/matches` | 今日比赛列表 |
| `GET` | `/api/match/{id}` | 单场详情 |
| `POST` | `/api/predict` | 泊松分布 AI 预测 |
| `POST` | `/api/kelly` | 凯利公式投注决策 |

## Mock 数据说明

当前使用内置 Mock 数据（6 场模拟比赛）。对接真实爬虫时修改 `backend/data.py`。

## 截图

![Dashboard Screenshot](screenshot.png)
