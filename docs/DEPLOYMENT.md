# Deployment Guide

## Netlify Website (30 seconds, no build)

The `website/` folder is pure static (HTML/CSS/JS). No npm build needed.

### Option A: Drag and Drop

1. Zip `website/` (provided as `KV-13-netlify-deploy.zip`)
2. Go to https://app.netlify.com/drop
3. Drag zip — live instantly at `https://<random>.netlify.app`
4. Rename to `kv-13` in Netlify site settings

### Option B: CLI

```bash
npm install -g netlify-cli
netlify login
cd website
netlify deploy --prod --dir .
```

### Option C: Git Continuous Deploy

1. Push repo to `kv-creates/KV-13`
2. Netlify: Add new site -> Import from Git -> GitHub -> select repo
3. Build settings:
   - Base directory: `website`
   - Build command: (empty)
   - Publish directory: `website`  or `.` if base is website
   - Or if base is repo root: Publish directory `website`
4. Deploy. `netlify.toml` handles headers and redirects.

## API Deployment

### Docker

```bash
docker compose up --build
# API at http://localhost:8000/docs
```

### HuggingFace Spaces

```bash
docker build -t kv13-api .
# Push to HF Spaces Docker template
```

### Fly.io / Render

Use `Dockerfile` as is. Set `PORT=8000`.

## Environment Variables

- `KV13_DEVICE` = `cuda` | `cpu` (default cuda if available)
- `KV13_QUANTIZE` = `4bit` | `fp16`
- `KV13_VARIANT` = `kv13-13b-instruct-q4`

## Custom Domain

Netlify Site settings -> Domain management -> Add custom domain -> update DNS.

## Verifying

- Website loads at `/` and `/playground`
- Playground Analyze button works offline
- API `/health` returns 200
- `curl -X POST /v1/analyze` returns risk_score
