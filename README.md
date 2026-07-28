# AI Shopping Assistant

An agentic shopping assistant that understands user intent, searches products across multiple stores, compares options, and delivers context-aware recommendations powered by an LLM.

Built under the DSA Open Source Initiative.

---

## What It Does

- Accepts a free-text query from the user ("good serum for oily skin under Rs 600")
- Searches a multi-category product dataset across 3 stores
- Scores and ranks the top 3 products based on price, rating, and popularity
- Sends the top 3 to an LLM and returns a plain English recommendation
- Exposes everything via a single REST API endpoint

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
│   └── main.py            # FastAPI server — /chat and /health
│
├── data/
│   ├── products.csv       # Product dataset (multi-category, 3 stores)
│   └── clean_products.py  # Cleaning pipeline for scraped data
│
├── tests/
│   ├── test_search.py
│   ├── test_compare.py
│   └── test_recommend.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── CONTRIBUTING.md
│
├── config.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/datascience-one/ai-shopping-assitant.git
cd ai-shopping-assitant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Install the LLM SDK for whichever provider you are using:

```bash
pip install google-generativeai   # Gemini
pip install openai                # OpenAI
pip install anthropic             # Anthropic
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

### 5. Start the WooCommerce stores (Docker)

```bash
bash setup.sh
```

Then open `http://localhost:8080` to verify the store is running.

### 6. Run the API server

```bash
uvicorn backend.main:app --reload
```

API docs available at `http://localhost:8000/docs`

---

## Using the API

### Health check

```bash
curl http://localhost:8000/health
```

### Send a query

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "good serum for oily skin under 600"}'
```

With optional budget and category:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "serum", "max_budget": 600, "category": "Skincare"}'
```

### Sample response

```json
{
  "user_message": "good serum for oily skin under 600",
  "recommendation": "For oily skin on a budget, the Minimalist 10% Niacinamide Serum is your best pick at Rs 549 from Store C...",
  "top_products": [
    {
      "product_name": "Minimalist 10% Niacinamide Serum",
      "brand": "Minimalist",
      "store": "Store C",
      "price": 549,
      "mrp": 699,
      "rating": 4.5,
      "review_count": 4320,
      "score": 84.5
    }
  ]
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## How to Contribute

Read `docs/CONTRIBUTING.md` before raising a PR.

The short version:
- Create a branch: `git checkout -b your-name/feature-name`
- Make your changes
- Run `pytest tests/ -v` — all tests must pass
- Raise a PR and tag Varsha or Nandana for review

---

## Architecture

See `docs/ARCHITECTURE.md` for the full agent pipeline diagram and phase roadmap.

---

## Phase Roadmap

| Phase | Status | Focus |
|---|---|---|
| Phase 1 | In progress | Static CSV + LLM reasoning |
| Phase 2 | Upcoming | Live WooCommerce API across 3 stores |
| Phase 3 | Future | Conversation memory + personalisation |
| Phase 4 | Future | Observability, guardrails, multi-store Docker |
