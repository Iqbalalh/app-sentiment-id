# -*- coding: utf-8 -*-
"""Runner per platform. Tiap modul menyediakan fungsi `jalankan()` yang
dipakai bersama oleh entrypoint utama (main.py), sekaligus bisa dijalankan
sendiri lewat `python -m runners.<platform>`."""
import importlib

PLATFORMS = ("playstore", "appstore", "tiktok")


def get_runner(nama):
    """Muat modul runner untuk satu platform secara lazy."""
    return importlib.import_module(f"{__name__}.{nama}")
