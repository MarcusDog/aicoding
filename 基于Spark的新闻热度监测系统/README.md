# 基于 Spark 的新闻热度监测系统

这是一个面向毕业设计演示的新闻热度监测系统，提供新闻采集、数据清洗、热度分析、情感分析、事件聚类、预警摘要和前端可视化展示。

本项目已经内置“一键部署 + 一键启动”脚本，适合拷贝到另一台电脑后快速运行。

## 1. 项目结构

```text
thesis/
├─ backend/                 Flask 后端、数据处理、采集与分析脚本
├─ frontend/                Vue 3 + Vite + ECharts 前端
├─ data/                    SQLite 数据库、原始数据、处理结果、导出文件
├─ docs/                    论文与过程文档
├─ deploy_start.py          跨平台部署启动入口
├─ start_windows.bat        Windows 双击启动脚本
├─ start_windows.ps1        Windows PowerShell 启动脚本
└─ start_macos_linux.sh     macOS / Linux 启动脚本
```

## 2. 推荐部署方案

如果你要把项目部署到别人电脑上，推荐按下面的优先级处理：

1. 优先使用 `Python 3.11`。
2. 前端使用 `Node.js 20 LTS` 或 `22 LTS`。
3. 数据库直接使用项目自带的 `SQLite`，不需要额外安装 MySQL。
4. 演示环境优先使用 `Pandas` 模式运行，不强依赖本机安装完整 Spark。

说明：

- 项目依赖里包含 `pyspark`，但系统默认配置 `ENABLE_SPARK=0`，即使目标电脑没有本地 Spark 运行环境，也能正常完成演示。
- 一键脚本在 `pyspark` 安装失败时会自动回退到不安装 `pyspark` 的模式继续部署。

## 3. 目标电脑需要提前安装的软件

### 必装

- Python `3.10+`，推荐 `3.11`
- Node.js `20 LTS` 或 `22 LTS`

### 可选

- Java 8/11/17
- Apache Spark

说明：

- 只有在你明确希望启用本地 Spark 计算时，才需要额外安装 Java 和 Spark。
- 纯演示部署不需要 MySQL、不需要 Redis、不需要 Docker。

## 4. 最稳妥的交付方式

把整个 `thesis/` 目录打包给对方即可，建议不要只拷某几个子目录。

建议交付时至少包含以下内容：

- `backend/`
- `frontend/`
- `data/`
- `deploy_start.py`
- `start_windows.bat`
- `start_windows.ps1`
- `start_macos_linux.sh`

建议不要把以下内容当成部署必需品：

- `backend/.venv/`
- `frontend/node_modules/`
- 各类日志、缓存、`__pycache__`

如果你想减少目标电脑的安装步骤，可以在你自己的电脑上先执行一次前端构建，把 `frontend/dist/` 一并打包过去。这样目标机即使没有 Node.js，也可以通过 `--skip-frontend` 直接启动。

## 5. Windows 一键部署与启动

### 方式一：最简单，双击启动

进入项目根目录后，直接双击：

```text
start_windows.bat
```

脚本会自动完成以下工作：

- 检查 Python 版本
- 创建 `backend/.venv`
- 安装后端依赖
- 自动创建 `backend/.env`
- 初始化 `SQLite` 数据库
- 数据为空时自动导入样例数据
- 安装并构建前端
- 启动 Flask 服务
- 自动打开浏览器

启动成功后，默认访问地址：

```text
http://127.0.0.1:5001/
```

健康检查地址：

```text
http://127.0.0.1:5001/health
```

如果 `5001` 被占用，脚本会自动尝试 `5002` 到 `5020`。

### 方式二：PowerShell 启动

```powershell
cd D:\news-monitor\thesis
.\start_windows.ps1
```

