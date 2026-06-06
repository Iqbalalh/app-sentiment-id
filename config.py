# -*- coding: utf-8 -*-
"""Konfigurasi terpusat. Seluruh nilai dapat diatur lewat berkas .env
sehingga proyek ini generik untuk aplikasi apa pun yang ingin dianalisis."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _ids(raw: str):
    """Parse daftar id dari string '111, 222 333' -> [111, 222, 333]."""
    return [int(x) for x in raw.replace(",", " ").split() if x.strip().isdigit()]


# ---------------- Identitas aplikasi yang dianalisis ----------------
APP_NAME = _env("APP_NAME", "Aplikasi")

# ---------------- Direktori (semua relatif terhadap root proyek) ----------------
RESOURCES_DIR = BASE / _env("RESOURCES_DIR", "resources")   # kamus & berkas unduhan
DATA_DIR = BASE / _env("DATA_DIR", "data")                  # data mentah hasil scraping
OUTPUT_DIR = BASE / _env("OUTPUT_DIR", "output")            # hasil analisis & grafik
for _d in (RESOURCES_DIR, DATA_DIR, OUTPUT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------- Resource (diunduh oleh setup_resources.py) ----------------
COLLOQUIAL_LEXICON = RESOURCES_DIR / "colloquial_lexicon.csv"
COLLOQUIAL_URL = _env(
    "COLLOQUIAL_URL",
    "https://raw.githubusercontent.com/nasalsabila/kamus-alay/"
    "master/colloquial-indonesian-lexicon.csv",
)

# ---------------- Play Store ----------------
PLAYSTORE_APP_ID = _env("PLAYSTORE_APP_ID")
PLAYSTORE_LANG = _env("PLAYSTORE_LANG", "id")
PLAYSTORE_COUNTRY = _env("PLAYSTORE_COUNTRY", "id")

# ---------------- App Store ----------------
APPSTORE_APP_ID = _env("APPSTORE_APP_ID")
APPSTORE_COUNTRY = _env("APPSTORE_COUNTRY", "id")

# ---------------- TikTok ----------------
TIKTOK_MS_TOKEN = _env("TIKTOK_MS_TOKEN")
TIKTOK_VIDEO_IDS = _ids(_env("TIKTOK_VIDEO_IDS"))

# ---------------- Model ----------------
MODEL_NAME = _env("MODEL_NAME", "cardiffnlp/twitter-xlm-roberta-base-sentiment")


# ---------------- Path helper (isolasi per platform) ----------------
def data_file(platform: str) -> Path:
    """Lokasi berkas data mentah, mis. data/data_playstore.csv"""
    return DATA_DIR / f"data_{platform}.csv"


def output_dir(platform: str) -> Path:
    """Folder output khusus platform, mis. output/playstore/"""
    d = OUTPUT_DIR / platform
    d.mkdir(parents=True, exist_ok=True)
    return d
