# Arthaya Backend — Multi-Agent Financial Intelligence Platform

High-performance FastAPI backend engine powering **Arthaya**: a multi-agent, multi-model stock intelligence system.

## 🏛️ Architecture Overview

```text
               FastAPI Backend API
                       │
             ┌─────────┼──────────┐
             ▼         ▼          ▼
          n8n Hub   Quant ML   Model Gateway
   (n8n.sushantkumaryadav) (XGBoost) (Claude/Gemini/Mistral/Groq)
```

- **API Layer**: FastAPI async endpoints with Server-Sent Events (SSE) streaming.
- **Orchestration**: Direct integration with deployed n8n instance at `https://n8n.sushantkumaryadav.com.np`.
- **Quant Predictive Layer**: Feature engineering & probabilistic ML (Logistic Regression, Random Forest, XGBoost).
- **Model Gateway**: Multi-model LLM router supporting Anthropic Claude, Google Gemini, Mistral AI, Groq, and OpenRouter.
- **Persistence**: SQLAlchemy 2.0 async engine with PostgreSQL & pgvector for semantic retrieval.

## 🚀 Getting Started

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Server runs at `http://localhost:8000`. API Documentation available at `http://localhost:8000/docs`.
