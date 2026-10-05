#!/usr/bin/env python3
"""Stage 1 — verify mapped places, quotes and link fragments against the text.

For every place/route in ../../data/spinnennetz-source.json this checks:
  * quote   — does the (normalised) quote occur in its own chapter?
  * srcText — does the verbatim fragment used for the Gutenberg deep link occur
              there exactly (whitespace-normalised)? If not, the "im Kontext"
              link would open the chapter without highlighting.
  * mention — do the distinctive tokens of the place name occur in the chapter?

A feature's chapter is its primary `group` (config key "Chapter n"); features
of thematic groups without a chapter are reported but not text-checked.
Adapted from Mapping Joyce's verify_places.py.

Output: ../annotations/verification.json (+ a human summary on stdout)
"""
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "data", "spinnennetz-source.json")
CHS = os.path.join(HERE, "..", "annotations", "chapters.json")
OUT = os.path.join(HERE, "..", "annotations", "verification.json")

STOP = {"der", "die", "das", "des", "dem", "den", "am", "an", "im", "in", "zum", "zur",
        "und", "von", "vor", "bei", "auf", "mit", "nach", "weg", "route", "wohnung",
        "haus", "büro", "villa", "bahnhof", "kaserne", "kasino", "lokal", "café", "hotel",
        "theodor", "theodors", "lohse", "lohses", "berlin", "alter", "standort", "kapitel"}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    for a, b in (("’", "'"), ("‘", "'"), ("»", '"'), ("«", '"'), ("“", '"'),
                 ("”", '"'), ("„", '"'), ("—", " "), ("–", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).lower().strip()


def chapter_of(group):
    g = group[0] if isinstance(group, list) else group
    m = re.match(r"Chapter (\d+)$", str(g))
    return int(m.group(1)) if m else None


def probes(name):
    return [t for t in re.findall(r"[A-Za-zÄÖÜäöüß\-]+", name)
            if t.lower() not in STOP and len(t) > 3 and t[0].isupper()]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    chs = {c["chapter"]: norm(c["text"]) for c in json.load(open(CHS, encoding="utf-8"))}
    items = [("place", p) for p in src.get("places", [])] + \
            [("route", r) for r in src.get("routes", [])]
    res, bad = [], {"quote": [], "srcText": [], "name": []}
    for kind, it in items:
        ch = chapter_of(it.get("group"))
        rec = {"kind": kind, "id": it.get("id"), "name": it["name"], "chapter": ch}
        text = chs.get(ch, "")
        if ch is None:
            rec["note"] = "no chapter group — not text-checked"
            res.append(rec)
            continue
        for field in ("quote", "srcText"):
            if it.get(field):
                ok = norm(it[field]) in text
                rec[field + "_ok"] = ok
                if not ok:
                    found = [k for k in sorted(chs) if norm(it[field]) in chs[k]]
                    rec[field + "_found_in"] = found
                    bad[field].append(rec)
        pr = probes(it["name"])
        if pr:
            hits = {p: text.count(p.lower()) for p in pr}
            rec["name_hits"] = hits
            if not any(hits.values()):
                bad["name"].append(rec)
        res.append(rec)
    summary = {
        "items": len(res),
        "quotes_bad": len(bad["quote"]), "srcText_bad": len(bad["srcText"]),
        "names_not_in_chapter": len(bad["name"]),
    }
    json.dump({"summary": summary, "items": res}, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("Summary:", summary)
    for field in ("quote", "srcText"):
        for r in bad[field]:
            print(f"  ✗ {field:<7} ch{r['chapter']:>2} {r['name'][:40]:<40} "
                  f"found in {r.get(field + '_found_in') or 'NOT FOUND'}")
    for r in bad["name"]:
        print(f"  ? name    ch{r['chapter']:>2} {r['name'][:40]:<40} probes={list(r['name_hits'])}")
    print("Full report ->", OUT)


if __name__ == "__main__":
    main()
