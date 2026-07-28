"""
tests/test_search.py
--------------------
Tests for the Search Agent.

Run with:
    pytest tests/test_search.py -v
"""

import pytest
from agents.search import search_products, load_products


# ── Dataset loading ───────────────────────────────────────────────────────────

def test_load_products_returns_dataframe():
    df = load_products()
    assert len(df) > 0, "Product dataset should not be empty"


def test_load_products_has_required_columns():
    df = load_products()
    required = ["product_id", "product_name", "brand", "category", "store", "price", "mrp", "rating", "stock_status"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


# ── Keyword search ────────────────────────────────────────────────────────────

def test_search_returns_results_for_valid_query():
    results = search_products(query="lipstick")
    assert len(results) > 0, "Should return results for 'lipstick'"


def test_search_returns_empty_for_unknown_query():
    results = search_products(query="xyzproductthatdoesnotexist123")
    assert results == [], "Should return empty list for unknown query"


def test_search_is_case_insensitive():
    lower = search_products(query="lipstick")
    upper = search_products(query="LIPSTICK")
    assert len(lower) == len(upper), "Search should be case insensitive"


# ── Budget filter ─────────────────────────────────────────────────────────────

def test_search_respects_budget():
    results = search_products(query="serum", max_budget=400)
    for r in results:
        assert r["price"] <= 400, f"Product price {r['price']} exceeds budget 400"


def test_search_with_zero_budget_returns_empty():
    results = search_products(query="lipstick", max_budget=0)
    assert results == [], "Budget of 0 should return no results"


# ── Category filter ───────────────────────────────────────────────────────────

def test_search_filters_by_category():
    results = search_products(query="", category="Electronics")
    for r in results:
        assert r["category"].lower() == "electronics", f"Expected Electronics, got {r['category']}"


def test_search_category_is_case_insensitive():
    lower = search_products(query="", category="skincare")
    upper = search_products(query="", category="Skincare")
    assert len(lower) == len(upper), "Category filter should be case insensitive"


# ── Stock filter ──────────────────────────────────────────────────────────────

def test_search_excludes_out_of_stock():
    results = search_products(query="")
    for r in results:
        assert r["stock_status"] != "out_of_stock", "Out of stock products should be excluded"


# ── Combined filters ──────────────────────────────────────────────────────────

def test_search_combined_query_budget_category():
    results = search_products(query="serum", max_budget=600, category="Skincare")
    for r in results:
        assert r["price"] <= 600
        assert r["category"].lower() == "skincare"
