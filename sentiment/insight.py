# -*- coding: utf-8 -*-
"""
Analisis lanjutan dari output klasifikasi (output/<platform>/hasil_sentimen_final.csv).

Mengekstrak: statistik ringkas, kata & frasa dominan per sentimen, pemetaan
aspek (lewat lexicon), serta kutipan komentar paling representatif. Murni
berbasis data/aturan, tanpa model atau layanan eksternal.
"""
import re
from collections import Counter

import pandas as pd

from config import output_dir

SENTIMENTS = ["positif", "netral", "negatif"]

# Lexicon aspek — generik untuk aplikasi apa pun. Dipindai pada komentar mentah
# (huruf kecil). Tiap aspek punya daftar kata/frasa penanda.
ASPECTS = {
    "Login & Akun": ["login", "log in", "masuk", "daftar", "regist", "akun",
                     "password", "kata sandi", "sandi", "otp", "verifikasi"],
    "Error & Bug": ["error", "eror", "bug", "ngebug", "crash", "force close",
                    "keluar sendiri", "gagal", "rusak", "tidak bisa", "gabisa",
                    "ga bisa", "gak bisa", "macet", "hang", "lag", "ngelag"],
    "Performa & Kecepatan": ["lambat", "lemot", "lelet", "loading", "lama",
                             "berat", "cepat", "ringan", "lancar", "responsif"],
    "Update & Versi": ["update", "versi", "pembaruan", "perbarui", "upgrade"],
    "Data & Akurasi": ["data", "akurat", "salah", "keliru", "sinkron", "sesuai",
                       "tidak sesuai", "valid", "informasi", "sertifikat", "status"],
    "Tampilan & Navigasi": ["tampilan", "desain", "interface", "navigasi", "menu",
                            "ribet", "rumit", "simpel", "membingungkan", "mudah",
                            "susah", "user friendly", "ui", "ux"],
    "Fitur & Fungsi": ["fitur", "fungsi", "layanan"],
    "Layanan & Respon": ["respon", "admin", "customer", "cs", "bantuan", "tanggap",
                         "pelayanan", "service", "balas", "dibalas"],
}

_PROB_COL = {"negatif": "prob_negatif", "netral": "prob_netral", "positif": "prob_positif"}


def load_result(platform):
    """Muat CSV hasil klasifikasi satu platform; None bila tidak ada."""
    path = output_dir(platform) / "hasil_sentimen_final.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def _tokens(series):
    return " ".join(series.dropna().astype(str)).split()


def top_unigrams(df, label, n=12):
    sub = df[df["sentimen"] == label]
    return Counter(_tokens(sub["text_clean"])).most_common(n)


def top_bigrams(df, label, n=10):
    sub = df[df["sentimen"] == label]
    bigrams = Counter()
    for text in sub["text_clean"].dropna().astype(str):
        toks = text.split()
        bigrams.update(f"{a} {b}" for a, b in zip(toks, toks[1:]))
    return bigrams.most_common(n)


def aspect_breakdown(df):
    """Untuk tiap aspek: jumlah komentar yang menyebut + komposisi sentimennya.
    Mengembalikan list dict, terurut dari yang paling sering disebut."""
    comments = df["comment"].fillna("").astype(str).str.lower()
    rows = []
    for aspect, keywords in ASPECTS.items():
        mask = pd.Series(False, index=df.index)
        for kw in keywords:
            mask = mask | comments.str.contains(re.escape(kw), regex=True)
        sub = df[mask]
        if len(sub) == 0:
            continue
        dist = sub["sentimen"].value_counts()
        rows.append({
            "aspek": aspect,
            "total": int(len(sub)),
            "negatif": int(dist.get("negatif", 0)),
            "netral": int(dist.get("netral", 0)),
            "positif": int(dist.get("positif", 0)),
        })
    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows


def quotes(df, label, n=3, max_len=180):
    """Kutipan paling representatif: probabilitas tertinggi untuk label tsb."""
    sub = df[df["sentimen"] == label].sort_values(_PROB_COL[label], ascending=False)
    out = []
    for comment in sub["comment"].head(n):
        comment = re.sub(r"\s+", " ", str(comment)).strip()
        if len(comment) > max_len:
            comment = comment[:max_len].rstrip() + "…"
        out.append(comment)
    return out


def summarize(df):
    """Statistik ringkas: total, distribusi, persentase, rating rata-rata, dominan."""
    total = len(df)
    dist = df["sentimen"].value_counts().reindex(SENTIMENTS).fillna(0).astype(int)
    percent = (dist / max(total, 1) * 100).round(1)
    avg_rating = None
    if "rating" in df.columns and df["rating"].notna().any():
        avg_rating = round(float(df["rating"].dropna().mean()), 2)
    dominant = dist.idxmax() if total else "netral"
    return {
        "total": total,
        "dist": dist.to_dict(),
        "percent": percent.to_dict(),
        "avg_rating": avg_rating,
        "dominant": dominant,
    }


def build_insight(df):
    """Kumpulkan seluruh metrik analisis untuk satu DataFrame."""
    return {
        "summary": summarize(df),
        "aspects": aspect_breakdown(df),
        "top_neg_words": top_unigrams(df, "negatif"),
        "top_pos_words": top_unigrams(df, "positif"),
        "top_neg_bigrams": top_bigrams(df, "negatif"),
        "top_pos_bigrams": top_bigrams(df, "positif"),
        "quotes_neg": quotes(df, "negatif"),
        "quotes_pos": quotes(df, "positif"),
    }
