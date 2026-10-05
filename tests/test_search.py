#
# # SPDX-License-Identifier: Apache-2.0
# # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
# ##
"""
tests/test_search.py
--------------------
Tests for the Search Agent.

Run with:
    pytest tests/test_search.py -v
"""

import pytest
from unittest.mock import patch, Mock
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


def test_woocommerce_product_mapping():
    fake_product = {
        "id": 101,
        "name": "Samsung Galaxy Phone",
        "price": "19999",
        "regular_price": "21999",
        "sale_price": "19999",
        "stock_status": "instock",
        "short_description": "128GB storage, 5000mAh battery",
        "meta_data": [
            {"key": "dsa_brand", "value": "Samsung"},
            {"key": "dsa_category", "value": "Electronics"},
            {"key": "dsa_subcategory", "value": "Phone"},
            {"key": "dsa_store", "value": "Store A"},
            {"key": "dsa_rating", "value": "4.5"},
            {"key": "dsa_review_count", "value": "100"},
            {"key": "dsa_pros", "value": "Good battery"},
            {"key": "dsa_cons", "value": "Expensive"},
        ],
    }

    with patch("agents.search.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [fake_product]
        mock_get.return_value = mock_response

        from agents.search import _fetch_store_products, _map_wc_product_to_dict

        products = _fetch_store_products(
            "http://localhost:8080",
            "test-key",
            "test-secret",
        )

        assert len(products) == 1

        mapped = _map_wc_product_to_dict(products[0])

        assert mapped["product_id"] == "101"
        assert mapped["product_name"] == "Samsung Galaxy Phone"
        assert mapped["brand"] == "Samsung"
        assert mapped["store"] == "Store A"
        assert mapped["price"] == 19999
        assert mapped["rating"] == 4.5
        assert mapped["stock_status"] == "in_stock"

# ── Keyword search ────────────────────────────────────────────────────────────

def test_search_returns_results_for_valid_query():
    results = search_products(query="phone")
    assert len(results) > 0, "Should return results for 'phone'"


def test_search_returns_empty_for_unknown_query():
    results = search_products(query="xyzproductthatdoesnotexist123")
    assert results == [], "Should return empty list for unknown query"


def test_search_is_case_insensitive():
    lower = search_products(query="phone")
    upper = search_products(query="PHONE")
    assert len(lower) == len(upper), "Search should be case insensitive"


# ── Budget filter ─────────────────────────────────────────────────────────────

def test_search_respects_budget():
    results = search_products(query="phone", max_budget=1500)
    for r in results:
        assert r["price"] <= 1500, f"Product price {r['price']} exceeds budget 1500"


def test_search_with_zero_budget_returns_empty():
    results = search_products(query="phone", max_budget=0)
    assert results == [], "Budget of 0 should return no results"


# ── Category filter ───────────────────────────────────────────────────────────

def test_search_filters_by_category():
    results = search_products(query="", category="Electronics")
    for r in results:
        assert r["category"].lower() == "electronics", f"Expected Electronics, got {r['category']}"


def test_search_category_is_case_insensitive():
    lower = search_products(query="", category="electronics")
    upper = search_products(query="", category="Electronics")
    assert len(lower) == len(upper), "Category filter should be case insensitive"


# ── Stock filter ──────────────────────────────────────────────────────────────

def test_search_excludes_out_of_stock():
    results = search_products(query="")
    for r in results:
        assert r["stock_status"] != "out_of_stock", "Out of stock products should be excluded"


# ── Combined filters ──────────────────────────────────────────────────────────

def test_search_combined_query_budget_category():
    results = search_products(query="serum", max_budget=600, category="Electronics")
    for r in results:
        assert r["price"] <= 600
        assert r["category"].lower() == "electronics"
