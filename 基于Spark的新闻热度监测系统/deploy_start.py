from __future__ import annotations

import argparse
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"


def log(message: str) -> None:
    print(f"[deploy] {message}", flush=True)


def is_windows() -> bool:
    return platform.system() == "Windows"


def command_name(name: str) -> str:
    if is_windows() and name in {"npm", "npx"}:
        return f"{name}.cmd"
    return name


def run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
    log(f"运行: {' '.join(command)}")
    return subprocess.run(command, cwd=str(cwd) if cwd else None, env=env, check=check)


def venv_python(venv_dir: Path) -> Path:
    if is_windows():
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def find_compatible_python() -> str | None:
    if sys.version_info >= (3, 10):
        return sys.executable

    candidates = [
        ["py", "-3.11"],
        ["py", "-3.10"],
        ["python3.11"],
        ["python3.10"],
        ["python3"],
        ["python"],
    ]
    for candidate in candidates:
        executable = candidate[0]
        if shutil.which(executable) is None:
            continue
        try:
            completed = subprocess.run(
                candidate + ["-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            continue
        if completed.returncode == 0:
            return executable if len(candidate) == 1 else " ".join(candidate)
    return None


def reexec_if_needed() -> None:
    if sys.version_info >= (3, 10):
        return
    python_cmd = find_compatible_python()
    if python_cmd is None:
        raise SystemExit("需要 Python 3.10 或 3.11。请先安装 Python 3.11 后重试。")
    log(f"当前 Python 版本过低，切换到: {python_cmd}")
    if " " in python_cmd:
        parts = python_cmd.split()
    else:
        parts = [python_cmd]
    os.execvp(parts[0], parts + [str(Path(__file__).resolve())] + sys.argv[1:])


def assert_project_root() -> None:
    required = [
        BACKEND_DIR / "requirements.txt",
        BACKEND_DIR / "scripts" / "init_db.py",
        FRONTEND_DIR / "package.json",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        paths = "\n".join(str(path) for path in missing)
        raise SystemExit(f"项目目录不完整，缺少文件:\n{paths}")


def write_runtime_requirements(source: Path, target: Path, skip_pyspark: bool) -> None:
    lines = source.read_text(encoding="utf-8").splitlines()
    filtered: list[str] = []
    for line in lines:
        stripped = line.strip()
        if skip_pyspark and stripped.startswith("pyspark=="):
            continue
        filtered.append(line)
    target.write_text("\n".join(filtered).rstrip() + "\n", encoding="utf-8")


def ensure_env_file() -> None:
    env_file = BACKEND_DIR / ".env"
    example_file = BACKEND_DIR / ".env.example"
    if env_file.exists() or not example_file.exists():
        return
    shutil.copyfile(example_file, env_file)
    log("已从 backend/.env.example 创建 backend/.env")


def ensure_backend_venv(args: argparse.Namespace) -> Path:
    venv_dir = BACKEND_DIR / ".venv"
    python_path = venv_python(venv_dir)
    if not python_path.exists():
        run([sys.executable, "-m", "venv", str(venv_dir)], cwd=PROJECT_ROOT)

    run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], cwd=BACKEND_DIR)

    requirement_file = BACKEND_DIR / "requirements.txt"
    runtime_requirement = BACKEND_DIR / ".requirements.runtime.txt"
    write_runtime_requirements(requirement_file, runtime_requirement, skip_pyspark=args.skip_pyspark)
    install_command = [str(python_path), "-m", "pip", "install", "-r", str(runtime_requirement)]
    if args.pip_index_url:
        install_command.extend(["-i", args.pip_index_url])

    completed = run(install_command, cwd=BACKEND_DIR, check=False)
    if completed.returncode != 0 and not args.skip_pyspark:
        log("完整依赖安装失败，自动重试：跳过体积较大的 pyspark，使用 Pandas 模式启动。")
        write_runtime_requirements(requirement_file, runtime_requirement, skip_pyspark=True)
        retry_command = [str(python_path), "-m", "pip", "install", "-r", str(runtime_requirement)]
        if args.pip_index_url:
            retry_command.extend(["-i", args.pip_index_url])
        run(retry_command, cwd=BACKEND_DIR)
    elif completed.returncode != 0:
        raise SystemExit("后端依赖安装失败，请检查 Python 版本和网络。")

    return python_path


def node_available() -> bool:
    return shutil.which("node") is not None and shutil.which(command_name("npm")) is not None


def ensure_frontend(args: argparse.Namespace) -> None:
    dist_index = FRONTEND_DIR / "dist" / "index.html"
    if args.skip_frontend:
        if not dist_index.exists():
            raise SystemExit("已指定跳过前端构建，但 frontend/dist/index.html 不存在。")
        return

    if not node_available():
        if dist_index.exists():
            log("未检测到 Node.js/npm，使用已有 frontend/dist 静态文件继续启动。")
            return
        raise SystemExit("未检测到 Node.js/npm。请安装 Node.js 20 LTS 或 22 LTS 后重试。")

    if args.force_install or not (FRONTEND_DIR / "node_modules").exists():
        run([command_name("npm"), "install"], cwd=FRONTEND_DIR)

    build = run([command_name("npm"), "run", "build"], cwd=FRONTEND_DIR, check=False)
    if build.returncode == 0:
        return

    log("前端构建失败，尝试重新安装依赖后再次构建。")
    run([command_name("npm"), "install"], cwd=FRONTEND_DIR)
    run([command_name("npm"), "run", "build"], cwd=FRONTEND_DIR)


def database_article_count() -> int:
    db_path = DATA_DIR / "news_monitor.db"
    if not db_path.exists():
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("select count(*) from news_articles")
            return int(cursor.fetchone()[0] or 0)
    except sqlite3.Error:
        return 0


def prepare_database(python_path: Path, args: argparse.Namespace) -> None:
    run([str(python_path), "scripts/init_db.py"], cwd=BACKEND_DIR)

    if args.reset_sample or database_article_count() == 0:
        log("数据库为空，写入离线样例数据，确保无网络时也能演示。")
        run(
            [str(python_path), "scripts/run_pipeline.py", "--mode", "sample", "--sample-limit", "80", "--no-history"],
            cwd=BACKEND_DIR,
        )

    if args.live_on_start:
        log("执行一次实时 RSS/API 抓取，网络较慢时可能需要 1-3 分钟。")
        run(
            [
                str(python_path),
                "scripts/run_pipeline.py",
                "--mode",
                "full",
                "--sample-limit",
                "0",
                "--rss-limit",
                str(args.rss_limit),
                "--api-limit",
                str(args.api_limit),
                "--no-sample",
                "--no-batch",
            ],
            cwd=BACKEND_DIR,
            check=False,
        )


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def choose_port(preferred: int) -> int:
    if port_available(preferred):
        return preferred
    for port in range(5001, 5021):
        if port_available(port):
            log(f"端口 {preferred} 已被占用，自动改用 {port}。")
            return port
    raise SystemExit("5001-5020 端口都被占用，请关闭占用端口的程序后重试。")


def wait_for_health(port: int, timeout_seconds: int = 25) -> bool:
    deadline = time.time() + timeout_seconds
    url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.5)
    return False


