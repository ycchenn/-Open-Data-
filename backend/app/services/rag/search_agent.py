"""Search agent：只在政府官方網域內搜尋，補足本地知識庫的不足。"""
import logging

import requests

logger = logging.getLogger(__name__)

OFFICIAL_SITES = [
    "moa.gov.tw",        # 農業部
    "tactri.gov.tw",     # 農業藥物試驗所
    "pesticide.aphia.gov.tw",  # 農藥資訊服務網
    "aphia.gov.tw",      # 動植物防疫檢疫署
    "afa.gov.tw",        # 農糧署
    "tari.gov.tw",       # 農業試驗所
    "data.gov.tw",       # 政府資料開放平臺
]
CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


class SearchAgent:
    def __init__(self, api_key: str, engine_id: str):
        self.api_key = api_key
        self.engine_id = engine_id

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.engine_id)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.available:
            return []
        site_filter = " OR ".join(f"site:{s}" for s in OFFICIAL_SITES)
        try:
            resp = requests.get(
                CSE_ENDPOINT,
                params={"key": self.api_key, "cx": self.engine_id, "q": f"{query} ({site_filter})", "num": top_k},
                timeout=8,
            )
            resp.raise_for_status()
        except requests.RequestException:
            logger.exception("Search agent 查詢失敗")
            return []
        return [
            {"text": item.get("snippet", ""), "source": item.get("title", ""), "url": item.get("link")}
            for item in resp.json().get("items", [])
            if any(site in item.get("link", "") for site in OFFICIAL_SITES)
        ]
