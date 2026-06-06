# -*- coding: utf-8 -*-
"""
Pipeline analisis sentimen yang dipakai bersama semua platform.

Fungsi `analyze(df, platform)` bersifat MANDIRI: ia hanya membaca DataFrame
yang diberikan dan menulis ke folder output/<platform>/ sehingga menjalankan
satu platform tidak memengaruhi platform lain.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

import pandas as pd
from tqdm import tqdm

from config import output_dir, APP_NAME
from sentiment.preprocessing import process
from sentiment.model import build_classifier, classify

# Pemetaan label sentimen (nilai data) ke warna grafik.
COLORS = {"positif": "#2e9e5b", "netral": "#9e9e9e", "negatif": "#d64545"}


def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "comment" not in df.columns:
        raise ValueError("DataFrame harus punya kolom 'comment'.")
    df["comment"] = df["comment"].astype(str).str.strip()
    df = df[(df["comment"].str.len() > 0) & (df["comment"].str.lower() != "nan")]
    df = df.reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    return df


def _plot(df, dist, percent, out_dir, platform):
    # (a) bar chart distribusi
    plt.figure(figsize=(7, 5))
    bars = plt.bar(dist.index, dist.values, color=[COLORS[lbl] for lbl in dist.index])
    for bar, value, pct in zip(bars, dist.values, percent.values):
        plt.text(bar.get_x() + bar.get_width()/2, value + 0.3, f"{value}\n({pct}%)",
                 ha="center", va="bottom", fontsize=10)
    plt.title(f"Distribusi Sentimen - {platform.capitalize()}\n{APP_NAME}",
              fontsize=12, fontweight="bold")
    plt.ylabel("Jumlah Komentar")
    plt.ylim(0, max(dist.max() * 1.25, 1))
    plt.tight_layout()
    plt.savefig(out_dir / "01_distribusi_sentimen.png", dpi=150)
    plt.close()

    # (b) pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(dist.values, labels=[lbl.capitalize() for lbl in dist.index],
            autopct="%1.1f%%", colors=[COLORS[lbl] for lbl in dist.index],
            startangle=90, wedgeprops={"edgecolor": "white"})
    plt.title(f"Persentase Sentimen - {platform.capitalize()}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_dir / "02_persentase_pie.png", dpi=150)
    plt.close()

    # (c) wordcloud keseluruhan + per sentimen
    from wordcloud import WordCloud
    all_text = " ".join(df["text_clean"])
    if all_text.strip():
        WordCloud(width=900, height=450, background_color="white",
                  colormap="viridis").generate(all_text).to_file(
                      str(out_dir / "03_wordcloud_keseluruhan.png"))
    for label, cmap in [("negatif", "Reds"), ("positif", "Greens")]:
        text = " ".join(df[df["sentimen"] == label]["text_clean"])
        if text.strip():
            WordCloud(width=900, height=450, background_color="white",
                      colormap=cmap).generate(text).to_file(
                          str(out_dir / f"04_wordcloud_{label}.png"))

    # (d) top-15 kata negatif & positif
    def top_words(label, n=15):
        text = " ".join(df[df["sentimen"] == label]["text_clean"]).split()
        return Counter(text).most_common(n)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, label, color in zip(axes, ["negatif", "positif"], ["#d64545", "#2e9e5b"]):
        pairs = top_words(label)
        if pairs:
            words, counts = zip(*pairs)
            ax.barh(range(len(words)), counts, color=color)
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words)
            ax.invert_yaxis()
        ax.set_title(f"15 Kata Terbanyak - {label.capitalize()}", fontweight="bold")
        ax.set_xlabel("Frekuensi")
    plt.tight_layout()
    plt.savefig(out_dir / "05_top_kata.png", dpi=150)
    plt.close()
    return top_words


def analyze(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    out_dir = output_dir(platform)
    print(f"[1/4] Menyiapkan data ({platform})...")
    df = _prepare_df(df)
    print(f"      Total komentar: {len(df)}")

    print("[2/4] Preprocessing (case folding -> cleansing -> tokenizing -> "
          "normalisasi -> filtering -> stemming)...")
    df["text_clean"] = [process(t)[1]
                        for t in tqdm(df["comment"], desc="      preprocessing",
                                      unit="komentar")]

    print("[3/4] Klasifikasi (model transformer)...")
    classifier = build_classifier()
    labels, p_neg, p_neu, p_pos = [], [], [], []
    for text in tqdm(df["comment"], desc="      klasifikasi", unit="komentar"):
        label, probs = classify(text, classifier)
        labels.append(label)
        p_neg.append(probs["negatif"]); p_neu.append(probs["netral"]); p_pos.append(probs["positif"])
    df["sentimen"] = labels
    df["prob_negatif"], df["prob_netral"], df["prob_positif"] = p_neg, p_neu, p_pos

    cols = ["id"] + [c for c in ("sumber", "rating") if c in df.columns] + \
           ["comment", "text_clean", "prob_negatif", "prob_netral", "prob_positif", "sentimen"]
    result = df[cols]
    out_csv = out_dir / "hasil_sentimen_final.csv"
    result.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("[4/4] Membuat visualisasi...")
    dist = df["sentimen"].value_counts().reindex(["positif", "netral", "negatif"]).fillna(0).astype(int)
    percent = (dist / max(dist.sum(), 1) * 100).round(1)
    top_words = _plot(df, dist, percent, out_dir, platform)

    print(f"\n=== DISTRIBUSI SENTIMEN ({platform.upper()}) ===")
    for key in ["positif", "netral", "negatif"]:
        print(f"  {key.capitalize():8s}: {dist[key]:4d} ({percent[key]}%)")
    print("  Kata dominan NEGATIF:", ", ".join(w for w, _ in top_words("negatif", 10)))
    print("  Kata dominan POSITIF:", ", ".join(w for w, _ in top_words("positif", 10)))
    print(f"\nHasil & 5 grafik tersimpan di: {out_dir}")
    return result
