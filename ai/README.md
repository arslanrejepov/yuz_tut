# 🤖 ai/ — AI Pipeline (Technical Deep Dive)

This folder contains the full AI pipeline for the Turkmen location
suggestion app: **indexing → retrieval → ranking → generation**.
Below is the *why*, the *how*, and the experiments behind every
decision.

---

## 📁 Folder Structure

```
ai/
├── indexing/
│   ├── embed.py          # one-time: embed + write to Chroma
│   └── chroma_db/        # Chroma persistent storage (leave UUID subfolder untouched)
├── retrieval/
│   └── search.py         # LocationSearch: query → embed → cosine search
├── ranking/               # 🚧 in progress — filter/rank layer
├── generation/            # 🔜 upcoming — LLM formatter
├── config.py
└── requirements.txt
```

`data/` and `ai/` are siblings — `data/` only holds one-time
merge/dedup/embedding-text scripts. Their output
(`locations_embedding_ready.jsonl`) feeds directly into
`ai/indexing/embed.py`.

---

## 1️⃣ Data Preparation (`data/`)

📥 **Source:** 3,693 raw JSON files, in two formats:
- **"detail" files** — one business per file, full fields (`body_tm`, `hours`, `contacts`, `seo_keywords`)
- **"list/section" files** — paginated category listings, short fields only

🔧 **`merge_locations.py`** merges + dedupes by ID → **225 duplicates removed → 3,347 unique locations.**
After merging, *every* location ended up with full detail-format data (no list-only records survived).

🔧 **`build_embedding_text.py`** builds an `embedding_text` field per location:

```
name_tm | categories | address_tm | seo_keywords | body_tm[:300]
```

> 💡 `seo_keywords` was deliberately included to capture spelling
> variants (e.g. "esik/eshik/eşik").

📤 **Output:** `locations_embedding_ready.jsonl` — embedding text +
structured metadata (id, name_tm, address_tm, categories, lat/long,
`has_location`, star, review_count, is_open, round_the_clock, hours,
contacts, slug).

### 📍 The Missing-Coordinates Problem
~838 locations (~25%) have no lat/long. A building-name matching
backfill only recovered 22/838 — **not worth pursuing further.**
**Decision:** these locations stay in results (`has_location=false`)
but are ranked by relevance/rating only — no distance sort.

---

## 2️⃣ Indexing (`ai/indexing/`)

### 🏆 Embedding Model Selection — Evaluation

A 30-query Turkmen gold-set was used to benchmark 4 models on **hit@3**:

| Rank | Model | hit@3 |
|---|---|---|
| 🥇 | **multilingual-e5-base** | **0.81** ✅ *selected* |
| 🥈 | LaBSE | 0.68 |
| 🥉 | e5-small | 0.55 |
| 4️⃣ | MiniLM (paraphrase-multilingual) | 0.48 |

⚠️ **Critical detail:** e5 models require prefixes at inference time —
`"query: "` for search queries, `"passage: "` for documents. Skipping
this **degrades retrieval quality** — this is a non-negotiable rule.

### 🗄️ Vector Database
**Chroma** (local, persistent, no separate server) — collection name
`"locations"`, `metadata={"hnsw:space": "cosine"}`.

### 🌐 Infrastructure Migration
Initially indexed on Google Colab (GPU, for speed). CPU produces
**identical embeddings**, just slower. Later moved to a **fully local
pipeline**:

- `ai/indexing/embed.py` loads the JSONL, embeds with e5-base in
  batches of 64, writes to `ai/indexing/chroma_db`
- Local dev machine is based in China → direct HuggingFace access is
  blocked → solved with `HF_ENDPOINT=https://hf-mirror.com`
  (a SOCKS proxy caused errors with `huggingface_hub`, the mirror worked)
- ✅ Verified: `collection.count()` = **3347** after local re-embedding

---

## 3️⃣ Retrieval (`ai/retrieval/search.py`)

The `LocationSearch` class wraps `SentenceTransformer` + Chroma query:

1. Embeds the Turkmen query with the `"query: "` prefix
2. Runs cosine search against Chroma
3. Returns top-N results with score + embedding_text + metadata

### 🧪 Evaluation — 20 Realistic Turkmen Queries

