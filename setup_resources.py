# -*- coding: utf-8 -*-
"""
Unduh resource yang dibutuhkan pipeline (kamus normalisasi slang).
Jalankan sekali setelah clone repo:  python setup_resources.py
"""
import ssl
import urllib.request

from config import COLLOQUIAL_LEXICON, COLLOQUIAL_URL


def download(url, dest):
    if dest.exists():
        print(f"sudah ada: {dest.name}")
        return
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(request, timeout=60, context=ctx).read()
    dest.write_bytes(data)
    print(f"diunduh: {dest.name} ({len(data)} bytes)")


if __name__ == "__main__":
    download(COLLOQUIAL_URL, COLLOQUIAL_LEXICON)
    print("Selesai. Resource siap dipakai.")
