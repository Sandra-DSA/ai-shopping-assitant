"""
data/clean_products.py
----------------------
Data Cleaning Pipeline — transforms raw scraped CSVs into our standard schema.

Run this script once Nandana brings the scraped data from Amazon, Flipkart, and a 3rd site.

Usage:
    python data/clean_products.py

Input:
    data/raw/amazon.csv
    data/raw/flipkart.csv
    data/raw/meesho.csv     (or whichever 3rd site)

Output:
    data/products.csv       (clean, merged, ready for the agents)

Students:
- Column name mapping is the first thing to fix — each site uses different names.
- TODO items show you what to handle in the cleaning step.
"""

import pandas as pd
import os
import re

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "products.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Column name mappings — maps each site's column names to our standard schema
# Update these once you see the actual scraped column names
# ─────────────────────────────────────────────────────────────────────────────

AMAZON_COLUMN_MAP = {
    "title": "product_name",
    "brand": "brand",
    "category": "category",
    "price": "price",
    "original_price": "mrp",
    "rating": "rating",
    "rating_count": "review_count",
    "description": "key_specs",
    # TODO: update these once you see the actual Amazon CSV columns
}

FLIPKART_COLUMN_MAP = {
    "product_name": "product_name",
    "brand": "brand",
    "category": "category",
    "selling_price": "price",
    "original_price": "mrp",
    "rating": "rating",
    "no_of_ratings": "review_count",
    "description": "key_specs",
    # TODO: update these once you see the actual Flipkart CSV columns
}

MEESHO_COLUMN_MAP = {
    "name": "product_name",
    "brand": "brand",
    "category": "category",
    "price": "price",
    "mrp": "mrp",
    "rating": "rating",
    "reviews": "review_count",
    "specs": "key_specs",
    # TODO: update these once you see the actual 3rd site CSV columns
}

# ─────────────────────────────────────────────────────────────────────────────
# Category normalisation — maps scraped category names to our standard set
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_MAP = {
    # Electronics
    "mobiles": "Electronics",
    "smartphones": "Electronics",
    "laptops": "Electronics",
    "headphones": "Electronics",
    "earphones": "Electronics",
    "electronics": "Electronics",
    # Beauty
    "beauty": "Beauty",
    "makeup": "Beauty",
    "lipstick": "Beauty",
    "foundation": "Beauty",
    # Skincare
    "skincare": "Skincare",
    "skin care": "Skincare",
    "moisturiser": "Skincare",
    "serum": "Skincare",
    "sunscreen": "Skincare",
    # Haircare
    "hair care": "Haircare",
    "haircare": "Haircare",
    "shampoo": "Haircare",
    "hair oil": "Haircare",
    # Fashion
    "clothing": "Fashion",
    "fashion": "Fashion",
    "footwear": "Fashion",
    "watches": "Fashion",
    # Home & Kitchen
    "home": "Home & Kitchen",
    "kitchen": "Home & Kitchen",
    "home & kitchen": "Home & Kitchen",
    # Grocery
    "grocery": "Grocery",
    "food": "Grocery",
    # Sports & Fitness
    "sports": "Sports & Fitness",
    "fitness": "Sports & Fitness",
    # Stationery
    "stationery": "Stationery",
    "office supplies": "Stationery",
}


def normalise_category(raw_category: str) -> str:
    """Maps a raw scraped category to our standard category name."""
    if not raw_category:
        return "Other"
    key = str(raw_category).lower().strip()
    return CATEGORY_MAP.get(key, raw_category.title())


