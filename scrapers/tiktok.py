# -*- coding: utf-8 -*-
"""
Scraper komentar TikTok (library tidak resmi TikTokApi + Playwright).

Prasyarat:
    pip install TikTokApi
    python -m playwright install chromium

ms_token diambil dari .env (TIKTOK_MS_TOKEN), daftar video dari config.TIKTOK_VIDEO_IDS.
Catatan: TikTok aktif memblokir scraping, jadi metode ini bisa sewaktu-waktu gagal.
"""
import asyncio
import pandas as pd

from config import TIKTOK_MS_TOKEN, TIKTOK_VIDEO_IDS


async def _komentar_video(video_id, jumlah=300):
    from TikTokApi import TikTokApi
    rows = []
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[TIKTOK_MS_TOKEN], num_sessions=1, sleep_after=3)
        video = api.video(id=video_id)
        async for c in video.comments(count=jumlah):
            d = c.as_dict
            rows.append({
                "video_id": video_id,
                "username": d.get("user", {}).get("unique_id", ""),
                "comment": d.get("text", ""),
                "likes": d.get("digg_count", 0),
                "sumber": "tiktok",
            })
    return rows


async def _scrape_async(video_ids, jumlah):
    semua = []
    for vid in video_ids:
        try:
            semua += await _komentar_video(vid, jumlah)
            print(f"  video {vid}: total terkumpul {len(semua)}")
        except Exception as e:
            print(f"  gagal video {vid}: {e}")
    return semua


def scrape(video_ids=None, jumlah: int = 300) -> pd.DataFrame:
    if not TIKTOK_MS_TOKEN:
        raise RuntimeError("TIKTOK_MS_TOKEN kosong. Isi di file .env terlebih dahulu.")
    video_ids = video_ids or TIKTOK_VIDEO_IDS
    rows = asyncio.run(_scrape_async(video_ids, jumlah))
    return pd.DataFrame(rows)
