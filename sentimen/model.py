# -*- coding: utf-8 -*-
"""
Model klasifikasi sentimen berbasis transformer (IndoBERT/XLM-R).
Model melakukan transformasi teks -> vektor secara internal lalu
mengklasifikasikan ke 3 kelas: positif / netral / negatif.
"""
from functools import lru_cache
from config import MODEL_NAME

LABEL_MAP = {"negative": "negatif", "neutral": "netral", "positive": "positif"}


@lru_cache(maxsize=1)
def buat_classifier():
    from transformers import (pipeline, AutoTokenizer, AutoModelForSequenceClassification)
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return pipeline("text-classification", model=mdl, tokenizer=tok,
                    top_k=None, truncation=True, max_length=256)


def klasifikasi(teks: str, classifier=None):
    """Kembalikan (label, dict probabilitas {negatif, netral, positif})."""
    classifier = classifier or buat_classifier()
    out = classifier(teks)[0]
    prob = {LABEL_MAP[o["label"]]: round(o["score"], 4) for o in out}
    label = max(prob, key=prob.get)
    return label, prob
