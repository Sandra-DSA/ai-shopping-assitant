<!--
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
#-->
# Architecture — AI Shopping Assistant

## Overview

The AI Shopping Assistant is a Phase 1 agentic system that accepts a user query,
searches a product dataset, ranks the top 3 results, and returns a natural language
recommendation powered by an LLM.

---

## Agent Pipeline

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│         FastAPI  /chat  endpoint         │
│           backend/main.py                │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │  Search Agent    │  agents/search.py
        │                  │
        │  - Loads CSV     │
        │  - Keyword match │
        │  - Budget filter │
        │  - Category filter│
        │  - Stock filter  │
        └────────┬─────────┘
                 │ filtered products list
        ┌────────▼────────┐
        │  Compare Agent   │  agents/compare.py
        │                  │
        │  - Scores 0-100  │
        │  - Price 40%     │
        │  - Rating 40%    │
        │  - Popularity 20%│
        │  - Top 3 ranked  │
        │  - 1 per store   │
        └────────┬─────────┘
                 │ top 3 products
        ┌────────▼────────┐
        │ Recommend Agent  │  agents/recommend.py
        │                  │
        │  - Builds prompt │
        │  - Calls LLM     │
        │  - Returns reply │
        └────────┬─────────┘
                 │
    ┌────────────▼────────────────┐
    │        LLM Provider          │
    │  Gemini / OpenAI / Anthropic │
    └────────────┬─────────────────┘
                 │
    ┌────────────▼────────────────┐
    │       ChatResponse           │
    │  - recommendation  (text)    │
    │  - top_products    (list)    │
    └──────────────────────────────┘
```

---

## Folder Structure

```
ai-shopping-assistant/
│
├── agents/
│   ├── search.py          # Filter products by query, budget, category
│   ├── compare.py         # Score and rank top 3 products
│   └── recommend.py       # Call LLM, return natural language reply
│
├── backend/
│   └── main.py            # FastAPI server — /chat and /health endpoints
│
├── data/
│   ├── products.csv       # Product dataset (multi-category, 3 stores)
│   └── clean_products.py  # Cleaning pipeline for raw scraped data
│
├── tests/
│   ├── test_search.py
│   ├── test_compare.py
│   └── test_recommend.py
│
├── docs/
│   ├── ARCHITECTURE.md    # This file
│   └── CONTRIBUTING.md    # PR workflow and coding standards
│
├── config.py              # Loads all env vars from .env
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── .gitignore
```

---

## Data Schema

Every product in `products.csv` has these fields:

| Field | Description |
|---|---|
| product_id | Unique ID e.g. P001 |
| product_name | Full product name |
| brand | Brand name |
| category | Electronics, Beauty, Skincare, Haircare, Fashion, Home & Kitchen, Grocery, Sports & Fitness, Stationery |
| subcategory | Earphones, Serum, Lipstick etc. |
| store | Store A (Amazon), Store B (Flipkart), Store C (Meesho) |
| price | Selling price in INR |
| mrp | Maximum retail price in INR |
| rating | Average rating 0–5 |
| review_count | Number of reviews |
| stock_status | in_stock, low_stock, out_of_stock |
| key_specs | Key product specifications |
| pros | 2–3 pros |
| cons | 1–2 cons |

---

## Agent Stack Layer Mapping (O'Reilly 2026)

| Layer | What it is | Phase 1 Implementation |
|---|---|---|
| 1. Models & Inference | LLM powering the agent | Gemini / OpenAI / Anthropic — configurable via .env |
| 2. Protocols & Tools | How agent accesses data | Static CSV (Phase 1) → Live WooCommerce API (Phase 2) |
| 3. Memory & Knowledge | What the agent knows | products.csv (Phase 1) → Postgres + vector search (Phase 3) |
| 4. Frameworks & SDKs | Orchestration | Raw FastAPI — no framework overhead needed for Phase 1 |
| 5. Eval & Observability | Measuring quality | pytest unit tests (Phase 1) → LangSmith tracing (Phase 3) |
| 6. Guardrails & Safety | Preventing misuse | Input validation via Pydantic (Phase 1) → full guardrails (Phase 4) |

---

## Phase Roadmap

| Phase | Focus | Key Addition |
|---|---|---|
| 1 | Static dataset + LLM reasoning | CSV → Search → Compare → Recommend |
| 2 | Live multi-store comparison | WooCommerce REST API replaces CSV |
| 3 | Memory + personalisation | Conversation history, user preferences |
| 4 | Full WooCommerce + Docker multi-store | 3 live stores, observability, guardrails |
