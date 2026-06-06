# -*- coding: utf-8 -*-
"""
Membangun laporan analisis sentimen (Markdown, Bahasa Indonesia) dari output
klasifikasi: satu laporan per platform dan satu laporan gabungan ketiga platform
yang diakhiri kesimpulan menyeluruh.
"""
import pandas as pd

from config import OUTPUT_DIR, APP_NAME, output_dir
from sentiment.insight import build_insight, load_result, summarize, SENTIMENTS

PLATFORM_LABEL = {
    "playstore": "Google Play Store",
    "appstore": "Apple App Store",
    "tiktok": "TikTok",
}


# ---------------- helper penyaji ----------------
def _fmt_words(pairs, n=8):
    return ", ".join(w for w, _ in pairs[:n]) or "-"


def _dist_table(summary):
    d, p = summary["dist"], summary["percent"]
    lines = ["| Sentimen | Jumlah | Persentase |", "| --- | ---: | ---: |"]
    for s in SENTIMENTS:
        lines.append(f"| {s.capitalize()} | {d.get(s, 0)} | {p.get(s, 0)}% |")
    return "\n".join(lines)


def _aspect_table(aspects, key, n=5):
    """Tabel aspek terurut berdasarkan jumlah komentar pada sentimen `key`."""
    rows = sorted([a for a in aspects if a[key] > 0],
                  key=lambda a: a[key], reverse=True)[:n]
    if not rows:
        return "_Tidak ada aspek yang menonjol._"
    lines = [f"| Aspek | Komentar {key} | Total menyebut |", "| --- | ---: | ---: |"]
    for a in rows:
        lines.append(f"| {a['aspek']} | {a[key]} | {a['total']} |")
    return "\n".join(lines)


def _quotes_block(quote_list):
    if not quote_list:
        return "_Tidak ada contoh._"
    return "\n".join(f"> {q}" for q in quote_list)


def _conclusion(label, insight):
    """Paragraf kesimpulan naratif (template) dari metrik yang dihitung."""
    s = insight["summary"]
    dom = s["dominant"]
    pct = s["percent"].get(dom, 0)
    neg = sorted([a for a in insight["aspects"] if a["negatif"] > 0],
                 key=lambda a: a["negatif"], reverse=True)[:3]
    pos = sorted([a for a in insight["aspects"] if a["positif"] > 0],
                 key=lambda a: a["positif"], reverse=True)[:3]
    rating_txt = (f", dengan rata-rata rating {s['avg_rating']}/5"
                  if s["avg_rating"] is not None else "")
    parts = [f"Dari **{s['total']}** komentar di {label}, opini publik cenderung "
             f"**{dom}** ({pct}%){rating_txt}."]
    if neg:
        parts.append(
            "Keluhan terbanyak berkaitan dengan "
            + ", ".join(f"**{a['aspek'].lower()}** ({a['negatif']} komentar)" for a in neg)
            + f". Kata yang sering muncul: _{_fmt_words(insight['top_neg_words'], 6)}_.")
    if pos:
        parts.append(
            "Hal yang paling diapresiasi berkaitan dengan "
            + ", ".join(f"**{a['aspek'].lower()}** ({a['positif']} komentar)" for a in pos)
            + f". Kata yang sering muncul: _{_fmt_words(insight['top_pos_words'], 6)}_.")
    return " ".join(parts)


