import pandas as pd

from ingest.sources.cffex import CffexClient
from ingest.sources.nbs import NbsClient
from ingest.sources.pbc import PbcClient


def test_cffex_parse_daily_xml_filters_index_futures() -> None:
    xml = b"""
    <dailydatas>
      <dailydata>
        <instrumentid>IF2606</instrumentid>
        <tradingday>20260318</tradingday>
        <openprice>3800</openprice>
        <highestprice>3820</highestprice>
        <lowestprice>3790</lowestprice>
        <closeprice>3810</closeprice>
        <preopeninterest>100</preopeninterest>
        <openinterest>120</openinterest>
        <presettlementprice>3795</presettlementprice>
        <settlementprice>3808</settlementprice>
        <volume>500</volume>
        <turnover>123456</turnover>
        <productid>IF</productid>
      </dailydata>
      <dailydata>
        <instrumentid>HO2603-C-2250</instrumentid>
        <tradingday>20260318</tradingday>
        <productid>HO</productid>
      </dailydata>
    </dailydatas>
    """
    df = CffexClient().parse_daily_xml(xml, "http://example.com/index.xml")
    assert len(df) == 1
    assert df.iloc[0]["instrument_id"] == "IF2606"
    assert df.iloc[0]["open_interest_change"] == 20


def test_pbc_parse_article_extracts_key_metrics() -> None:
    html = """
    <html><body>
    2026年2月金融统计数据报告
    社会融资规模存量同比增长8.2%
    广义货币(M2)余额349.22万亿元，同比增长9%。
    狭义货币(M1)余额115.93万亿元，同比增长5.9%。
    人民币贷款余额277.52万亿元，同比增长6%。
    同业拆借月加权平均利率为1.4%。
    </body></html>
    """
    df = PbcClient()._parse_article("2026年2月金融统计数据报告", "https://example.com", html)
    assert {"m2_yoy", "m1_yoy", "loan_yoy", "interbank_rate"}.issubset(set(df["series_name"]))


def test_nbs_parse_article_extracts_cpi() -> None:
    html = "<html><body>2026年2月份居民消费价格同比上涨1.3%</body></html>"
    df = NbsClient()._parse_article("cpi_yoy", "2026年2月份居民消费价格同比上涨1.3%", "https://example.com", html)
    assert len(df) == 1
    assert df.iloc[0]["value"] == 1.3
