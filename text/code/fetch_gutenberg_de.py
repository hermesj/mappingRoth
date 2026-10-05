#!/usr/bin/env python3
"""Fetch a work from Projekt Gutenberg-DE into one plain-text file.

One-off, polite (one request every few seconds), standard library only.
Gutenberg-DE serves one page per chapter (…/chapter/1 = title page,
…/chapter/2 = chapter I, …). The script keeps only the work text — headings
and paragraphs of the page's <main> — and writes each chapter as

    ## <heading>
    <paragraph>
    …

Pages that come back as the site's "Einen Moment bitte" check are reported and
skipped (re-run later with --only N to fill the gap; the bot check is never
circumvented).

Usage:
    python3 fetch_gutenberg_de.py <book-url> <pages> <out.txt> [--only N,M]
    python3 fetch_gutenberg_de.py \\
        https://projekt-gutenberg.org/authors/joseph-roth/books/das-spinnennetz 31 \\
        ../raw/das-spinnennetz.txt
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

UA = "litmap/1.0 (literary-geography research; one-off text fetch)"
DELAY = 3.0


def page_paras(raw):
    m = raw[raw.find("<main"):]
    m = m[:m.find("</main>")]
    m = re.sub(r"(?s)<(script|style|nav|header|footer)[^>]*>.*?</\1>", "", m)
    out = []
    for tag, p in re.findall(r"(?s)<(p|h1|h2|h3|h4)[^>]*>(.*?)</\1>", m):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", p))).strip()
        if t:
            out.append(("## " if tag.startswith("h") else "") + t)
    # the page repeats its text block (reading mode) — keep each paragraph once
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def main(base, pages, out, only=None):
    cache = out + ".pages.json"            # resumable: chapters fetched so far
    got = json.load(open(cache, encoding="utf-8")) if os.path.exists(cache) else {}
    for n in range(1, pages + 1):
        if (only and n not in only) or (not only and str(n) in got):
            continue
        url = "%s/chapter/%d/" % (base.rstrip("/"), n)
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}),
                                     timeout=30).read().decode("utf-8", "replace")
        if "<main" not in raw:
            print("  page %2d: blocked by the site's check — skipped" % n)
        else:
            got[str(n)] = page_paras(raw)
            print("  page %2d: %d paragraphs" % (n, len(got[str(n)])))
        json.dump(got, open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(DELAY)
    missing = [n for n in range(1, pages + 1) if str(n) not in got]
    with open(out, "w", encoding="utf-8") as f:
        for n in range(1, pages + 1):
            for p in got.get(str(n), ["## [Seite %d fehlt]" % n]):
                f.write(p + "\n")
            f.write("\n")
    print("wrote %s%s" % (out, ("  — MISSING pages: %s" % missing) if missing else ""))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only="):
            only = {int(x) for x in a.split("=", 1)[1].split(",")}
    if len(args) != 3:
        sys.exit(__doc__)
    main(args[0], int(args[1]), args[2], only)
