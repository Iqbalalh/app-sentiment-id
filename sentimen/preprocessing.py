# -*- coding: utf-8 -*-
"""
Tahap preprocessing teks (dipakai bersama oleh semua platform):
case folding -> cleansing -> tokenizing -> normalisasi -> filtering -> stemming.

Objek berat (kamus slang, stemmer) dimuat sekali secara lazy agar efisien.
"""
import re
import csv
from functools import lru_cache

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from config import COLLOQUIAL_LEXICON

# Negasi WAJIB dipertahankan (jangan dibuang sebagai stopword)
NEGASI = {"tidak", "tak", "bukan", "belum", "jangan", "tanpa", "kurang"}


@lru_cache(maxsize=1)
def _stopwords():
    sw = set(StopWordRemoverFactory().get_stop_words())
    return sw - NEGASI


@lru_cache(maxsize=1)
def _stemmer():
    return StemmerFactory().create_stemmer()


@lru_cache(maxsize=1)
def muat_kamus_slang():
    """Kamus normalisasi kata tidak baku (slang -> baku)."""
    kamus = {}
    if COLLOQUIAL_LEXICON.exists():
        with open(COLLOQUIAL_LEXICON, encoding="utf-8") as fp:
            for row in csv.DictReader(fp):
                kamus.setdefault(row["slang"].strip(), row["formal"].strip())
    # override / istilah domain + negasi yang sering muncul
    kamus.update({
        "apk": "aplikasi", "app": "aplikasi", "aplikasinya": "aplikasi",
        "gk": "tidak", "ga": "tidak", "gak": "tidak", "ngga": "tidak",
        "nggak": "tidak", "enggak": "tidak", "engga": "tidak", "kga": "tidak",
        "tdk": "tidak", "gabisa": "tidak bisa", "knp": "kenapa",
        "bgt": "banget", "bngt": "banget", "udh": "sudah", "sdh": "sudah",
        "udah": "sudah", "blm": "belum", "bsa": "bisa",
        "sertipikat": "sertifikat", "ngebug": "error", "ngeprank": "menipu",
        "lemot": "lambat", "woi": "", "woii": "", "wooii": "", "dong": "",
    })
    return kamus


# ---------------- fungsi tahap-per-tahap ----------------
def case_folding(teks: str) -> str:
    return teks.lower()


def cleansing(teks: str) -> str:
    teks = re.sub(r"http\S+|www\.\S+", " ", teks)   # URL
    teks = re.sub(r"@\w+", " ", teks)               # mention
    teks = re.sub(r"#\w+", " ", teks)               # hashtag
    teks = re.sub(r"[^a-z\s]", " ", teks)           # angka/emoji/simbol
    teks = re.sub(r"(.)\1{2,}", r"\1", teks)        # elongasi: "bagusss"->"bagus"
    teks = re.sub(r"\s+", " ", teks).strip()
    return teks


def tokenizing(teks: str):
    return teks.split()


def normalisasi(tokens, kamus=None):
    kamus = kamus or muat_kamus_slang()
    hasil = []
    for t in tokens:
        t = kamus.get(t, t)
        hasil.extend(t.split())     # slang bisa jadi 2 kata: "gabisa"->"tidak bisa"
    return hasil


def filtering(tokens):
    sw = _stopwords()
    return [t for t in tokens if t not in sw and len(t) > 1]


def stemming(tokens):
    stem = _stemmer()
    return [stem.stem(t) for t in tokens]


def proses(teks: str):
    """Jalankan seluruh tahap. Mengembalikan (tokens_norm, text_clean).

    - tokens_norm : token ternormalisasi (negasi terjaga) -> untuk analisis lanjutan
    - text_clean  : teks bersih + stopword removal + stemming -> untuk wordcloud/frekuensi
    """
    kamus = muat_kamus_slang()
    norm = normalisasi(tokenizing(cleansing(case_folding(teks))), kamus)
    clean = stemming(filtering(norm))
    return norm, " ".join(clean)
