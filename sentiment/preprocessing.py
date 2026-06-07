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

from config import COLLOQUIAL_LEXICON, STEMMING

# Negasi WAJIB dipertahankan (jangan dibuang sebagai stopword)
NEGATION = {"tidak", "tak", "bukan", "belum", "jangan", "tanpa", "kurang"}


@lru_cache(maxsize=1)
def _stopwords():
    sw = set(StopWordRemoverFactory().get_stop_words())
    return sw - NEGATION


@lru_cache(maxsize=1)
def _stemmer():
    return StemmerFactory().create_stemmer()


@lru_cache(maxsize=1)
def load_slang_dict():
    """Kamus normalisasi kata tidak baku (slang -> baku)."""
    slang = {}
    if COLLOQUIAL_LEXICON.exists():
        with open(COLLOQUIAL_LEXICON, encoding="utf-8") as fp:
            for row in csv.DictReader(fp):
                slang.setdefault(row["slang"].strip(), row["formal"].strip())
    # override / istilah domain + negasi yang sering muncul
    slang.update({
        "apk": "aplikasi", "app": "aplikasi", "aplikasinya": "aplikasi",
        "gk": "tidak", "ga": "tidak", "gak": "tidak", "ngga": "tidak",
        "nggak": "tidak", "enggak": "tidak", "engga": "tidak", "kga": "tidak",
        "tdk": "tidak", "gabisa": "tidak bisa", "knp": "kenapa",
        "bgt": "banget", "bngt": "banget", "udh": "sudah", "sdh": "sudah",
        "udah": "sudah", "blm": "belum", "bsa": "bisa",
        "sertipikat": "sertifikat", "ngebug": "error", "ngeprank": "menipu",
        "lemot": "lambat", "woi": "", "woii": "", "wooii": "", "dong": "",
    })
    return slang


# ---------------- fungsi tahap-per-tahap ----------------
def case_folding(text: str) -> str:
    return text.lower()


def cleansing(text: str) -> str:
    text = re.sub(r"http\S+|www\.\S+", " ", text)   # URL
    text = re.sub(r"@\w+", " ", text)               # mention
    text = re.sub(r"#\w+", " ", text)               # hashtag
    text = re.sub(r"[^a-z\s]", " ", text)           # angka/emoji/simbol
    text = re.sub(r"(.)\1{2,}", r"\1", text)        # elongasi: "bagusss"->"bagus"
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenizing(text: str):
    return text.split()


def normalize(tokens, slang=None):
    slang = slang or load_slang_dict()
    result = []
    for token in tokens:
        token = slang.get(token, token)
        result.extend(token.split())    # slang bisa jadi 2 kata: "gabisa"->"tidak bisa"
    return result


def filtering(tokens):
    sw = _stopwords()
    return [t for t in tokens if t not in sw and len(t) > 1]


def stemming(tokens):
    stemmer = _stemmer()
    return [stemmer.stem(t) for t in tokens]


def process(text: str):
    """Jalankan seluruh tahap. Mengembalikan (tokens_norm, text_clean).

    - tokens_norm : token ternormalisasi (negasi terjaga) -> untuk analisis lanjutan
    - text_clean  : teks bersih + stopword removal (+ stemming bila STEMMING=true)
                    -> untuk wordcloud/frekuensi

    Stemming dimatikan secara default agar kata tetap utuh/natural pada laporan
    (mis. "jaringan" tidak menjadi "jaring"). Aktifkan lewat STEMMING=true di .env.
    """
    slang = load_slang_dict()
    norm = normalize(tokenizing(cleansing(case_folding(text))), slang)
    tokens = filtering(norm)
    if STEMMING:
        tokens = stemming(tokens)
    return norm, " ".join(tokens)