如果系统提示 PowerShell 禁止执行脚本，先执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_windows.ps1
```

## 6. macOS / Linux 一键部署与启动

```bash
cd /path/to/thesis
./start_macos_linux.sh
```

如果没有执行权限：

```bash
chmod +x start_macos_linux.sh
./start_macos_linux.sh
```

## 7. 直接使用 Python 启动

如果你不想走批处理脚本，也可以直接运行主部署脚本：

```bash
python deploy_start.py
```

常用参数如下：

```bash
python deploy_start.py --skip-pyspark
python deploy_start.py --skip-frontend
python deploy_start.py --live-on-start
python deploy_start.py --port 5001
python deploy_start.py --no-open
```

参数说明：

- `--skip-pyspark`：跳过 `pyspark` 安装，直接使用 Pandas 模式，适合演示机部署
- `--skip-frontend`：跳过前端构建，直接使用现有的 `frontend/dist`
- `--live-on-start`：启动前先抓取一次实时 RSS/API 数据
- `--port 5001`：指定 Flask 端口
- `--no-open`：启动后不自动打开浏览器

## 8. 给别人电脑部署时的推荐命令

如果目标电脑网络一般、环境较干净，推荐直接运行：

```bash
python deploy_start.py --skip-pyspark
```

如果你已经提前把前端构建好了，并且一并带上了 `frontend/dist/`，推荐运行：

```bash
python deploy_start.py --skip-pyspark --skip-frontend
```

这是最适合答辩演示和现场展示的方式，因为：

- 安装更快
- 对 Java / Spark 没有硬要求
- 依赖更少，失败概率更低

## 9. 手动部署流程

如果一键脚本因为网络、权限或环境问题失败，可以按下面步骤手动部署。

### 9.1 解压项目

建议把项目放到较短、较干净的路径，例如：

```text
D:\news-monitor\thesis
```

尽量避免：

- 路径过长
- 带很多空格
- 放在权限受限目录

### 9.2 安装后端依赖

Windows PowerShell：

```powershell
cd D:\news-monitor\thesis\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Copy-Item .env.example .env
```

如果 `pyspark` 安装失败，可改为手动跳过：

```powershell
Get-Content requirements.txt | Where-Object { $_ -notmatch '^pyspark==' } | Set-Content .requirements.runtime.txt
pip install -r .requirements.runtime.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Copy-Item .env.example .env -ErrorAction SilentlyContinue
```

macOS / Linux：

```bash
cd /path/to/thesis/backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cp .env.example .env
```

### 9.3 初始化数据库

```bash
python scripts/init_db.py
```

### 9.4 导入样例数据

```bash
python scripts/run_pipeline.py --mode sample --sample-limit 80 --no-history
```

如果现场网络正常，希望先拉一批实时新闻，可以再执行：

```bash
python scripts/run_pipeline.py --mode full --sample-limit 0 --rss-limit 30 --api-limit 50 --no-sample --no-batch
```

### 9.5 构建前端

新开一个终端：

```bash
cd /path/to/thesis/frontend
npm install
npm run build
```

构建完成后会生成：

```text
frontend/dist/
```

后端会自动托管这个目录中的静态页面。

### 9.6 启动系统

回到后端目录：

```bash
cd /path/to/thesis/backend
```

Windows：

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app app run --host 127.0.0.1 --port 5001
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m flask --app app run --host 127.0.0.1 --port 5001
```

访问地址：

```text
http://127.0.0.1:5001/
```

健康检查：

```text
http://127.0.0.1:5001/health
```

如果返回：

```json
{"status":"ok"}
```

说明后端已正常启动。

## 10. 配置说明

配置文件位置：

```text
backend/.env
```

默认内容示例：

```env
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=sqlite:///../data/news_monitor.db
SECRET_KEY=dev-secret
SPARK_MASTER=local[*]
ENABLE_SPARK=0
EXPORT_DIR=../data/exports
AUTO_FETCH_ENABLED=1
AUTO_FETCH_INTERVAL_SECONDS=600
AUTO_FETCH_RSS_LIMIT=30
AUTO_FETCH_API_LIMIT=50
AUTO_FETCH_WEB_LIMIT=0
```

