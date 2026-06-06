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
def build_classifier():
    from transformers import (pipeline, AutoTokenizer, AutoModelForSequenceClassification)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return pipeline("text-classification", model=model, tokenizer=tokenizer,
                    top_k=None, truncation=True, max_length=256)


def classify(text: str, classifier=None):
    """Kembalikan (label, dict probabilitas {negatif, netral, positif})."""
    classifier = classifier or build_classifier()
    output = classifier(text)[0]
    probs = {LABEL_MAP[o["label"]]: round(o["score"], 4) for o in output}
    label = max(probs, key=probs.get)
    return label, probs