def start_server(python_path: Path, args: argparse.Namespace) -> int:
    port = choose_port(args.port)
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "app")
    env.setdefault("ENABLE_SPARK", "0")
    env.setdefault("AUTO_FETCH_ENABLED", "1")
    env.setdefault("AUTO_FETCH_INTERVAL_SECONDS", "600")

    command = [
        str(python_path),
        "-m",
        "flask",
        "--app",
        "app",
        "run",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    process = subprocess.Popen(command, cwd=str(BACKEND_DIR), env=env)
    if not wait_for_health(port):
        process.terminate()
        raise SystemExit("Flask 启动超时，请检查终端输出中的错误。")

    url = f"http://127.0.0.1:{port}/"
    log(f"系统已启动: {url}")
    if not args.no_open:
        webbrowser.open(url)

    try:
        process.wait()
    except KeyboardInterrupt:
        log("收到停止信号，正在关闭 Flask 服务。")
        process.terminate()
        process.wait(timeout=10)
        return 0
    return process.returncode or 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一键部署并启动新闻热度监测系统")
    parser.add_argument("--port", type=int, default=5001, help="Flask 启动端口，默认 5001")
    parser.add_argument("--pip-index-url", default=DEFAULT_INDEX_URL, help="pip 镜像源，默认清华源")
    parser.add_argument("--skip-pyspark", action="store_true", help="跳过 pyspark 安装，使用 Pandas 模式")
    parser.add_argument("--skip-frontend", action="store_true", help="跳过前端 npm install/build，直接使用已有 dist")
    parser.add_argument("--force-install", action="store_true", help="强制重新安装前端 node_modules")
    parser.add_argument("--reset-sample", action="store_true", help="重新写入样例数据")
    parser.add_argument("--live-on-start", action="store_true", help="启动前先执行一次实时 RSS/API 抓取")
    parser.add_argument("--rss-limit", type=int, default=30, help="实时抓取每个 RSS 源最多抓取条数")
    parser.add_argument("--api-limit", type=int, default=50, help="实时抓取每个 API 源最多抓取条数")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()


def main() -> int:
    reexec_if_needed()
    args = parse_args()
    assert_project_root()
    ensure_env_file()
    python_path = ensure_backend_venv(args)
    ensure_frontend(args)
    prepare_database(python_path, args)
    return start_server(python_path, args)


if __name__ == "__main__":
    raise SystemExit(main())
