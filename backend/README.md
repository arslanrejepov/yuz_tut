# Yuz Tut — Backend

FastAPI backend for the Turkmen AI location-suggestion app.

## Stack
- FastAPI
- PostgreSQL (later)
- Redis (later)
- Docker Compose

## Local setup

\`\`\`bash
cp .env.example .env
docker compose up --build
\`\`\`

Then check:
\`\`\`bash
curl http://localhost:8000/health
# {"status": "ok"}
\`\`\`
