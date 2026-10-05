# text

Text-driven pipelines to **verify and enrich** the Spinnennetz dataset against
Roth's own words — the same layout as in Mapping Joyce.

```
text/
├── raw/            public-domain source text (+ provenance NOTICE)
├── code/           pipeline scripts (one step each, composable)
├── split-config.json
└── annotations/    generated JSON (chapters, verification, NER)
```

The text is **public domain** (Roth † 1939; published 1923) — see
[`raw/NOTICE.md`](raw/NOTICE.md). This folder is safe to publish.

## Pipelines

| Step | Script | Output |
|------|--------|--------|
| Fetch the text (one-off) | `code/fetch_gutenberg_de.py` | `raw/das-spinnennetz.txt` |
| Split into 30 chapters | `code/split_episodes.py` (generic, shared with Joyce) | `annotations/chapters.json` |
| Stage 1 — verify places, quotes, link fragments | `code/verify_places.py` | `annotations/verification.json` |
| Stage 2a — full NER annotation | `code/annotate.py` | `annotations/entities.json` |
| Stage 2b — derive place candidates | `code/candidates.py` | `annotations/ner_candidates.json` |

```bash
cd text/code
python3 split_episodes.py
python3 verify_places.py
pip install -r requirements.txt && python -m spacy download de_core_news_lg   # once
python3 annotate.py          # text -> entity annotation (PER, LOC, ORG, MISC)
python3 candidates.py        # annotation -> unmapped place candidates
```

`verify_places.py` checks, for every mapped place, that its **quote** and its
**`srcText`** (the fragment the Gutenberg deep link highlights) occur verbatim
in its own chapter, and that the place name is mentioned there. Re-run it
whenever `data/spinnennetz-source.json` changes.

> The checked-in annotations were generated with **spaCy 3.8 /
> `de_core_news_lg`**. German NER confuses capitalised nouns with names
> ("Beilpicke", "Rügen" in the sense of reprimands); the candidate list is a
> suggestion set, not ground truth.
