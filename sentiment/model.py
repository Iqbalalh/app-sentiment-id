# -*- coding: utf-8 -*-
"""
Model klasifikasi sentimen berbasis transformer (IndoBERT/XLM-R).
Model melakukan transformasi teks -> vektor secara internal lalu
mengklasifikasikan ke 3 kelas: positif / netral / negatif.
"""
from functools import lru_cache
from config import MODEL_NAME, MODEL_LABELS

# Default mendukung dua keluarga model sekaligus:
#  - berlabel teks (mis. cardiffnlp XLM-R): negative/neutral/positive
#  - IndoBERT sentimen (mdhugol): LABEL_0=positif, LABEL_1=netral, LABEL_2=negatif
_DEFAULT_LABEL_MAP = {
    "negative": "negatif", "neutral": "netral", "positive": "positif",
    "LABEL_0": "positif", "LABEL_1": "netral", "LABEL_2": "negatif",
}


def _build_label_map():
    if not MODEL_LABELS:
        return _DEFAULT_LABEL_MAP
    mapping = {}
    for pair in MODEL_LABELS.replace(";", ",").split(","):
        if "=" in pair:
            raw, mapped = pair.split("=", 1)
            mapping[raw.strip()] = mapped.strip()
    return mapping or _DEFAULT_LABEL_MAP


LABEL_MAP = _build_label_map()


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
    probs = {LABEL_MAP.get(o["label"], o["label"]): round(o["score"], 4) for o in output}
    label = max(probs, key=probs.get)
    return label, probs