**🟢 Works well** — direct/category-style queries (e.g. "restaurant",
"bookstore", "bank", "toy store", "fabric & sewing supplies") → score
~0.83–0.87, correct results. **No changes needed.**

**🔴 Fails** on:
- Indirect/situational queries (e.g. *"my hand is cut and bleeding, need a nearby pharmacy"*, *"my car broke down, need an auto service"*)
- Even direct-but-weak queries (e.g. *"need a pharmacy"* — the DB only has 11 weak/incidental matches, top result is irrelevant)

**Root cause:** pure embedding similarity can't extract intent/meaning
from free-form sentences. This is an **understanding** problem, not
something re-embedding alone can fix.

---

## 4️⃣ Query Understanding Layer 🚧 *(in progress)*

A layer inserted **before** retrieval:

### Stage 1 — Rule-Based Extractor ⚡ *(fast, cheap)*
- A synonym dictionary maps Turkmen keywords to categories
  (e.g. "aptek"/"derman" → "Pharmacy")
- A separate sort-intent detector picks up on signals like
  "cheap"/"best"/"nearby"/"open late" → `sort_by=rating/price/distance`,
  `open_now_only` flag

### Stage 2 — LLM Fallback 🧠 *(only when rule-based confidence is low)*
- Qwen2.5 extracts a category from indirect/situational free-form
  queries (e.g. *"my hand is cut and bleeding"* → **"Pharmacy"**)

The **extracted category** (not the raw sentence) is what gets passed
into `search.py`'s vector search — `search.py` itself stays unchanged,
since it already performs well on clean category-style queries.

The output of retrieval + this understanding layer feeds into
`ai/ranking/rank.py`, which applies sort intent and the open-now filter.

> 🚫 **Core principle:** this pipeline must never behave like a
> free-form generative chatbot. The LLM's only two jobs are:
> **(a)** classify the query into a category, and
> **(b)** format real DB results into a Turkmen sentence.
> It never invents a recommendation from its own knowledge.

---

## 5️⃣ What's Next 🔜

- ⚖️ `ai/ranking/rank.py` — open/closed filtering (hours,
  round_the_clock), distance sort (for `has_location=true` using user
  lat/long), rating/review_count as a tiebreaker; `has_location=false`
  records ranked by relevance/rating only
- ✍️ `ai/generation/` — Qwen2.5 as the default candidate; Gemma 4
  E2B/E4B QAT to be benchmarked separately. Open question: can the LLM
  generate short, coherent Turkmen suggestions directly from Turkmen
  context, without translation?
- 🌍 NLLB-200-distilled-600M reserved as a fallback path in
  generation only (not used in retrieval)
- ❌ mGPT already ruled out (incoherent, off-topic output in a Colab
  head-to-head test)
- 🔌 Backend interface (HTTP API vs. direct Python import) deferred
  until the full pipeline is built end-to-end

---

## 🧑‍💻 How Claude Was Used

Claude (Anthropic) was used throughout this project as a **technical
co-architect** — not as an autonomous code generator. Concretely:

- 🏗️ **Architecture discussions** — designing the 4-layer pipeline
  (indexing/retrieval/ranking/generation), establishing that
  recommendation logic is a lightweight filter/rank layer *inside*
  RAG, not a separate RecSys
- 🧪 **Experiment design** — building the 30-query Turkmen gold-set
  evaluation to select the embedding model (hit@3 metric,
  head-to-head comparison → e5-base won)
- 💻 **Code writing** — drafting/refining `merge_locations.py`,
  `build_embedding_text.py`, `ai/indexing/embed.py`,
  `ai/retrieval/search.py`
- 🔧 **Debugging** — solving the blocked-HuggingFace issue (HF
  mirror), Chroma configuration, and other practical infra snags
- 📊 **Evaluating retrieval results** — analyzing the 20-query test
  set, diagnosing *why* certain query types fail (an understanding
  problem, not a retrieval problem), and proposing the Query
  Understanding layer architecture as a fix
- 🧐 **Critical pushback** — flawed approaches (e.g. over-investing in
  coordinate backfilling, expecting pure embeddings to solve every
  query type) were flagged directly rather than validated —
  Claude did not rubber-stamp every idea

This section documents the AI-tool usage transparently, as required
for presenting this project as a flagship deliverable.
