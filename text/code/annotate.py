#!/usr/bin/env python3
"""Stage 2a — full NER annotation of Das Spinnennetz.

Runs spaCy over every chapter and records *all* named entities (every label:
PER, LOC, ORG, MISC for the German models) with their character offsets, as a
reusable annotation layer. Downstream steps (candidates.py) read this JSON
instead of re-running NER. Adapted from Mapping Joyce's annotate.py.

Requires:  pip install spacy && python -m spacy download de_core_news_lg
Input:     ../annotations/chapters.json
Output:    ../annotations/entities.json
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CHS = os.path.join(HERE, "..", "annotations", "chapters.json")
OUT = os.path.join(HERE, "..", "annotations", "entities.json")


def main(model="de_core_news_lg"):
    try:
        import spacy
    except ImportError:
        sys.exit("spaCy not installed. Run:\n"
                 "  pip install spacy && python -m spacy download " + model)
    try:
        nlp = spacy.load(model, disable=["lemmatizer"])
    except OSError:
        sys.exit(f"model {model!r} missing. Run: python -m spacy download {model}")

    chapters = json.load(open(CHS, encoding="utf-8"))
    nlp.max_length = max(len(c["text"]) for c in chapters) + 1000

    by_chapter, label_counts, total = {}, Counter(), 0
    for c in chapters:
        doc = nlp(c["text"])
        ents = [{"label": e.label_, "text": e.text, "start": e.start_char, "end": e.end_char}
                for e in doc.ents]
        label_counts.update(e["label"] for e in ents)
        by_chapter[str(c["chapter"])] = ents
        total += len(ents)
        print(f"  ch{c['chapter']:>2} {c['title']:<14} {len(ents):>4} entities")

    json.dump({
        "model": model,
        "entity_count": total,
        "label_counts": dict(label_counts.most_common()),
        "note": "Offsets are character positions into the matching chapter text in "
                "chapters.json. Auto-generated NER over the public-domain text "
                "(Projekt Gutenberg-DE); German models tag LOC/PER/ORG/MISC and "
                "confuse capitalised nouns with names — a suggestion layer, not ground truth.",
        "by_chapter": by_chapter,
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nWrote {total} entities -> {OUT}")
    print("Labels:", ", ".join(f"{k}={v}" for k, v in label_counts.most_common()))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "de_core_news_lg")
