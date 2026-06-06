# -*- coding: utf-8 -*-
"""Runner analisis sentimen TIKTOK (terisolasi).
Hanya membaca/menulis data/data_tiktok.csv dan folder output/tiktok/.

Prasyarat scraping: pip install TikTokApi && python -m playwright install chromium
ms_token diambil dari .env (TIKTOK_MS_TOKEN).

Contoh:
    python -m runners.tiktok                     # analisis data yang sudah ada
    python -m runners.tiktok --scrape            # scrape ulang lalu analisis
    python -m runners.tiktok --scrape --jumlah 500
"""
import argparse

from runners._common import jalankan_pipeline
from scrapers import tiktok as scraper

PLATFORM = "tiktok"


def jalankan(scrape=False, jumlah=300, sample=0):
    def _scrape():
        print("Scraping TikTok...")
        return scraper.scrape(jumlah=jumlah)

    return jalankan_pipeline(PLATFORM, _scrape, scrape, sample)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrape", action="store_true", help="scrape ulang data")
    ap.add_argument("--jumlah", type=int, default=300, help="komentar per video")
    ap.add_argument("--sample", type=int, default=0, help="ambil N sampel acak (0 = semua)")
    args = ap.parse_args()
    jalankan(scrape=args.scrape, jumlah=args.jumlah, sample=args.sample)


if __name__ == "__main__":
    main()
