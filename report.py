# -*- coding: utf-8 -*-
"""Hasilkan laporan analisis (Markdown) dari output klasifikasi yang sudah ada.
Tidak menjalankan model — hanya membaca output/<platform>/hasil_sentimen_final.csv.

Menulis:
  - output/<platform>/analisis_<platform>.md   (per platform)
  - output/analisis_gabungan.md                (gabungan + kesimpulan akhir)

Contoh:
    python report.py                  # semua platform yang punya output
    python report.py --only playstore # satu platform (tanpa laporan gabungan)
"""
import argparse

from runners import PLATFORMS
from sentiment.report import write_platform_report, write_combined_report


def main():
    ap = argparse.ArgumentParser(description="Hasilkan laporan analisis sentimen.")
    ap.add_argument("--only", choices=list(PLATFORMS),
                    help="hanya satu platform (laporan gabungan dilewati)")
    args = ap.parse_args()

    if args.only:
        path = write_platform_report(args.only)
        print(f"Laporan tersimpan: {path}" if path
              else f"Tidak ada output untuk {args.only}. Jalankan analisis dulu.")
        return

    print("Membuat laporan per platform...")
    found = False
    for p in PLATFORMS:
        path = write_platform_report(p)
        if path:
            print(f"  - {path}")
            found = True
    if not found:
        print("  Tidak ada output yang bisa dianalisis. Jalankan 'python main.py' dulu.")
        return

    print("Membuat laporan gabungan...")
    combined = write_combined_report(list(PLATFORMS))
    print(f"  - {combined}" if combined else "  (tidak ada data untuk digabung)")


if __name__ == "__main__":
    main()
