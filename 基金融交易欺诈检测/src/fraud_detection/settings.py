from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
METRICS_DIR = ARTIFACTS_DIR / "metrics"
FIGURES_DIR = ARTIFACTS_DIR / "figures"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
STREAMING_DIR = ARTIFACTS_DIR / "streaming"
REPORTS_DIR = PROJECT_ROOT / "reports"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
KAFKA_DIR = RUNTIME_DIR / "kafka"
MODELS_DIR = PROJECT_ROOT / "models"


def ensure_directories() -> None:
    for path in [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        ARTIFACTS_DIR,
        METRICS_DIR,
        FIGURES_DIR,
        SCREENSHOTS_DIR,
        STREAMING_DIR,
        REPORTS_DIR,
        RUNTIME_DIR,
        KAFKA_DIR,
        MODELS_DIR,
        EXTERNAL_DATA_DIR / "sec",
    ]:
        path.mkdir(parents=True, exist_ok=True)
