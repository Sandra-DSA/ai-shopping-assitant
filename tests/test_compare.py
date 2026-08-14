#
# # SPDX-License-Identifier: Apache-2.0
# # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
# ##
"""
tests/test_compare.py
---------------------
Tests for the Compare Agent.

Run with:
    pytest tests/test_compare.py -v
"""

import pytest
from agents.compare import score_product, compare_and_rank


# ── Sample data ───────────────────────────────────────────────────────────────

def make_product(store="Store A", price=500, mrp=600, rating=4.2, review_count=1000, stock_status="in_stock"):
    return {
        "product_name": "Test Product",
        "brand": "Test Brand",
        "category": "Skincare",
        "store": store,
        "price": price,
        "mrp": mrp,
        "rating": rating,
        "review_count": review_count,
        "stock_status": stock_status,
        "key_specs": "Volume: 50ml",
        "pros": "Good",
        "cons": "None",
    }


# ── Scoring ───────────────────────────────────────────────────────────────────

def test_score_returns_float():
    product = make_product()
    score = score_product(product)
    assert isinstance(score, float), "Score should be a float"


def test_score_between_0_and_100():
    product = make_product()
    score = score_product(product)
    assert 0 <= score <= 100, f"Score {score} out of range 0-100"


def test_higher_discount_gives_higher_price_score():
    cheap = make_product(price=400, mrp=800)   # 50% discount
    expensive = make_product(price=750, mrp=800)  # 6.25% discount
    assert score_product(cheap) > score_product(expensive), "Higher discount should give higher score"


def test_higher_rating_gives_higher_score():
    good = make_product(rating=4.8, price=500, mrp=500)
    bad = make_product(rating=2.0, price=500, mrp=500)
    assert score_product(good) > score_product(bad), "Higher rating should give higher score"


def test_score_handles_zero_mrp():
    product = make_product(price=500, mrp=0)
    score = score_product(product)
    assert score >= 0, "Score should handle zero MRP without crashing"


# ── Ranking ───────────────────────────────────────────────────────────────────

def test_compare_returns_top_3():
    products = [make_product(store=f"Store {s}") for s in ["A", "B", "C"]]
    result = compare_and_rank(products)
    assert len(result) == 3, "Should return exactly 3 products"


def test_compare_returns_empty_for_empty_input():
    result = compare_and_rank([])
    assert result == [], "Should return empty list for empty input"


def test_compare_adds_score_field():
    products = [make_product()]
    result = compare_and_rank(products)
    assert "score" in result[0], "Each product should have a score field after ranking"


def test_compare_one_per_store():
    products = [
        make_product(store="Store A", price=300),
        make_product(store="Store A", price=400),
        make_product(store="Store B", price=350),
        make_product(store="Store C", price=320),
    ]
    result = compare_and_rank(products, top_n=3)
    stores = [r["store"] for r in result]
    assert len(stores) == len(set(stores)), "Should return one product per store"


def test_compare_sorted_by_score():
    products = [
        make_product(store="Store A", price=300, mrp=600, rating=4.5),
        make_product(store="Store B", price=580, mrp=600, rating=2.0),
        make_product(store="Store C", price=400, mrp=600, rating=3.5),
    ]
    result = compare_and_rank(products)
    scores = [r["score"] for r in result]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by score descending"
