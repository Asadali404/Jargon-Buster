# Jorgan Buster

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

## Files
- `app.py` - the app (input, categories, simplify, side-by-side, highlighting, definitions, saved, glossary)
- `glossary.json` - local IT glossary used for highlighting and definitions
- `seed_terms.txt` - ~2,200 IT terms to turn into glossary entries (add your own lines)
- `build_glossary.py` - one-time script: Groq writes the definitions and merges them into `glossary.json`
- `requirements.txt`

## Grow the glossary
```bash
export GROQ_API_KEY="your-key"
python build_glossary.py --limit 40   # quick test
python build_glossary.py              # full run; safe to stop and re-run
```
Commit the updated `glossary.json` and push; the deployed app picks it up. Skim the new definitions before publishing.

