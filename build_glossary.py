#!/usr/bin/env python3
"""Grow glossary.json from seed_terms.txt using Groq (openai/gpt-oss-120b).

Run once on your own machine (free Groq key), then commit the updated glossary.json:

    export GROQ_API_KEY="your-key"        # Windows PowerShell: $env:GROQ_API_KEY="your-key"
    python build_glossary.py

Safe to stop and re-run: progress is saved after every batch, existing entries are never
changed, and terms already in glossary.json are skipped.

Options:
    --batch 20     terms per request
    --pause 6      seconds to wait between requests (keeps you under free-tier limits)
    --limit 40     stop after adding this many new terms (handy for a first test)
    --category Databases    only build one category
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from groq import Groq

MODEL = "openai/gpt-oss-120b"
HERE = Path(__file__).parent
GLOSSARY = HERE / "glossary.json"
SEED = HERE / "seed_terms.txt"
TYPES = {"jargon", "acronym", "error_code"}

SYSTEM = """You write entries for a plain-language IT glossary aimed at non-experts.
You receive JSON: {"category": ..., "terms": [{"term": ..., "type": ...}, ...]}.

For each term write:
- "definition": at most 25 words, grade 6-8 reading level, no unexplained jargon, and
  without repeating the term itself where possible.
  * type "acronym": begin with the full expansion, then a period, then what it means.
    If the term is not truly an acronym (for example a product name), just define it.
  * type "error_code": say what the error means and its most common cause.
  * type "jargon": say what it is or does.
- "example": one short sentence (at most 20 words) that uses the term naturally.

Be accurate. If you do not recognise a term as a real IT term, leave it out.
Return ONLY JSON: {"entries": [{"term": "<copied exactly>", "definition": "...", "example": "..."}]}"""


def norm(t):
    return re.sub(r"\s+", " ", t).strip().lower()


def load_seed():
    items = []
    for line in SEED.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|", 2)]
        if len(parts) != 3 or parts[1] not in TYPES:
            print(f"Skipping malformed seed line: {line[:60]}...", file=sys.stderr)
            continue
        cat, typ, terms = parts
        for t in terms.split(","):
            t = t.strip()
            if t:
                items.append((cat, typ, t))
    return items


def ask(client, category, batch):
    payload = {"category": category, "terms": [{"term": t, "type": ty} for ty, t in batch]}
    for attempt in range(6):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                temperature=0.2,
                max_completion_tokens=6000,
                reasoning_effort="low",
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content).get("entries", [])
        except Exception as e:  # rate limit, bad JSON, network...
            wait = 15 * (attempt + 1)
            print(f"  retry in {wait}s ({type(e).__name__}: {str(e)[:100]})")
            time.sleep(wait)
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--pause", type=float, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--category", default="")
    args = ap.parse_args()

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("Set GROQ_API_KEY first (free key: https://console.groq.com/keys)")
    client = Groq(api_key=key)

    glossary = json.loads(GLOSSARY.read_text(encoding="utf-8")) if GLOSSARY.exists() else []
    have = {norm(e["term"]) for e in glossary}

    todo, seen = [], set()
    for cat, typ, term in load_seed():
        if args.category and cat.lower() != args.category.lower():
            continue
        k = norm(term)
        if k in have or k in seen:
            continue
        seen.add(k)
        todo.append((cat, typ, term))
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(glossary)} entries now, {len(todo)} new terms to write.")

    by_cat = {}
    for cat, typ, term in todo:
        by_cat.setdefault(cat, []).append((typ, term))

    added = 0
    for cat, items in by_cat.items():
        for i in range(0, len(items), args.batch):
            batch = items[i : i + args.batch]
            wanted = {norm(t): (ty, t) for ty, t in batch}
            for e in ask(client, cat, batch):
                k = norm(str(e.get("term", "")))
                d, ex = str(e.get("definition", "")).strip(), str(e.get("example", "")).strip()
                if k in wanted and d and ex and len(d) <= 400 and k not in have:
                    typ, term = wanted[k]
                    glossary.append({"term": term, "type": typ, "category": cat, "definition": d, "example": ex})
                    have.add(k)
                    added += 1
            GLOSSARY.write_text(json.dumps(glossary, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[{cat}] {min(i + args.batch, len(items))}/{len(items)}  (+{added} total, {len(glossary)} entries)")
            time.sleep(args.pause)

    print(f"Done. glossary.json now has {len(glossary)} entries.")


if __name__ == "__main__":
    main()
