# -*- coding: utf-8 -*-
"""Runner analisis sentimen APP STORE (terisolasi).
Hanya membaca/menulis data/data_appstore.csv dan folder output/appstore/.

Contoh:
    python -m runners.appstore                  # analisis data yang sudah ada
    python -m runners.appstore --scrape         # scrape ulang lalu analisis
    python -m runners.appstore --scrape --pages 10
"""
import argparse

from runners._common import run_pipeline
from scrapers import appstore as scraper

PLATFORM = "appstore"


def run(scrape=False, pages=10, sample=0):
    def _scrape():
        print("Scraping App Store (RSS)...")
        return scraper.scrape(max_pages=pages)

    return run_pipeline(PLATFORM, _scrape, scrape, sample)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrape", action="store_true", help="scrape ulang data")
    ap.add_argument("--pages", type=int, default=10, help="maksimal halaman RSS (1 hal ~50 ulasan)")
    ap.add_argument("--sample", type=int, default=0, help="ambil N sampel acak (0 = semua)")
    args = ap.parse_args()
    run(scrape=args.scrape, pages=args.pages, sample=args.sample)


if __name__ == "__main__":
    main()
