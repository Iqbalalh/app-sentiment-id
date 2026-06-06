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


async def _video_comments(video_id, count=300):
    from TikTokApi import TikTokApi
    rows = []
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[TIKTOK_MS_TOKEN], num_sessions=1, sleep_after=3)
        video = api.video(id=video_id)
        async for comment in video.comments(count=count):
            data = comment.as_dict
            rows.append({
                "video_id": video_id,
                "username": data.get("user", {}).get("unique_id", ""),
                "comment": data.get("text", ""),
                "likes": data.get("digg_count", 0),
                "sumber": "tiktok",
            })
    return rows


async def _scrape_async(video_ids, count):
    all_rows = []
    for video_id in video_ids:
        try:
            all_rows += await _video_comments(video_id, count)
            print(f"  video {video_id}: total terkumpul {len(all_rows)}")
        except Exception as err:
            print(f"  gagal video {video_id}: {err}")
    return all_rows


def scrape(video_ids=None, count: int = 300) -> pd.DataFrame:
    if not TIKTOK_MS_TOKEN:
        raise RuntimeError("TIKTOK_MS_TOKEN kosong. Isi di file .env terlebih dahulu.")
    video_ids = video_ids or TIKTOK_VIDEO_IDS
    rows = asyncio.run(_scrape_async(video_ids, count))
    return pd.DataFrame(rows)
