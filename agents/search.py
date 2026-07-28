"""
agents/search.py
----------------
Search Agent — filters products from the dataset based on user query.

This agent is responsible for:
- Loading the product dataset
- Parsing the user's intent (category, budget, keywords)
- Returning a filtered list of matching products

Students:
- The basic filtering logic is implemented below as a starting point.
- TODO items show you where to extend and improve the logic.
- Do not change the function signatures — other agents depend on them.
"""

import pandas as pd
import os

# Path to the product dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/products.csv")


def load_products() -> pd.DataFrame:
    """
    Loads the product dataset from CSV.

    Returns:
        pd.DataFrame: All products
    """
    return pd.read_csv(DATA_PATH)


def search_products(query: str, max_budget: float = None, category: str = None) -> list[dict]:
    """
    Filters products based on a search query, optional budget, and optional category.

    Args:
        query      : Free-text search string from the user (e.g. "moisturiser for dry skin")
        max_budget : Maximum price the user is willing to pay (optional)
        category   : Product category to filter by (optional, e.g. "Skincare", "Electronics")

    Returns:
        List of matching product dicts. Returns empty list if no matches found.

    Example:
        >>> results = search_products("lipstick under 400", max_budget=400, category="Beauty")
    """
    df = load_products()

    # ── Category filter ──────────────────────────────────────────────────────
    if category:
        df = df[df["category"].str.lower() == category.lower()]

    # ── Budget filter ────────────────────────────────────────────────────────
    if max_budget is not None:
        df = df[df["price"] <= max_budget]

    # ── Keyword filter ───────────────────────────────────────────────────────
    # Searches across product name, brand, subcategory, and key_specs
    if query:
        keywords = query.lower().split()
        search_columns = ["product_name", "brand", "subcategory", "key_specs", "category"]

        def row_matches(row):
            combined = " ".join(str(row[col]).lower() for col in search_columns if col in row.index)
            return any(kw in combined for kw in keywords)

        df = df[df.apply(row_matches, axis=1)]

    # ── Stock filter ─────────────────────────────────────────────────────────
    if not df.empty:
        df = df[df["stock_status"] != "out_of_stock"]

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 1: Improve keyword matching
    #   - Right now it splits the query into words and does basic string matching.
    #   - Consider using fuzzy matching (e.g. fuzzywuzzy or rapidfuzz) so that
    #     "moisturizer" also matches "moisturiser", "mosturizer" etc.
    #   - Example: from rapidfuzz import fuzz
    #              fuzz.partial_ratio("moisturizer", "moisturiser") > 80
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 2: Handle synonyms and beauty-specific terms
    #   - "under eye cream" should also match "eye contour serum"
    #   - Build a small synonym dictionary for common beauty/product terms
    #   - Example: synonyms = {"moisturiser": ["moisturizer", "hydrating cream", "face cream"]}
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 3: Extract budget from the query automatically
    #   - Right now budget must be passed separately.
    #   - Add logic to detect "under 500", "below Rs 1000", "less than 2000"
    #     directly from the query string and set max_budget automatically.
    #   - Hint: use regex  re.search(r'under\s*(?:rs\.?\s*)?(\d+)', query, re.I)
    # ─────────────────────────────────────────────────────────────────────────

    return df.to_dict(orient="records")
