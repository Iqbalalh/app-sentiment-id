# -*- coding: utf-8 -*-
"""
Scraper ulasan Apple App Store via RSS "Customer Reviews" resmi Apple
(endpoint JSON publik, hanya butuh pustaka bawaan Python).
"""
import json
import urllib.request
import pandas as pd

from config import APPSTORE_APP_ID, APPSTORE_COUNTRY


def scrape(app_id: str = APPSTORE_APP_ID, country: str = APPSTORE_COUNTRY,
           max_halaman: int = 10) -> pd.DataFrame:
    if not app_id:
        raise RuntimeError("APPSTORE_APP_ID kosong. Isi di file .env terlebih dahulu.")
    rows = []
    for page in range(1, max_halaman + 1):
        url = (f"https://itunes.apple.com/{country}/rss/customerreviews/"
               f"id={app_id}/sortBy=mostRecent/page={page}/json")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
        except Exception as e:
            print(f"  halaman {page}: gagal ({e})")
            break
        revs = [e for e in data.get("feed", {}).get("entry", []) if "im:rating" in e]
        if not revs:
            break
        for e in revs:
            rows.append({
                "username": e.get("author", {}).get("name", {}).get("label", ""),
                "comment": e.get("content", {}).get("label", ""),
                "rating": int(e.get("im:rating", {}).get("label", 0)),
                "judul": e.get("title", {}).get("label", ""),
                "sumber": "appstore",
            })
        print(f"  halaman {page}: {len(revs)} ulasan")
    return pd.DataFrame(rows)
