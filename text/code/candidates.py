#!/usr/bin/env python3
"""Stage 2b — derive place candidates from the NER annotation.

Reads entities.json, keeps the location label (LOC in the German models),
aggregates by surface form, and flags which are NOT yet mapped in
data/spinnennetz-source.json — a review list for deciding what to add.
Adapted from Mapping Joyce's candidates.py.

Input:  ../annotations/entities.json, ../../data/spinnennetz-source.json
Output: ../annotations/ner_candidates.json
"""
import json
import os
import re
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(HERE, "..", "annotations", "entities.json")
SRC = os.path.join(HERE, "..", "..", "data", "spinnennetz-source.json")
OUT = os.path.join(HERE, "..", "annotations", "ner_candidates.json")

PLACE_LABELS = {"LOC"}
MIN_COUNT = 1  # short novel: keep one-off mentions too


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    data = json.load(open(ENT, encoding="utf-8"))
    src = json.load(open(SRC, encoding="utf-8"))
    mapped = set()
    for p in src.get("places", []) + src.get("mentions", []):
        for k in ("name", "geocode"):
            mapped.add(norm(p.get(k, "")))
        for a in p.get("aliases", []):
            mapped.add(norm(a))
    mapped.discard("")

    def is_mapped(cand):
        nc = norm(cand)
        return any(nc and (nc in m or m in nc) for m in mapped)

    agg = defaultdict(lambda: {"count": 0, "chapters": set(), "display": None})
    for ch, ents in data["by_chapter"].items():
        for e in ents:
            if e["label"] in PLACE_LABELS:
                key = norm(e["text"])
                if len(key) < 3:
                    continue
                a = agg[key]
                a["count"] += 1
                a["chapters"].add(int(ch))
                a["display"] = a["display"] or re.sub(r"\s+", " ", e["text"].strip())

    cands = sorted(({"text": a["display"], "count": a["count"], "chapters": sorted(a["chapters"]),
                     "already_mapped": is_mapped(a["display"])}
                    for a in agg.values() if a["count"] >= MIN_COUNT),
                   key=lambda c: (-c["count"], c["text"]))
    unmapped = [c for c in cands if not c["already_mapped"]]
    json.dump({"model": data.get("model"), "place_labels": sorted(PLACE_LABELS),
               "min_count": MIN_COUNT, "candidates": cands, "unmapped_count": len(unmapped)},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(cands)} place candidates; {len(unmapped)} not yet mapped -> {OUT}\n")
    for c in unmapped[:40]:
        print(f"  {c['count']:>3}  {c['text']:<30} ch {c['chapters']}")


if __name__ == "__main__":
    main()
