# VoiceForge

Consent-first, self-hosted voice cloning and expressive text-to-speech portal.

## Included
- Voice sample upload and local profiles
- Mandatory consent declaration
- Hindi, Marathi, English and mixed-language scripts
- Emotion presets and modulation controls
- WAV preview/download and generation history
- Mock engine for testing without a GPU
- Pluggable OpenVoice V2 GPU adapter
- FastAPI, SQLite and Docker Compose

Only clone your own voice or one you have explicit permission to use. Never use generated speech to deceive, impersonate, defraud or bypass identity verification.

## Quick start without GPU

1. Copy .env.example to .env
2. Run: docker compose up --build
3. Open http://localhost:8000

Mock mode creates a clearly non-speech preview tone so the workflow can be tested without model weights.

## GPU/OpenVoice deployment
1. Use Linux, Docker, NVIDIA drivers and NVIDIA Container Toolkit.
2. Put a pinned OpenVoice V2 checkout and model files in ./models/openvoice.
3. Complete the isolated bridge in app/engines/openvoice.py against that exact upstream revision.
4. Set VOICE_ENGINE=openvoice in .env.
5. Run: docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build

The adapter intentionally fails closed until a reviewed upstream commit and checkpoints are pinned. This avoids executing changing third-party model code as though it were production-ready.

## API
- GET /api/health
- POST /api/voices
- GET /api/voices
- DELETE /api/voices/{voice_id}
- POST /api/generate
- GET /api/generations
- GET /media/{filename}

## Before public deployment
- Add HTTPS, login, per-user authorization and rate limits.
- Encrypt recordings and backups.
- Add content moderation and an abuse-reporting route.
- Retain consent audit records.
- Add appropriate audio disclosure/watermarking.
- Never expose the development container directly to the internet.

Application code is MIT licensed. Model weights and dependencies retain their own licenses.
