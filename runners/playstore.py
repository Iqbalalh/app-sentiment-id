# -*- coding: utf-8 -*-
"""Runner analisis sentimen PLAY STORE (terisolasi).
Hanya membaca/menulis data/data_playstore.csv dan folder output/playstore/.

Contoh:
    python -m runners.playstore                 # analisis data yang sudah ada
    python -m runners.playstore --scrape        # scrape ulang lalu analisis
    python -m runners.playstore --scrape --jumlah 5000
    python -m runners.playstore --sample 1500   # ambil sampel acak
"""
import argparse

from runners._common import jalankan_pipeline
from scrapers import playstore as scraper

PLATFORM = "playstore"


def jalankan(scrape=False, jumlah=2000, sample=0):
    def _scrape():
        print(f"Scraping Play Store ({jumlah} ulasan)...")
        return scraper.scrape(jumlah)

    return jalankan_pipeline(PLATFORM, _scrape, scrape, sample)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrape", action="store_true", help="scrape ulang data")
    ap.add_argument("--jumlah", type=int, default=2000, help="jumlah ulasan saat scrape")
    ap.add_argument("--sample", type=int, default=0, help="ambil N sampel acak (0 = semua)")
    args = ap.parse_args()
    jalankan(scrape=args.scrape, jumlah=args.jumlah, sample=args.sample)


if __name__ == "__main__":
    main()
