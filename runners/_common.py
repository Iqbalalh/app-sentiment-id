# -*- coding: utf-8 -*-
"""Alur kerja bersama untuk semua runner: muat/scrape data, ambil sampel bila
diminta, lalu jalankan analisis."""
import pandas as pd

from config import data_file
from sentimen.pipeline import analisis


def jalankan_pipeline(platform, scrape_fn, perlu_scrape, sample):
    """Muat data platform (scrape bila perlu) lalu analisis.

    `scrape_fn` adalah callable tanpa argumen yang mengembalikan DataFrame.
    Mengembalikan DataFrame hasil, atau None bila tidak ada data.
    """
    f = data_file(platform)
    if perlu_scrape or not f.exists():
        df = scrape_fn()
        if df is None or len(df) == 0:
            print(f"  Tidak ada data terambil untuk {platform}.")
            return None
        df.to_csv(f, index=False, encoding="utf-8-sig")
        print(f"  Tersimpan {len(df)} baris -> {f}")

    if not f.exists():
        print(f"  Belum ada data untuk {platform}. Jalankan dengan --scrape.")
        return None

    df = pd.read_csv(f)
    if sample and sample < len(df):
        df = df.sample(sample, random_state=42).reset_index(drop=True)
        print(f"  Memakai sampel acak: {len(df)} komentar")
    return analisis(df, platform)
