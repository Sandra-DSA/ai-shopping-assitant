"""
backend/main.py
---------------
FastAPI server — the entry point for the AI Shopping Assistant.

Endpoints:
    POST /chat   — accepts a user message, runs the full agent pipeline,
                   returns a product recommendation
    GET  /health — health check

To run:
    uvicorn backend.main:app --reload

Students:
- The /chat endpoint wires together Search → Compare → Recommend.
- TODO items show you what to extend once the base is working.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.search import search_products
from agents.compare import compare_and_rank
from agents.recommend import get_recommendation

app = FastAPI(
    title="AI Shopping Assistant",
    description="An agentic shopping assistant that searches, compares, and recommends products.",
    version="0.1.0",
)


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    max_budget: float = None      # optional — user can specify budget
    category: str = None          # optional — user can specify category


class ProductResult(BaseModel):
    product_name: str
    brand: str
    store: str
    price: float
    mrp: float
    rating: float
    review_count: int
    key_specs: str
    pros: str
    cons: str
    score: float = None


class ChatResponse(BaseModel):
    user_message: str
    recommendation: str           # natural language response from LLM
    top_products: list[ProductResult]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint — runs the full agent pipeline.

    Pipeline:
        1. Search Agent  — filters products based on query + budget + category
        2. Compare Agent — scores and ranks filtered products, picks top 3
        3. Recommend Agent — sends top 3 to LLM, returns natural language reply

    Args:
        request: ChatRequest with user message, optional budget and category

    Returns:
        ChatResponse with LLM recommendation and top product details
    """

    # Step 1 — Search
    search_results = search_products(
        query=request.message,
        max_budget=request.max_budget,
        category=request.category,
    )

    if not search_results:
        raise HTTPException(
            status_code=404,
            detail="No products found matching your query. Try different keywords or a higher budget."
        )

    # Step 2 — Compare
    top_products = compare_and_rank(search_results, max_budget=request.max_budget)

    # Step 3 — Recommend
    recommendation = get_recommendation(request.message, top_products)

    return ChatResponse(
        user_message=request.message,
        recommendation=recommendation,
        top_products=[ProductResult(**p) for p in top_products],
    )


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Add conversation memory
#   - Right now every /chat call is stateless — the assistant has no memory
#     of previous messages in the same session.
#   - Add a session_id field to ChatRequest and maintain a conversation history
#     dict in memory (or Redis later).
#   - Pass the conversation history to the LLM so it can handle follow-ups
#     like "which of these is best for dry skin?" after a previous query.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# TODO 2: Add intent extraction
#   - Before calling the Search Agent, add an intent extraction step that
#     parses the user's message and automatically fills max_budget and category.
#   - Example: "I need a good lipstick under Rs 400" should automatically set
#     max_budget=400 and category="Beauty" without the user specifying them.
#   - You can use the LLM itself or a simple regex-based extractor for this.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# TODO 3: Connect to live WooCommerce stores
#   - Right now the system reads from a static CSV file.
#   - In Phase 2, replace the CSV with live WooCommerce API calls.
#   - Endpoint: GET {WP_BASE_URL}/wp-json/wc/v3/products
#   - See add_users.py for the auth pattern (consumer key + secret).
# ─────────────────────────────────────────────────────────────────────────────
