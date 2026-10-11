# Jargon Buster

Turns IT jargon into plain language. Streamlit front end, Groq `openai/gpt-oss-120b` for the LLM. Free tools only.

## Run locally
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # add your Groq key
streamlit run app.py
```
Get a free key at https://console.groq.com/keys

## Deploy (Streamlit Community Cloud, from GitHub)
1. Push this folder to a GitHub repo (do not commit `secrets.toml`).
2. Go to https://share.streamlit.io, click **Create app**, pick the repo, branch and `app.py`.
3. Open **Advanced settings > Secrets** and add: `GROQ_API_KEY = "your-key"`.
4. Deploy. Every push to the branch redeploys the app.

## How the simplified text works
Every jargon term or acronym is replaced by its simplest plain meaning, in place. A second check re-runs the text if any glossary term is still left in the result.

## Interface
Custom CSS plus small HTML/JS widgets (`streamlit.components.v1.html`), all supported on Streamlit Community Cloud: live word counter, clickable highlighted terms with instant definitions, clickable green swaps, filter chips, synced scrolling, copy buttons.

## Files
- `app.py` - the app (input, categories, simplify, side-by-side, highlighting, definitions, saved, glossary)
- `glossary.json` - local IT glossary used for highlighting and definitions
- `seed_terms.txt` - ~2,000 more IT terms (definitions are generated on demand)
- `requirements.txt`

## Glossary
`glossary.json` has hand-written definitions. `seed_terms.txt` lists about 2,000 more IT terms that are highlighted
in your text. Their definitions are written by Groq the first time someone opens a term, then cached by the app.
To add terms, add lines to `seed_terms.txt` (`category | type | term, term, ...`) and push to GitHub.