def _insight_body(insight, h):
    """Badan laporan (ringkasan + pemicu negatif + pemicu positif).
    `h` adalah prefiks heading (mis. '##' atau '###')."""
    s = insight["summary"]
    md = [f"{h} Ringkasan", "",
          f"- Total komentar: **{s['total']}**"]
    if s["avg_rating"] is not None:
        md.append(f"- Rata-rata rating: **{s['avg_rating']}/5**")
    md += [f"- Sentimen dominan: **{s['dominant'].capitalize()}** "
           f"({s['percent'].get(s['dominant'], 0)}%)", "",
           _dist_table(s), ""]

    md += [f"{h} Apa yang membuat opini negatif", "",
           _aspect_table(insight["aspects"], "negatif"), "",
           f"- Kata dominan: _{_fmt_words(insight['top_neg_words'])}_",
           f"- Frasa dominan: _{_fmt_words(insight['top_neg_bigrams'])}_", "",
           "Contoh komentar negatif paling kuat:",
           _quotes_block(insight["quotes_neg"]), ""]

    md += [f"{h} Apa yang membuat opini positif", "",
           _aspect_table(insight["aspects"], "positif"), "",
           f"- Kata dominan: _{_fmt_words(insight['top_pos_words'])}_",
           f"- Frasa dominan: _{_fmt_words(insight['top_pos_bigrams'])}_", "",
           "Contoh komentar positif paling kuat:",
           _quotes_block(insight["quotes_pos"]), ""]
    return "\n".join(md)


# ---------------- laporan per platform ----------------
def platform_report_md(platform, df):
    label = PLATFORM_LABEL.get(platform, platform.capitalize())
    insight = build_insight(df)
    md = [f"# Analisis Sentimen — {APP_NAME} ({label})", "",
          _insight_body(insight, "##"),
          "## Kesimpulan", "",
          _conclusion(label, insight), ""]
    return "\n".join(md)


def write_platform_report(platform):
    df = load_result(platform)
    if df is None or len(df) == 0:
        return None
    path = output_dir(platform) / f"analisis_{platform}.md"
    path.write_text(platform_report_md(platform, df), encoding="utf-8")
    return path


# ---------------- laporan gabungan ----------------
def combined_report_md(dfs):
    names = ", ".join(PLATFORM_LABEL.get(p, p) for p in dfs)
    md = [f"# Analisis Sentimen Gabungan — {APP_NAME}", "",
          f"Laporan ini menggabungkan {len(dfs)} sumber data: {names}.", ""]

    # Tabel perbandingan antar platform
    md += ["## Perbandingan Antar Platform", "",
           "| Platform | Total | Positif | Netral | Negatif | Dominan | Rating |",
           "| --- | ---: | ---: | ---: | ---: | --- | ---: |"]
    for p, df in dfs.items():
        s = summarize(df)
        pr = s["percent"]
        rating = s["avg_rating"] if s["avg_rating"] is not None else "-"
        md.append(f"| {PLATFORM_LABEL.get(p, p)} | {s['total']} | "
                  f"{pr.get('positif', 0)}% | {pr.get('netral', 0)}% | "
                  f"{pr.get('negatif', 0)}% | {s['dominant'].capitalize()} | {rating} |")
    md.append("")

    # Kesimpulan ringkas tiap platform
    md += ["## Kesimpulan per Platform", ""]
    for p, df in dfs.items():
        label = PLATFORM_LABEL.get(p, p)
        md += [f"### {label}", "", _conclusion(label, build_insight(df)), ""]

    # Analisis keseluruhan (data digabung)
    union = pd.concat(list(dfs.values()), ignore_index=True)
    insight_all = build_insight(union)
    md += ["## Analisis Keseluruhan (Gabungan)", "",
           _insight_body(insight_all, "###")]

    # Kesimpulan akhir
    md += ["## Kesimpulan Akhir", "", _conclusion("ketiga platform", insight_all), ""]
    return "\n".join(md)


def write_combined_report(platforms):
    dfs = {}
    for p in platforms:
        df = load_result(p)
        if df is not None and len(df):
            dfs[p] = df
    if not dfs:
        return None
    path = OUTPUT_DIR / "analisis_gabungan.md"
    path.write_text(combined_report_md(dfs), encoding="utf-8")
    return path


def generate_all(platforms):
    """Tulis laporan per platform + laporan gabungan. Mengembalikan list path."""
    paths = [p for p in (write_platform_report(x) for x in platforms) if p]
    combined = write_combined_report(platforms)
    if combined:
        paths.append(combined)
    return paths
