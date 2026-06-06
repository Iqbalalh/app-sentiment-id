# -*- coding: utf-8 -*-
"""Runner analisis sentimen PLAY STORE (terisolasi).
Hanya membaca/menulis data/data_playstore.csv dan folder output/playstore/.

Contoh:
    python -m runners.playstore                 # analisis data yang sudah ada
    python -m runners.playstore --scrape        # scrape ulang lalu analisis
    python -m runners.playstore --scrape --count 5000
    python -m runners.playstore --sample 1500   # ambil sampel acak
"""
import argparse

from runners._common import run_pipeline
from scrapers import playstore as scraper

PLATFORM = "playstore"


def run(scrape=False, count=2000, sample=0):
    def _scrape():
        print(f"Scraping Play Store ({count} ulasan)...")
        return scraper.scrape(count)

    return run_pipeline(PLATFORM, _scrape, scrape, sample)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrape", action="store_true", help="scrape ulang data")
    ap.add_argument("--count", type=int, default=2000, help="jumlah ulasan saat scrape")
    ap.add_argument("--sample", type=int, default=0, help="ambil N sampel acak (0 = semua)")
    args = ap.parse_args()
    run(scrape=args.scrape, count=args.count, sample=args.sample)


if __name__ == "__main__":
    main()
