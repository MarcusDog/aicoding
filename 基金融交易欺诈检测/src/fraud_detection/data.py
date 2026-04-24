import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from sklearn.datasets import fetch_openml

from fraud_detection.settings import EXTERNAL_DATA_DIR, RAW_DATA_DIR, ensure_directories


OPENML_DATA_ID = 1597
SEC_NMFP_PAGE = "https://www.sec.gov/data-research/sec-markets-data/dera-form-n-mfp-data-sets"
SEC_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sec.gov/",
}
SEC_FALLBACK_URLS = [
    "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/20260209-20260306_nmfp.zip",
]


def _fetch_openml_frame() -> pd.DataFrame:
    try:
        bunch = fetch_openml(data_id=OPENML_DATA_ID, as_frame=True, parser="auto")
    except TypeError:
        bunch = fetch_openml(data_id=OPENML_DATA_ID, as_frame=True)

    frame = bunch.frame.copy()
    if "Class" not in frame.columns:
        lowered = {col.lower(): col for col in frame.columns}
        if "class" in lowered:
            frame = frame.rename(columns={lowered["class"]: "Class"})
    if "Class" not in frame.columns:
        raise ValueError("Downloaded dataset does not contain 'Class' column.")
    return frame


def download_creditcard_dataset(force: bool = False) -> tuple[Path, dict[str, Any]]:
    ensure_directories()
    dataset_path = RAW_DATA_DIR / "creditcard.csv"
    metadata_path = RAW_DATA_DIR / "creditcard.metadata.json"

    if dataset_path.exists() and metadata_path.exists() and not force:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return dataset_path, metadata

    frame = _fetch_openml_frame()
    frame.to_csv(dataset_path, index=False)

    metadata = {
        "dataset_name": "creditcard",
        "source": "OpenML data_id=1597",
        "openml_data_id": OPENML_DATA_ID,
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "target_column": "Class",
        "fraud_count": int(frame["Class"].astype(int).sum()),
        "fraud_ratio": float(frame["Class"].astype(int).mean()),
        "references": [
            "Dal Pozzolo A, Caelen O, Le Borgne Y A, et al. Expert Systems with Applications, 2014",
            "https://www.openml.org/",
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return dataset_path, metadata


def download_latest_sec_nmfp(force: bool = False) -> Path:
    ensure_directories()
    sec_dir = EXTERNAL_DATA_DIR / "sec"
    candidate_urls: list[str] = []

    try:
        page_response = requests.get(SEC_NMFP_PAGE, headers=SEC_HEADERS, timeout=60)
        page_response.raise_for_status()
        matches = re.findall(r'href="([^"]+?\.zip)"', page_response.text, flags=re.IGNORECASE)
        candidate_urls.extend(urljoin(SEC_NMFP_PAGE, href) for href in matches)
    except requests.HTTPError:
        pass

    candidate_urls.extend(SEC_FALLBACK_URLS)

    for latest_url in candidate_urls:
        file_name = Path(latest_url).name
        output_path = sec_dir / file_name
        if output_path.exists() and not force:
            return output_path
        try:
            with requests.get(latest_url, headers=SEC_HEADERS, timeout=120, stream=True) as response:
                response.raise_for_status()
                with output_path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
            return output_path
        except requests.RequestException:
            if output_path.exists():
                output_path.unlink()
            continue

    raise ValueError("Unable to download SEC N-MFP archive from official sources.")


def load_creditcard_data(path: Path | None = None) -> pd.DataFrame:
    dataset_path = path or (RAW_DATA_DIR / "creditcard.csv")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    frame = pd.read_csv(dataset_path)
    frame["Class"] = frame["Class"].astype(int)
    return frame
