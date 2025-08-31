# AI Influencer: Social Media Post Generator (LangChain + Gemini)

Generate platform-optimized social media posts end-to-end: topic, content, image prompt, hashtags — powered by Google Gemini via LangChain, with optional Google Imagen (Vertex AI) for image generation.

## Features
- Topic stub + Gemini content generation (Instagram, LinkedIn, Twitter, Facebook)
- Content-grounded image prompts (JSON analysis → compositional prompt)
- Optional Imagen backend for actual images; local placeholder fallback
- SEO hashtag generation + simple categorization
- Organized outputs under `posts/` with `posts/images/`
- Jupyter demo + quick helpers

## Quickstart
1) Clone and enter the project.
2) Create/activate a Python 3.10+ env.
3) Install deps.
4) Set env vars.
5) Run the notebook.

```bash
# 1) Clone
git clone https://github.com/hasnainkhan8532/Social-Media-AI-Influencer-using-Langchain.git
cd Social-Media-AI-Influencer-using-Langchain

# 2) Environment (example with venv)
python -m venv .venv
source .venv/bin/activate

# 3) Install deps
pip install -r requirements.txt

# 4) Env vars
export GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
# Optional: enable Vertex Imagen backend
# export GOOGLE_GENAI_USE_VERTEXAI=true
# export GOOGLE_CLOUD_PROJECT=your-gcp-project
# export GOOGLE_CLOUD_LOCATION=global
# export IMAGE_MODEL=imagen-4.0-generate-preview-06-06

# 5) Launch Jupyter and open social_media_ai_influencer.ipynb
python -m jupyter lab
```

## How it Works
- `ContentGenerator` uses `ChatGoogleGenerativeAI` (Gemini 1.5 Flash 8B) via LangChain.
- `ImageGenerator` builds image prompts from actual post content (LLM JSON analysis → prompt). If Vertex Imagen is enabled, images are generated via `google.genai`; otherwise we save a local placeholder PNG into `posts/images/`.
- `HashtagGenerator` produces SEO tags and categorizes them.
- `AIInfluencerPostGenerator` orchestrates the flow and saves JSON/TXT under `posts/`.

## Imagen (Vertex) Backend
To generate real images with Google Imagen instead of placeholders:
- Ensure you have `google-genai` installed (already in `requirements.txt`).
- Enable Vertex integration via env:
```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-gcp-project
export GOOGLE_CLOUD_LOCATION=global
# Optional override (default shown)
export IMAGE_MODEL=imagen-4.0-generate-preview-06-06
```
- Authenticate gcloud (one-time):
```bash
gcloud auth application-default login
```
The code will attempt Imagen first and fall back to local placeholder if it fails.

## Output Structure
```
posts/
  images/
    instagram_YYMMDD_HHMM.png
    linkedin_YYMMDD_HHMM.png
  instagram_<niche>_YYMMDD_HHMM.json
  instagram_<niche>_YYMMDD_HHMM.txt
  linkedin_<niche>_YYMMDD_HHMM.json
  linkedin_<niche>_YYMMDD_HHMM.txt
```

## Notebook Tips
- Run cells top-to-bottom after setting env.
- Use `demo_post_generation()` to generate multiple scenarios.
- Use `quick_generate(niche, platform, audience)` for fast runs.

## Troubleshooting
- NameError: `sample_topic` → Re-run the cell that defines it (included above content test).
- 500 Internal from Gemini (rate/infra): re-run or lower frequency.
- Imagen errors: verify `GOOGLE_GENAI_USE_VERTEXAI`, project/location, and ADC auth.
- Missing deps: `pip install -r requirements.txt` in the same venv Jupyter uses.

## License
MIT
