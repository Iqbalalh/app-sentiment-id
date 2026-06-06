# -*- coding: utf-8 -*-
"""App Sentiment ID — entrypoint utama.

Menjalankan seluruh pipeline dari awal sampai akhir:
  1. Memastikan resource (kamus normalisasi) tersedia.
  2. Untuk tiap platform: scrape (opsional) -> preprocessing -> klasifikasi -> visualisasi.
  3. Menampilkan ringkasan lokasi hasil.

Contoh:
    python main.py                      # analisis semua platform dari data yang ada
    python main.py --scrape             # ambil data terbaru semua platform lalu analisis
    python main.py --only playstore     # jalankan satu platform saja
    python main.py --scrape --sample 1500
"""
import argparse

import config
from runners import PLATFORMS, get_runner
from setup_resources import unduh


def main():
    ap = argparse.ArgumentParser(
        description="App Sentiment ID — jalankan seluruh pipeline analisis sentimen.")
    ap.add_argument("--scrape", action="store_true",
                    help="ambil data terbaru sebelum analisis")
    ap.add_argument("--only", choices=list(PLATFORMS),
                    help="jalankan satu platform saja (default: semua)")
    ap.add_argument("--sample", type=int, default=0,
                    help="ambil N komentar acak per platform (0 = semua)")
    args = ap.parse_args()

    print("=" * 52)
    print(f"  App Sentiment ID — {config.APP_NAME}")
    print("=" * 52)

    # 1) Resource
    print("\n[Resource] Memastikan kamus normalisasi tersedia...")
    unduh(config.COLLOQUIAL_URL, config.COLLOQUIAL_LEXICON)

    # 2) Jalankan tiap platform
    platforms = [args.only] if args.only else list(PLATFORMS)
    berhasil, dilewati = [], []
    for nama in platforms:
        print(f"\n{'=' * 52}\n  PLATFORM: {nama.upper()}\n{'=' * 52}")
        try:
            hasil = get_runner(nama).jalankan(scrape=args.scrape, sample=args.sample)
            (berhasil if hasil is not None else dilewati).append(nama)
        except Exception as e:
            print(f"  [LEWATI] {nama}: {e}")
            dilewati.append(nama)

    # 3) Ringkasan
    print(f"\n{'=' * 52}\n  RINGKASAN\n{'=' * 52}")
    if berhasil:
        print(f"  Berhasil  : {', '.join(berhasil)}")
        for nama in berhasil:
            print(f"    - {config.output_dir(nama)}")
    if dilewati:
        print(f"  Dilewati  : {', '.join(dilewati)} "
              f"(belum ada data / belum dikonfigurasi di .env)")


if __name__ == "__main__":
    main()
