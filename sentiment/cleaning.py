# -*- coding: utf-8 -*-
"""
Pembersihan komentar sebelum klasifikasi dan pelacakan provenance data.

Tujuan utama: membuang komentar tak bermakna dan komentar spam/duplikat
(indikasi buzzer yang menyalin-tempel teks yang sama) agar analisis tidak bias.
Mengembalikan DataFrame bersih beserta ringkasan berapa komentar di-scrap,
dipakai, dan dibuang (per alasan).
"""
import re

from sentiment.preprocessing import case_folding, cleansing

# Kunci deduplikasi: samakan teks dengan mengabaikan huruf besar/kecil, emoji,
# tanda baca, dan spasi berlebih, sehingga "Bagus!!!" == "bagus 👍" == "BAGUS".
_NONALNUM = re.compile(r"[^a-z0-9]+")


def _dedup_key(text: str) -> str:
    return _NONALNUM.sub(" ", text.lower()).strip()


def prepare(df, n_scraped=None):
    """Bersihkan kolom `comment` lalu susun DataFrame siap analisis.

    Tahap: buang kosong/NaN -> buang komentar tanpa konten teks (emoji/simbol/
    angka saja) -> buang duplikat (spam/buzzer). Mengembalikan (df, provenance).
    """
    df = df.copy()
    if "comment" not in df.columns:
        raise ValueError("DataFrame harus punya kolom 'comment'.")
    df["comment"] = df["comment"].astype(str).str.strip()
    n_input = len(df)

    # 1) kosong / 'nan'
    mask_empty = (df["comment"].str.len() == 0) | (df["comment"].str.lower() == "nan")
    n_empty = int(mask_empty.sum())
    df = df[~mask_empty]

    # 2) tanpa konten teks (hanya emoji/simbol/angka)
    cleaned = df["comment"].map(lambda t: cleansing(case_folding(t)))
    mask_noalpha = cleaned.str.len() == 0
    n_noalpha = int(mask_noalpha.sum())
    df = df[~mask_noalpha]

    # 3) duplikat (indikasi spam/buzzer copy-paste) -> simpan kemunculan pertama
    keys = df["comment"].map(_dedup_key)
    mask_dup = keys.duplicated(keep="first")
    n_dup = int(mask_dup.sum())
    df = df[~mask_dup]

    df = df.reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))

    scraped = int(n_scraped) if n_scraped is not None else n_input
    provenance = {
        "scraped": scraped,          # total komentar mentah hasil scraping
        "diproses": n_input,         # masuk pembersihan (setelah sampling, bila ada)
        "kosong": n_empty,           # dibuang: kosong / NaN
        "tanpa_teks": n_noalpha,     # dibuang: hanya emoji/simbol/angka
        "spam_duplikat": n_dup,      # dibuang: duplikat (buzzer)
        "dipakai": int(len(df)),     # akhirnya dianalisis
        "dibuang": int(n_input - len(df)),
    }
    return df, provenance
