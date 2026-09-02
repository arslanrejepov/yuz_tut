# 🗺️ Turkmen AI Suggestion App
### *A Meituan/Xiaotuan-style local discovery assistant*

---

## 🎯 Purpose

An app where users type anything in **Turkmen** — food, gifts, health,
general help, location-based needs — and get short, concrete
suggestions pulled from a **real database of 3,347 locations and
organizations** (restaurants, shops, supermarkets, services, etc.).

This is **not** free-form ChatGPT-style conversation. It's a
retrieval-grounded recommendation system (RAG) that only ever
surfaces real places from the database.

Inspired by the Meituan / Xiaotuan model.

---

## 👥 Team

| Role | Owner |
|---|---|
| 🧭 System / Engineering Lead | Senior Developer |
| ⚙️ Backend | Backend Engineer |
| 🤖 AI Pipeline | **Me** (AI Engineering Intern) |

My scope: embeddings, RAG, LLM, prompt engineering.
Backend, DevOps, infra, and frontend are owned by other teams.
This README covers the AI pipeline's progress.

---

## 🔒 Key Constraint: Fully Self-Hosted, CPU-Only

The backend server runs **inside Turkmenistan**, where external AI
APIs (OpenAI, Anthropic API, etc.) are **blocked at the network
level**. This shapes every decision:

- ✅ Everything must run **fully self-hosted**
- ✅ **No external API calls** of any kind
- ✅ **CPU-only** inference — no GPU in production
- ✅ Models must be quantized / lightweight

---

## 🧱 Pipeline Architecture (4 Layers)

```
① Indexing  →  ② Retrieval  →  ③ Filter/Rank  →  ④ Generation
 (offline)       (runtime)        (runtime)         (runtime)
```

| Layer | What it does |
|---|---|
| 🗂️ **1. Indexing** *(offline, one-time)* | Merge raw JSON → dedupe → build embedding text → embed → store in vector DB |
| 🔍 **2. Retrieval** *(runtime)* | Embed the Turkmen query directly (no translation) → cosine search → top-N candidates |
| ⚖️ **3. Filter/Rank** *(runtime)* | Plain-code filtering: open/closed, distance, rating |
| ✍️ **4. Generation** *(runtime)* | Small LLM turns top-N real results into a short Turkmen sentence — never invents anything |

---

## 📊 Current Status

### ✅ Data Preparation — Done
- **3,347 unique locations** extracted from 3,693 raw JSON files (225 duplicates removed)
- Every location now has full detail data (categories, address, hours, SEO keywords)
- 📍 ~838 locations (~25%) have no coordinates → kept in results, ranked by relevance/rating only (`has_location` flag)

### ✅ Indexing — Done
- **Embedding model: `multilingual-e5-base`** 🏆 — won a 30-query Turkmen gold-set evaluation

  | Model | hit@3 |
  |---|---|
  | 🥇 multilingual-e5-base | **0.81** |
  | 🥈 LaBSE | 0.68 |
  | 🥉 e5-small | 0.55 |
  | MiniLM | 0.48 |

- **Vector DB: Chroma** (local, persistent, no separate server needed)
- Migrated from Google Colab (GPU) to a **fully local pipeline** via `ai/indexing/embed.py`

### ✅ Retrieval — Done & Tested
- `ai/retrieval/search.py` built and validated
- 🟢 Direct/category queries ("late-night restaurant") → excellent results (score ~0.83–0.87)
- 🔴 Indirect/situational queries ("my hand is cut, bleeding, need a pharmacy nearby") → weak results — this is an *understanding* problem, not a retrieval-tuning problem

### 🚧 In Progress — Query Understanding Layer
A layer inserted **before** retrieval to translate messy natural
queries into clean categories + sort intent. (Full details in `ai/README.md`.)

### 🔜 Up Next
- `ai/ranking/rank.py` — filter/rank layer
- `ai/generation/` — LLM-based answer formatting (Qwen2.5 default, Gemma 4 E2B/E4B QAT under evaluation)

---

## 📁 Repository Structure

```
data/     📦 one-time data prep scripts + output JSONL
ai/       🤖 core AI pipeline
  ├── indexing/
  ├── retrieval/
  ├── ranking/
  ├── generation/
  ├── config.py
  └── requirements.txt
```

---

## 🛠️ Use of AI Tools

Claude (Anthropic) was used throughout this project as a **technical
co-architect** — for architecture discussions, designing evaluation
experiments, writing code, and documenting progress.
See **"How Claude Was Used"** in `ai/README.md` for full details.
