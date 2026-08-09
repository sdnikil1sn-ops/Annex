# ANNEX — Architecture Overview

## Mission
**Learn Before You Believe.** ANNEX lets users verify claims found in media —
images, video, text, and documents — with transparent, explainable AI analysis.

## System context

```mermaid
flowchart LR
    U[User] -->|uses| M[Flutter Mobile]
    U -->|uses| W[React Web]
    U -->|uses| E[Browser Extension]
    M --> API[FastAPI API - Cloud Run]
    W --> API
    E --> API
    API --> PG[(Supabase Postgres)]
    API --> ST[(Supabase Storage)]
    API --> AUTH[Firebase Auth]
    API --> AI[OpenAI / Gemini]
    API --> OCR[Tesseract + OpenCV]
    API --> RQ[(Redis)]
    RQ --> CQ[Celery Workers]
