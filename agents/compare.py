"""
agents/compare.py
-----------------
Compare Agent — scores and ranks filtered products, returning the top 3.

This agent is responsible for:
- Taking filtered product results from the Search Agent
- Scoring each product based on price, rating, and popularity
- Grouping by store so the user sees the best option from each store
- Returning the top 3 ranked products

Students:
- The base scoring logic is implemented below.
- TODO items show you where to improve and extend the scoring.
- Do not change the function signatures — the Recommend Agent depends on them.
"""


def score_product(product: dict, max_budget: float = None) -> float:
    """
    Scores a single product on a 0–100 scale.

    Scoring weights (adjust these as you improve the logic):
        - Price score  : 40%  (lower price relative to MRP = better)
        - Rating score : 40%  (higher rating = better)
        - Popularity   : 20%  (higher review count = better, capped)

    Args:
        product    : A single product dict from the search results
        max_budget : User's stated budget (optional, used for price scoring)

    Returns:
        float: Score between 0 and 100
    """
    price = float(product.get("price", 0))
    mrp = float(product.get("mrp", price))
    rating = float(product.get("rating", 0))
    review_count = int(product.get("review_count", 0))

    # Price score — discount from MRP (higher discount = better value)
    discount_pct = ((mrp - price) / mrp) * 100 if mrp > 0 else 0
    price_score = min(discount_pct, 50) * 2  # cap at 50% discount = full 100

    # Rating score — scale 0–5 to 0–100
    rating_score = (rating / 5) * 100

    # Popularity score — cap review count at 10,000 for normalisation
    popularity_score = min(review_count / 10000, 1) * 100

    # Weighted total
    total = (price_score * 0.40) + (rating_score * 0.40) + (popularity_score * 0.20)

    return round(total, 2)


def compare_and_rank(products: list[dict], max_budget: float = None, top_n: int = 3) -> list[dict]:
    """
    Scores all products and returns the top N, one per store where possible.

    Args:
        products   : List of product dicts from the Search Agent
        max_budget : User's stated budget (passed to scorer)
        top_n      : Number of top products to return (default: 3)

    Returns:
        List of top N product dicts, each with an added "score" field.

    Example:
        >>> top = compare_and_rank(search_results, max_budget=500)
    """
    if not products:
        return []

    # Score each product
    for product in products:
        product["score"] = score_product(product, max_budget)

    # Sort by score descending
    sorted_products = sorted(products, key=lambda x: x["score"], reverse=True)

    # ── Pick best one per store ───────────────────────────────────────────────
    seen_stores = set()
    top_products = []

    for product in sorted_products:
        store = product.get("store")
        if store not in seen_stores:
            top_products.append(product)
            seen_stores.add(store)
        if len(top_products) == top_n:
            break

    # If fewer than top_n stores available, fill remaining slots from sorted list
    if len(top_products) < top_n:
        for product in sorted_products:
            if product not in top_products:
                top_products.append(product)
            if len(top_products) == top_n:
                break

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 1: Make scoring weights configurable
    #   - Right now weights are hardcoded (0.40, 0.40, 0.20).
    #   - Allow the user's intent to shift weights dynamically.
    #   - Example: if query contains "budget" or "cheap" → increase price_score weight
    #              if query contains "best" or "top rated" → increase rating_score weight
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 2: Add spec-based scoring for specific categories
    #   - For Electronics: factor in battery life, RAM, storage
    #   - For Skincare: factor in volume (ml/g per rupee = value for money)
    #   - For Fashion: factor in material quality keywords
    #   - Hint: parse the key_specs field and extract numeric values
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 3: Add a "value for money" metric
    #   - Calculate price per unit (e.g. price per ml for skincare,
    #     price per GB for electronics) and use it as an additional signal
    # ─────────────────────────────────────────────────────────────────────────

    return top_products
