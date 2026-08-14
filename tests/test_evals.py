#
# # SPDX-License-Identifier: Apache-2.0
# # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
# ##

"""
tests/test_evals.py
-------------------
Evaluation tests for the AI Shopping Assistant pipeline.

Unlike unit tests which check if code works correctly, evals check
if the agent OUTPUT is actually good — relevance, correctness, fairness.

Three eval levels:
    Level 1  Rule-based evals (this file) — fast, free, no LLM needed
    Level 2  LLM-as-judge evals           — Phase 3 (see TODOs)
    Level 3  LangSmith dataset evals      — Phase 4 (see TODOs)

Run with:
    pytest tests/test_evals.py -v

Based on real scraped dataset (100 Amazon smartphones):
    Price range : Rs 449 – Rs 1,72,999
    Brands      : Samsung, Redmi, OnePlus, Apple, Motorola, vivo, realme, etc.
    Specs       : RAM 3–16 GB | Battery 3505–7400 mAh | 23 brands

Students: Level 1 evals are fully implemented below.
          Level 2 and 3 are marked as TODOs for you to build.
"""

import pytest
from agents.search import search_products
from agents.compare import compare_and_rank, score_product


# ─────────────────────────────────────────────────────────────────────────────
# Golden test scenarios — real user queries with expected behaviour
# Based on the actual scraped Amazon smartphone dataset
# ─────────────────────────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "Budget phone under 10k",
        "query": "budget smartphone",
        "max_budget": 10000,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": True,
        "min_expected_results": 1,
    },
    {
        "name": "Mid-range phone 15k-25k",
        "query": "good phone",
        "max_budget": 25000,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": True,
        "min_expected_results": 3,
    },
    {
        "name": "Premium phone no budget cap",
        "query": "flagship phone",
        "max_budget": None,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "Impossible budget — nothing exists under Rs 100",
        "query": "smartphone",
        "max_budget": 100,
        "category": "Electronics",
        "expect_results": False,
        "expect_within_budget": True,
        "min_expected_results": 0,
    },
    {
        "name": "Brand search — Samsung",
        "query": "Samsung",
        "max_budget": None,
        "category": None,
        "expect_results": None,   # None = depends on dataset version
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "Brand search — OnePlus",
        "query": "OnePlus",
        "max_budget": None,
        "category": None,
        "expect_results": None,   # None = depends on dataset version
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "Battery-focused search",
        "query": "long battery phone",
        "max_budget": None,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "Camera-focused search",
        "query": "best camera phone",
        "max_budget": None,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "5G phone search",
        "query": "5G phone",
        "max_budget": None,
        "category": "Electronics",
        "expect_results": True,
        "expect_within_budget": False,
        "min_expected_results": 1,
    },
    {
        "name": "Completely irrelevant query",
        "query": "xyznonexistentproduct999abc",
        "max_budget": None,
        "category": None,
        "expect_results": False,
        "expect_within_budget": False,
        "min_expected_results": 0,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 1 — Search returns results when expected, empty when not
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_search_returns_expected_results(scenario):
    """Search should return results for valid queries and nothing for impossible ones."""
    results = search_products(
        query=scenario["query"],
        max_budget=scenario["max_budget"],
        category=scenario["category"],
    )
    if scenario["expect_results"] is None:
        pytest.skip("Result expectation depends on dataset version — skip on placeholder data")
    elif scenario["expect_results"]:
        assert len(results) >= scenario["min_expected_results"], (
            f"[{scenario['name']}] Expected >= {scenario['min_expected_results']} results "
            f"for query='{scenario['query']}' budget={scenario['max_budget']} "
            f"but got {len(results)}"
        )
    else:
        assert len(results) == 0, (
            f"[{scenario['name']}] Expected 0 results "
            f"for query='{scenario['query']}' budget={scenario['max_budget']} "
            f"but got {len(results)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 2 — Budget is always respected — no product exceeds stated budget
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_budget_always_respected(scenario):
    """Every returned product must be within the stated budget."""
    if not scenario["expect_within_budget"] or scenario["max_budget"] is None:
        pytest.skip("No budget constraint for this scenario")

    results = search_products(
        query=scenario["query"],
        max_budget=scenario["max_budget"],
        category=scenario["category"],
    )
    for r in results:
        assert float(r["price"]) <= scenario["max_budget"], (
            f"[{scenario['name']}] Product '{r['product_name']}' "
            f"at Rs {r['price']} exceeds budget Rs {scenario['max_budget']}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 3 — Compare returns at most 3 results and one per store
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_compare_returns_at_most_3_one_per_store(scenario):
    """
    Compare agent must return at most 3 products, with no duplicate
    PRODUCTS, and store diversity maximised given how many distinct
    stores actually have matching data.

    NOTE: If fewer distinct stores than top_n exist in the results,
    some store repetition is mathematically unavoidable and correct.
    This test only requires that EVERY distinct available store is
    represented at least once when there are enough slots to do so —
    not that there are zero repeats regardless of store count.
    """
    results = search_products(
        query=scenario["query"],
        max_budget=scenario["max_budget"],
        category=scenario["category"],
    )
    if not results:
        pytest.skip("No results to compare")

    top = compare_and_rank(results, max_budget=scenario["max_budget"])

    assert len(top) <= 3, (
        f"[{scenario['name']}] Compare returned {len(top)} products, max allowed is 3"
    )

    product_ids = [p.get("product_id") for p in top]
    assert len(product_ids) == len(set(product_ids)), (
        f"[{scenario['name']}] Duplicate products in results: {product_ids}"
    )

    unique_stores_available = set(p["store"] for p in results)
    stores_in_top = set(p["store"] for p in top)
    expected_distinct_stores = min(len(unique_stores_available), 3)

    assert len(stores_in_top) == expected_distinct_stores, (
        f"[{scenario['name']}] Expected {expected_distinct_stores} distinct "
        f"stores represented (available: {unique_stores_available}), "
        f"but top results only cover: {stores_in_top}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# EVAL 4 — Results are always sorted by score descending
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_results_sorted_by_score(scenario):
    """Top products must be in descending score order."""
    results = search_products(
        query=scenario["query"],
        max_budget=scenario["max_budget"],
        category=scenario["category"],
    )
    if not results:
        pytest.skip("No results")

    top = compare_and_rank(results, max_budget=scenario["max_budget"])
    if len(top) < 2:
        pytest.skip("Not enough products to check sort order")

    scores = [p["score"] for p in top]
    assert scores == sorted(scores, reverse=True), (
        f"[{scenario['name']}] Results not sorted by score: {scores}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 5 — All scores are within valid 0-100 range
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_scores_within_valid_range(scenario):
    """Every product score must be between 0 and 100."""
    results = search_products(
        query=scenario["query"],
        max_budget=scenario["max_budget"],
        category=scenario["category"],
    )
    if not results:
        pytest.skip("No results")

    top = compare_and_rank(results, max_budget=scenario["max_budget"])
    for p in top:
        assert 0 <= p["score"] <= 100, (
            f"[{scenario['name']}] Score {p['score']} out of range "
            f"for '{p['product_name']}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 6 — No out-of-stock products ever appear in results
# ─────────────────────────────────────────────────────────────────────────────

def test_no_out_of_stock_in_any_results():
    """Search must never return out-of-stock products."""
    results = search_products(query="")
    for r in results:
        assert r["stock_status"] != "out_of_stock", (
            f"Out-of-stock product '{r['product_name']}' appeared in results"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 7 — Scoring fairness — higher rating wins at same price
# ─────────────────────────────────────────────────────────────────────────────

def test_higher_rating_wins_at_same_price():
    """A product with a better rating should always score higher at the same price."""
    base = {
        "price": 15000, "mrp": 15000,
        "review_count": 1000,
        "category": "Electronics", "subcategory": "Smartphone",
        "spec_confidence": "low",
        "spec_ram": 0.0, "spec_storage": 0.0, "spec_battery": 0.0,
        "spec_rear_camera": 0.0, "spec_display_size": 0.0,
    }
    good = {**base, "rating": 4.8}
    bad  = {**base, "rating": 2.5}

    assert score_product(good) > score_product(bad), (
        "Product with higher rating should score higher at the same price"
    )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 8 — Scoring fairness — better discount wins at same rating
# ─────────────────────────────────────────────────────────────────────────────

def test_better_discount_wins_at_same_rating():
    """A product with a larger MRP discount should score higher at the same rating."""
    base = {
        "rating": 4.0, "review_count": 500,
        "category": "Electronics", "subcategory": "Smartphone",
        "spec_confidence": "low",
        "spec_ram": 0.0, "spec_storage": 0.0, "spec_battery": 0.0,
        "spec_rear_camera": 0.0, "spec_display_size": 0.0,
    }
    discounted = {**base, "price": 10000, "mrp": 20000}  # 50% off
    full_price = {**base, "price": 19800, "mrp": 20000}  # 1% off

    assert score_product(discounted) > score_product(full_price), (
        "Product with bigger discount should score higher at same rating"
    )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 9 — Spec confidence affects scoring correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_high_confidence_specs_score_higher_than_low():
    """
    Two identical products, same specs, but one has high spec confidence and
    the other has low. High confidence should score higher or equal — never lower.
    """
    base = {
        "price": 15000, "mrp": 20000, "rating": 4.2,
        "review_count": 2000,
        "category": "Electronics", "subcategory": "Smartphone",
        "spec_ram": 8.0, "spec_storage": 128.0,
        "spec_battery": 5000.0, "spec_rear_camera": 50.0,
        "spec_display_size": 6.5,
    }
    high_conf = {**base, "spec_confidence": "high"}
    low_conf  = {**base, "spec_confidence": "low"}

    assert score_product(high_conf) >= score_product(low_conf), (
        "High spec confidence should never score lower than low confidence"
    )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 10 — Real dataset: budget phones under 10k exist and are findable
# ─────────────────────────────────────────────────────────────────────────────

def test_real_dataset_budget_phones_exist():
    """
    With the real scraped dataset (min price Rs 449), there must be phones
    available under Rs 10,000.
    """
    results = search_products(query="phone", max_budget=10000)
    assert len(results) > 0, (
        "Expected budget phones under Rs 10,000 in the dataset but found none. "
        "Check that products.csv is the cleaned scraped data."
    )
    for r in results:
        assert float(r["price"]) <= 10000, (
            f"Product '{r['product_name']}' at Rs {r['price']} exceeds Rs 10,000 budget"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 11 — Real dataset: known brands are searchable
# ─────────────────────────────────────────────────────────────────────────────

def _is_scraped_dataset() -> bool:
    """
    Returns True if products.csv contains the real scraped Amazon smartphone
    data (Phase 2 — 100 products, brands like Samsung/OnePlus/Motorola).
    Returns False if it still has the Phase 1 multi-category placeholder data
    (brands like Lakme, Himalaya, boAt etc.).

    Detection logic: the placeholder data has Beauty/Skincare categories.
    The scraped smartphone data does not.
    """
    from agents.search import load_products
    df = load_products()
    placeholder_categories = {"Beauty", "Skincare", "Haircare"}
    has_placeholder = bool(placeholder_categories.intersection(set(df["category"].unique())))
    return not has_placeholder


@pytest.mark.parametrize("brand", ["Samsung", "Redmi", "OnePlus", "Motorola"])
def test_known_brands_are_searchable(brand):
    """
    Major smartphone brands from the scraped Amazon dataset must be searchable.

    NOTE: Skipped when products.csv is still Phase 1 placeholder data.
    Activates automatically once data/clean_products.py is run with real scraped data.

    INTERN TASK (Phase 2): Place amazon.csv in data/raw/, run data/clean_products.py,
    and this test will pass with zero code changes needed.
    """
    if not _is_scraped_dataset():
        pytest.skip(
            "Skipping — products.csv has Phase 1 placeholder data. "
            "Run data/clean_products.py with scraped data to activate."
        )
    results = search_products(query=brand)
    assert len(results) > 0, (
        f"Brand '{brand}' returned no results. "
        f"Ensure products.csv contains scraped smartphone data."
    )
    brand_lower = brand.lower()
    matching = [
        r for r in results
        if brand_lower in r.get("brand", "").lower()
        or brand_lower in r.get("product_name", "").lower()
    ]
    assert len(matching) > 0, (
        f"Results for '{brand}' don't include '{brand}' products. "
        f"Got: {set(r.get('brand','') for r in results)}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# EVAL 12 — Pipeline consistency — same query always returns same results
# ─────────────────────────────────────────────────────────────────────────────

def test_pipeline_is_deterministic():
    """
    The same query run twice should return the same products in the same order.
    Pipeline must be deterministic (no random sampling, no shuffling).
    """
    query = "Samsung phone under 30000"
    budget = 30000

    run1 = compare_and_rank(search_products(query=query, max_budget=budget))
    run2 = compare_and_rank(search_products(query=query, max_budget=budget))

    names1 = [p["product_name"] for p in run1]
    names2 = [p["product_name"] for p in run2]

    assert names1 == names2, (
        f"Pipeline is not deterministic. "
        f"Run 1: {names1} | Run 2: {names2}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TODO — Level 2: LLM-as-judge evals (implement in Phase 3)
# ─────────────────────────────────────────────────────────────────────────────
#
# Once the LLM integration is working, add evals that score the recommendation
# text itself using a second LLM call as a judge.
#
# INTERN TASK: Implement this function and add 3–5 golden test cases.
#
# def evaluate_recommendation(
#     query: str,
#     recommendation: str,
#     top_products: list[dict]
# ) -> dict:
#     """
#     Uses the LLM to score the recommendation on 4 criteria (1–5 each).
#
#     Args:
#         query:           The original user query
#         recommendation:  The LLM-generated recommendation text
#         top_products:    The top 3 products that were recommended
#
#     Returns:
#         dict with keys: relevance, accuracy, clarity, helpfulness, overall
#
#     Example judge prompt:
#         f'''
#         You are evaluating an AI shopping assistant response.
#         Score each criterion from 1 (poor) to 5 (excellent).
#
#         User asked for: "{query}"
#         Assistant responded: "{recommendation}"
#         Products shown: {top_products}
#
#         Criteria:
#         - relevance:    Does the recommendation match what the user asked for?
#         - accuracy:     Are product details (price, specs) correct?
#         - clarity:      Is the explanation easy to understand?
#         - helpfulness:  Would this help the user make a buying decision?
#
#         Respond ONLY in JSON (no markdown):
#         {{"relevance": 0, "accuracy": 0, "clarity": 0,
#           "helpfulness": 0, "overall": 0}}
#         '''
#     """
#     pass  # TODO: implement
#
#
# GOLDEN TEST CASES for Level 2:
# [
#     {"query": "best phone under 15000", "expect_mention": "Redmi"},
#     {"query": "Samsung phone with good camera", "expect_brand": "Samsung"},
#     {"query": "long battery phone", "expect_spec": "mAh"},
# ]
#
# MINIMUM PASSING SCORE: overall >= 3.5 average across all golden cases.
# If average drops below 3.5, the pipeline has regressed.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# TODO — Level 3: LangSmith dataset evals (implement in Phase 4)
# ─────────────────────────────────────────────────────────────────────────────
#
# Once LangSmith is set up, create a permanent eval dataset and run
# automated scoring on every PR.
#
# INTERN TASK: Set up the dataset and eval runner.
#
# from langsmith import Client
# from langsmith.evaluation import evaluate
#
# client = Client()
#
# # Create the dataset once
# dataset = client.create_dataset("shopping-assistant-golden")
# client.create_example(
#     inputs={"query": "best phone under 15000", "max_budget": 15000},
#     outputs={"expected_category": "Electronics", "min_results": 1}
# )
#
# # Define evaluator
# def result_count_evaluator(run, example):
#     results = run.outputs.get("top_products", [])
#     return {"score": len(results) > 0, "key": "has_results"}
#
# # Run evals
# evaluate(
#     lambda inputs: compare_and_rank(search_products(**inputs)),
#     data=dataset,
#     evaluators=[result_count_evaluator],
#     experiment_prefix="phase1-eval",
# )
# ─────────────────────────────────────────────────────────────────────────────