def clean_price(price_str) -> float:
    """Strips currency symbols and commas, returns float."""
    if pd.isna(price_str):
        return 0.0
    cleaned = re.sub(r"[₹,\s]", "", str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def clean_rating(rating_str) -> float:
    """Extracts numeric rating from strings like '4.2 out of 5'."""
    if pd.isna(rating_str):
        return 0.0
    match = re.search(r"(\d+\.?\d*)", str(rating_str))
    return float(match.group(1)) if match else 0.0


def clean_review_count(count_str) -> int:
    """Extracts numeric review count from strings like '1,234 ratings'."""
    if pd.isna(count_str):
        return 0
    cleaned = re.sub(r"[,\s]", "", str(count_str))
    match = re.search(r"(\d+)", cleaned)
    return int(match.group(1)) if match else 0


def load_and_map(filepath: str, column_map: dict, store_name: str) -> pd.DataFrame:
    """
    Loads a raw scraped CSV, renames columns to our schema, adds store name.

    Args:
        filepath   : Path to the raw CSV file
        column_map : Dict mapping scraped column names to our schema
        store_name : Store A, Store B, or Store C

    Returns:
        pd.DataFrame with standardised columns
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath} — skipping")
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from {filepath}")

    # Keep only columns we have a mapping for
    available_cols = {k: v for k, v in column_map.items() if k in df.columns}
    df = df[list(available_cols.keys())].rename(columns=available_cols)

    # Add store identifier
    df["store"] = store_name

    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans a single store's dataframe — normalises prices, ratings, categories.
    """
    if df.empty:
        return df

    # Clean prices
    if "price" in df.columns:
        df["price"] = df["price"].apply(clean_price)
    if "mrp" in df.columns:
        df["mrp"] = df["mrp"].apply(clean_price)

    # If MRP is missing or 0, set it equal to price
    df["mrp"] = df.apply(lambda r: r["price"] if r.get("mrp", 0) == 0 else r["mrp"], axis=1)

    # Clean ratings
    if "rating" in df.columns:
        df["rating"] = df["rating"].apply(clean_rating)

    # Clean review counts
    if "review_count" in df.columns:
        df["review_count"] = df["review_count"].apply(clean_review_count)

    # Normalise categories
    if "category" in df.columns:
        df["category"] = df["category"].apply(normalise_category)

    # Add missing columns with defaults
    if "subcategory" not in df.columns:
        df["subcategory"] = ""
    if "pros" not in df.columns:
        df["pros"] = ""
    if "cons" not in df.columns:
        df["cons"] = ""
    if "stock_status" not in df.columns:
        df["stock_status"] = "in_stock"

    # Drop rows with missing product name or price
    df = df.dropna(subset=["product_name", "price"])
    df = df[df["price"] > 0]

    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicates products across stores.
    Same product from different stores stays as separate rows (different store column).
    Exact duplicates within the same store are removed.
    """
    before = len(df)
    df = df.drop_duplicates(subset=["product_name", "brand", "store"])
    after = len(df)
    print(f"Deduplication: {before} → {after} rows ({before - after} duplicates removed)")
    return df


def add_product_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a unique product_id to each row."""
    df = df.reset_index(drop=True)
    df["product_id"] = ["P" + str(i + 1).zfill(3) for i in range(len(df))]
    return df


def main():
    print("Starting data cleaning pipeline...\n")

    # ── Load raw data from each store ─────────────────────────────────────────
    amazon_df = load_and_map(
        filepath=os.path.join(RAW_DIR, "amazon.csv"),
        column_map=AMAZON_COLUMN_MAP,
        store_name="Store A",
    )

    flipkart_df = load_and_map(
        filepath=os.path.join(RAW_DIR, "flipkart.csv"),
        column_map=FLIPKART_COLUMN_MAP,
        store_name="Store B",
    )

    meesho_df = load_and_map(
        filepath=os.path.join(RAW_DIR, "meesho.csv"),
        column_map=MEESHO_COLUMN_MAP,
        store_name="Store C",
    )

    # ── Merge all stores ──────────────────────────────────────────────────────
    all_dfs = [df for df in [amazon_df, flipkart_df, meesho_df] if not df.empty]

    if not all_dfs:
        print("No raw data files found. Add CSVs to data/raw/ and try again.")
        return

    merged = pd.concat(all_dfs, ignore_index=True)
    print(f"\nMerged: {len(merged)} total rows from {len(all_dfs)} stores\n")

    # ── Clean ─────────────────────────────────────────────────────────────────
    cleaned = clean_dataframe(merged)

    # ── Deduplicate ───────────────────────────────────────────────────────────
    cleaned = deduplicate(cleaned)

    # ── Add product IDs ───────────────────────────────────────────────────────
    cleaned = add_product_ids(cleaned)

    # ── Reorder columns to match our schema ───────────────────────────────────
    column_order = [
        "product_id", "product_name", "brand", "category", "subcategory",
        "store", "price", "mrp", "rating", "review_count",
        "stock_status", "key_specs", "pros", "cons"
    ]
    existing_cols = [c for c in column_order if c in cleaned.columns]
    cleaned = cleaned[existing_cols]

    # ── Save ──────────────────────────────────────────────────────────────────
    cleaned.to_csv(OUTPUT_PATH, index=False)
    print(f"\nCleaned dataset saved to {OUTPUT_PATH}")
    print(f"Total products: {len(cleaned)}")
    print(f"\nCategory breakdown:")
    print(cleaned["category"].value_counts().to_string())

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 1: Update column maps
    #   - Once Nandana shares the raw CSVs, open them and check the actual
    #     column names. Update AMAZON_COLUMN_MAP, FLIPKART_COLUMN_MAP,
    #     MEESHO_COLUMN_MAP at the top of this file accordingly.
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 2: Improve category normalisation
    #   - Add more entries to CATEGORY_MAP for categories you find in the data
    #   - Categories not in the map will default to their raw value
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 3: Extract pros and cons automatically
    #   - If the scraped data has a description field, use the LLM to extract
    #     pros and cons from it automatically
    #   - Example prompt: "Given this product description, list 2-3 pros and
    #     1-2 cons in simple language: {description}"
    # ─────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    main()
