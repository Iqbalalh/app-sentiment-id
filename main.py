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
from setup_resources import download


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
    download(config.COLLOQUIAL_URL, config.COLLOQUIAL_LEXICON)

    # 2) Jalankan tiap platform
    platforms = [args.only] if args.only else list(PLATFORMS)
    succeeded, skipped = [], []
    for name in platforms:
        print(f"\n{'=' * 52}\n  PLATFORM: {name.upper()}\n{'=' * 52}")
        try:
            result = get_runner(name).run(scrape=args.scrape, sample=args.sample)
            (succeeded if result is not None else skipped).append(name)
        except Exception as err:
            print(f"  [LEWATI] {name}: {err}")
            skipped.append(name)

    # 3) Ringkasan
    print(f"\n{'=' * 52}\n  RINGKASAN\n{'=' * 52}")
    if succeeded:
        print(f"  Berhasil  : {', '.join(succeeded)}")
        for name in succeeded:
            print(f"    - {config.output_dir(name)}")
    if skipped:
        print(f"  Dilewati  : {', '.join(skipped)} "
              f"(belum ada data / belum dikonfigurasi di .env)")


if __name__ == "__main__":
    main()