常用配置说明：

- `DATABASE_URL`：数据库地址，默认使用 `SQLite`
- `ENABLE_SPARK=0`：默认关闭 Spark，演示环境建议保持不变
- `AUTO_FETCH_ENABLED=1`：开启自动抓取
- `AUTO_FETCH_INTERVAL_SECONDS=600`：每 10 分钟抓取一次
- `AUTO_FETCH_WEB_LIMIT=0`：默认不抓网页正文，降低不稳定因素

## 11. 自动实时抓取说明

系统启动后，在收到第一次浏览器请求后会自动启动后台定时抓取任务。

默认行为：

- 每 10 分钟执行一次
- 抓取 RSS / Atom / 开放 API 数据
- 写入 `data/news_monitor.db`
- 更新热度、趋势、情感、事件和预警分析结果

如果只是做演示，当前默认配置已经足够，不建议现场再改动。

## 12. 数据源检查

数据源配置文件：

```text
backend/config/source_catalog.json
```

查看当前启用的数据源：

```bash
cd /path/to/thesis/backend
python scripts/list_sources.py
```

检查实时数据源是否可抓取：

```bash
python scripts/check_live_sources.py --rss-limit 1 --api-limit 1 --web-limit 0
```

## 13. 开发模式启动

如果不是部署，而是本地开发，可以前后端分开启动。

后端：

```bash
cd /path/to/thesis/backend
python -m flask --app app run --host 127.0.0.1 --port 5000 --debug
```

前端：

```bash
cd /path/to/thesis/frontend
npm install
npm run dev
```

前端开发地址：

```text
http://127.0.0.1:5173/
```

注意：

- `frontend/vite.config.js` 默认把 `/api` 和 `/health` 代理到 `http://127.0.0.1:5000`
- 如果你把后端开发端口改成了别的端口，需要同步修改 `frontend/vite.config.js`

## 14. 常见问题

### 1. 双击脚本没有反应

优先排查：

- Python 是否已安装
- 安装 Python 时是否勾选了 `Add Python to PATH`
- 是否在项目根目录运行脚本

### 2. PowerShell 提示脚本被禁止执行

执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. `pyspark` 安装失败

这是常见情况，演示环境不影响使用。直接改用：

```bash
python deploy_start.py --skip-pyspark
```

### 4. 没装 Node.js

如果你已经在自己的电脑上构建过前端，并把 `frontend/dist/` 一起打包给对方，则可以直接运行：

```bash
python deploy_start.py --skip-frontend --skip-pyspark
```

### 5. 端口被占用

默认脚本会自动尝试 `5002` 到 `5020`。如果手动启动时端口冲突，可以改成：

```bash
python -m flask --app app run --host 127.0.0.1 --port 5002
```

### 6. 页面能打开，但没有数据

先执行：

```bash
cd /path/to/thesis/backend
python scripts/init_db.py
python scripts/run_pipeline.py --mode sample --sample-limit 80 --no-history
```

### 7. 目标电脑网络不稳定

建议直接使用样例数据演示，不要依赖现场实时抓取。

推荐命令：

```bash
python deploy_start.py --skip-pyspark --no-open
```

然后手动在浏览器打开页面。

## 15. 停止系统

如果是命令行启动，直接在终端按：

```text
Ctrl + C
```

即可停止 Flask 服务和当前进程。

## 16. 部署建议总结

如果你现在就是要把项目部署到别人电脑上，最推荐这样做：

1. 在自己电脑上先确认 `python deploy_start.py --skip-pyspark` 能跑通。
2. 额外执行一次前端构建，确保 `frontend/dist/` 已生成。
3. 将整个 `thesis/` 目录打包发给对方。
4. 在对方电脑上优先运行 `start_windows.bat`。
5. 如果对方电脑没有 Node.js，就运行 `python deploy_start.py --skip-frontend --skip-pyspark`。

这套方式对环境要求最低，最适合答辩、汇报和现场演示。
