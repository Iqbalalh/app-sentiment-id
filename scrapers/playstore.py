# -*- coding: utf-8 -*-
"""Scraper ulasan Google Play Store (google-play-scraper)."""
import pandas as pd
from google_play_scraper import reviews, Sort

from config import PLAYSTORE_APP_ID, PLAYSTORE_LANG, PLAYSTORE_COUNTRY


def scrape(count: int = 2000, app_id: str = PLAYSTORE_APP_ID) -> pd.DataFrame:
    if not app_id:
        raise RuntimeError("PLAYSTORE_APP_ID kosong. Isi di file .env terlebih dahulu.")
    data, _ = reviews(app_id, lang=PLAYSTORE_LANG, country=PLAYSTORE_COUNTRY,
                      sort=Sort.NEWEST, count=count)
    df = pd.DataFrame(data)[["userName", "content", "score", "at"]].rename(
        columns={"userName": "username", "content": "comment",
                 "score": "rating", "at": "tanggal"})
    df["sumber"] = "playstore"
    return df
