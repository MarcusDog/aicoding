from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
SILVER_DIR = WAREHOUSE_DIR / "silver"
GOLD_DIR = WAREHOUSE_DIR / "gold"
LOG_DIR = ROOT_DIR / "logs"
DUCKDB_PATH = DATA_DIR / "futures_analytics.duckdb"

CFFEX_BASE_URLS = ("http://www.cffex.com.cn", "https://www.cffex.com.cn")
PBC_BASE_URL = "https://www.pbc.gov.cn"
NBS_BASE_URL = "https://www.stats.gov.cn"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
SUPPORTED_PRODUCTS = ("IF", "IH", "IC", "IM")
PRODUCT_NAMES = {
    "IF": "沪深300股指期货",
    "IH": "上证50股指期货",
    "IC": "中证500股指期货",
    "IM": "中证1000股指期货",
}
LICENSE_NOTE = "教学/研究用途，仅保留官方公开数据与来源标识，不做实时再分发。"


@dataclass(frozen=True)
class SourceMetadata:
    name: str
    url: str
    description: str


SOURCE_CATALOG = [
    SourceMetadata(
        name="CFFEX 日统计",
        url="http://www.cffex.com.cn/rtj/",
        description="中国金融期货交易所盘后统计数据，覆盖合约日频行情与持仓指标。",
    ),
    SourceMetadata(
        name="CFFEX 交易所通知",
        url="http://www.cffex.com.cn/jystz/",
        description="交易所通知列表，可用于事件与规则变更说明。",
    ),
    SourceMetadata(
        name="PBC 调查统计司",
        url="https://www.pbc.gov.cn/diaochatongjisi/116219/116225/index.html",
        description="金融统计数据报告，用于 M2、社融等宏观金融指标。",
    ),
    SourceMetadata(
        name="国家统计局数据发布",
        url="https://www.stats.gov.cn/sj/zxfb/",
        description="CPI、PPI、工业增加值等宏观统计发布。",
    ),
]


def ensure_directories() -> None:
    for path in [DATA_DIR, RAW_DIR, WAREHOUSE_DIR, SILVER_DIR, GOLD_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)
