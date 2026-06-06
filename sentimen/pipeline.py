# -*- coding: utf-8 -*-
"""
Pipeline analisis sentimen yang dipakai bersama semua platform.

Fungsi `analisis(df, platform)` bersifat MANDIRI: ia hanya membaca DataFrame
yang diberikan dan menulis ke folder output_<platform>/ sehingga menjalankan
satu platform tidak memengaruhi platform lain.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

import pandas as pd

from config import output_dir, APP_NAME
from sentimen.preprocessing import proses
from sentimen.model import buat_classifier, klasifikasi

WARNA = {"positif": "#2e9e5b", "netral": "#9e9e9e", "negatif": "#d64545"}


def _siapkan_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "comment" not in df.columns:
        raise ValueError("DataFrame harus punya kolom 'comment'.")
    df["comment"] = df["comment"].astype(str).str.strip()
    df = df[(df["comment"].str.len() > 0) & (df["comment"].str.lower() != "nan")]
    df = df.reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    return df


def _plot(df, dist, persen, outdir, platform):
    # (a) bar chart distribusi
    plt.figure(figsize=(7, 5))
    bars = plt.bar(dist.index, dist.values, color=[WARNA[k] for k in dist.index])
    for b, v, p in zip(bars, dist.values, persen.values):
        plt.text(b.get_x() + b.get_width()/2, v + 0.3, f"{v}\n({p}%)",
                 ha="center", va="bottom", fontsize=10)
    plt.title(f"Distribusi Sentimen - {platform.capitalize()}\n{APP_NAME}",
              fontsize=12, fontweight="bold")
    plt.ylabel("Jumlah Komentar")
    plt.ylim(0, max(dist.max() * 1.25, 1))
    plt.tight_layout()
    plt.savefig(outdir / "01_distribusi_sentimen.png", dpi=150)
    plt.close()

    # (b) pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(dist.values, labels=[k.capitalize() for k in dist.index],
            autopct="%1.1f%%", colors=[WARNA[k] for k in dist.index],
            startangle=90, wedgeprops={"edgecolor": "white"})
    plt.title(f"Persentase Sentimen - {platform.capitalize()}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(outdir / "02_persentase_pie.png", dpi=150)
    plt.close()

    # (c) wordcloud keseluruhan + per sentimen
    from wordcloud import WordCloud
    semua = " ".join(df["text_clean"])
    if semua.strip():
        WordCloud(width=900, height=450, background_color="white",
                  colormap="viridis").generate(semua).to_file(
                      str(outdir / "03_wordcloud_keseluruhan.png"))
    for label, cmap in [("negatif", "Reds"), ("positif", "Greens")]:
        teks = " ".join(df[df["sentimen"] == label]["text_clean"])
        if teks.strip():
            WordCloud(width=900, height=450, background_color="white",
                      colormap=cmap).generate(teks).to_file(
                          str(outdir / f"04_wordcloud_{label}.png"))

    # (d) top-15 kata negatif & positif
    def top_words(label, n=15):
        teks = " ".join(df[df["sentimen"] == label]["text_clean"]).split()
        return Counter(teks).most_common(n)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, label, c in zip(axes, ["negatif", "positif"], ["#d64545", "#2e9e5b"]):
        data = top_words(label)
        if data:
            kata, jml = zip(*data)
            ax.barh(range(len(kata)), jml, color=c)
            ax.set_yticks(range(len(kata)))
            ax.set_yticklabels(kata)
            ax.invert_yaxis()
        ax.set_title(f"15 Kata Terbanyak - {label.capitalize()}", fontweight="bold")
        ax.set_xlabel("Frekuensi")
    plt.tight_layout()
    plt.savefig(outdir / "05_top_kata.png", dpi=150)
    plt.close()
    return top_words


def analisis(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    outdir = output_dir(platform)
    print(f"[1/4] Menyiapkan data ({platform})...")
    df = _siapkan_df(df)
    print(f"      Total komentar: {len(df)}")

    print("[2/4] Preprocessing (case folding -> cleansing -> tokenizing -> "
          "normalisasi -> filtering -> stemming)...")
    df["text_clean"] = [proses(t)[1] for t in df["comment"]]

    print("[3/4] Klasifikasi (model transformer)...")
    clf = buat_classifier()
    labels, pneg, pnet, ppos = [], [], [], []
    for i, teks in enumerate(df["comment"], 1):
        lab, pr = klasifikasi(teks, clf)
        labels.append(lab)
        pneg.append(pr["negatif"]); pnet.append(pr["netral"]); ppos.append(pr["positif"])
        if i % 50 == 0:
            print(f"      {i}/{len(df)} selesai")
    df["sentimen"] = labels
    df["prob_negatif"], df["prob_netral"], df["prob_positif"] = pneg, pnet, ppos

    kol = ["id"] + [c for c in ("sumber", "rating") if c in df.columns] + \
          ["comment", "text_clean", "prob_negatif", "prob_netral", "prob_positif", "sentimen"]
    hasil = df[kol]
    out_csv = outdir / "hasil_sentimen_final.csv"
    hasil.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("[4/4] Membuat visualisasi...")
    dist = df["sentimen"].value_counts().reindex(["positif", "netral", "negatif"]).fillna(0).astype(int)
    persen = (dist / max(dist.sum(), 1) * 100).round(1)
    top_words = _plot(df, dist, persen, outdir, platform)

    print(f"\n=== DISTRIBUSI SENTIMEN ({platform.upper()}) ===")
    for k in ["positif", "netral", "negatif"]:
        print(f"  {k.capitalize():8s}: {dist[k]:4d} ({persen[k]}%)")
    print("  Kata dominan NEGATIF:", ", ".join(w for w, _ in top_words("negatif", 10)))
    print("  Kata dominan POSITIF:", ", ".join(w for w, _ in top_words("positif", 10)))
    print(f"\nHasil & 5 grafik tersimpan di: {outdir}")
    return hasil
