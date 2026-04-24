from __future__ import annotations

import argparse
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = Path("C:/codex-runtime")
KAFKA_VERSION = "3.7.1"
SCALA_VERSION = "2.13"
ARCHIVE_NAME = f"kafka_{SCALA_VERSION}-{KAFKA_VERSION}.tgz"
DOWNLOAD_URL = f"https://archive.apache.org/dist/kafka/{KAFKA_VERSION}/{ARCHIVE_NAME}"
INSTALL_DIR = RUNTIME_DIR / f"kafka_{SCALA_VERSION}-{KAFKA_VERSION}"
ARCHIVE_PATH = RUNTIME_DIR / ARCHIVE_NAME
CONFIG_PATH = INSTALL_DIR / "config" / "kraft" / "codex-server.properties"
LOG_DIR = INSTALL_DIR / "data" / "logs"
METADATA_DIR = INSTALL_DIR / "data" / "metadata"
PID_PATH = INSTALL_DIR / "kafka.pid"
OUT_LOG = INSTALL_DIR / "kafka.out.log"
ERR_LOG = INSTALL_DIR / "kafka.err.log"
CLUSTER_ID_PATH = INSTALL_DIR / "data" / "cluster.id"


SERVER_CONFIG = """
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@127.0.0.1:9093
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://172.27.128.1:9092
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
inter.broker.listener.name=PLAINTEXT
controller.listener.names=CONTROLLER
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs={log_dirs}
metadata.log.dir={metadata_dir}
num.partitions=3
num.recovery.threads.per.data.dir=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
group.initial.rebalance.delay.ms=0
auto.create.topics.enable=true
delete.topic.enable=true
log.retention.hours=168
"""


def ensure_runtime() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


def download_archive(force: bool = False) -> None:
    ensure_runtime()
    if ARCHIVE_PATH.exists() and not force:
        return
    with urllib.request.urlopen(DOWNLOAD_URL) as response, ARCHIVE_PATH.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def extract_archive(force: bool = False) -> None:
    if INSTALL_DIR.exists() and not force:
        return
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        archive.extractall(RUNTIME_DIR)


def write_config() -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        SERVER_CONFIG.format(
            log_dirs=str(LOG_DIR).replace("\\", "/"),
            metadata_dir=str(METADATA_DIR).replace("\\", "/"),
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def kafka_storage_bat() -> Path:
    return INSTALL_DIR / "bin" / "windows" / "kafka-storage.bat"


def kafka_server_start_bat() -> Path:
    return INSTALL_DIR / "bin" / "windows" / "kafka-server-start.bat"


def kafka_server_stop_bat() -> Path:
    return INSTALL_DIR / "bin" / "windows" / "kafka-server-stop.bat"


def kafka_classpath() -> str:
    return f"{INSTALL_DIR / 'libs' / '*'}"


def log4j_opt() -> str:
    log4j_path = (INSTALL_DIR / "config" / "log4j.properties").resolve().as_posix()
    return f"-Dlog4j.configuration=file:/{log4j_path}"


def ensure_cluster_id() -> str:
    if CLUSTER_ID_PATH.exists():
        return CLUSTER_ID_PATH.read_text(encoding="utf-8").strip()
    result = subprocess.run(
        ["java", "-cp", kafka_classpath(), "kafka.tools.StorageTool", "random-uuid"],
        cwd=str(INSTALL_DIR),
        capture_output=True,
        text=True,
        check=True,
    )
    cluster_id = result.stdout.strip().splitlines()[-1].strip()
    CLUSTER_ID_PATH.parent.mkdir(parents=True, exist_ok=True)
    CLUSTER_ID_PATH.write_text(cluster_id, encoding="utf-8")
    return cluster_id


def format_storage() -> None:
    cluster_id = ensure_cluster_id()
    subprocess.run(
        [
            "java",
            "-cp",
            kafka_classpath(),
            "kafka.tools.StorageTool",
            "format",
            "-t",
            cluster_id,
            "-c",
            str(CONFIG_PATH),
            "--ignore-formatted",
        ],
        cwd=str(INSTALL_DIR),
        check=True,
    )


def start_kafka() -> None:
    if PID_PATH.exists():
        print(f"Kafka pid file already exists: {PID_PATH}")
        return
    with OUT_LOG.open("ab") as stdout_handle, ERR_LOG.open("ab") as stderr_handle:
        process = subprocess.Popen(
            [
                "java",
                "-Xms512M",
                "-Xmx1G",
                log4j_opt(),
                "-cp",
                kafka_classpath(),
                "kafka.Kafka",
                str(CONFIG_PATH),
            ],
            cwd=str(INSTALL_DIR),
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    PID_PATH.write_text(str(process.pid), encoding="utf-8")
    print(f"Kafka started with pid {process.pid}")


def stop_kafka() -> None:
    if PID_PATH.exists():
        try:
            pid = int(PID_PATH.read_text(encoding="utf-8").strip())
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
        finally:
            PID_PATH.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup and manage local Kafka (KRaft) runtime.")
    parser.add_argument("action", choices=["install", "start", "stop", "restart"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.action in {"install", "start", "restart"}:
        download_archive(force=args.force)
        extract_archive(force=args.force)
        write_config()
        format_storage()

    if args.action == "install":
        print(f"Kafka installed at: {INSTALL_DIR}")
        return
    if args.action == "restart":
        stop_kafka()
        start_kafka()
        return
    if args.action == "start":
        start_kafka()
        return
    if args.action == "stop":
        stop_kafka()


if __name__ == "__main__":
    main()
