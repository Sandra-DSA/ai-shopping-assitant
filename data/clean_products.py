#
# # SPDX-License-Identifier: Apache-2.0
# # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
# ##
"""
data/clean_products.py
----------------------
Data Cleaning Pipeline — transforms raw scraped CSVs into our standard schema.

Now category-aware: uses spec_profiles.py to handle different spec columns
per category rather than a one-size-fits-all approach.

Usage:
    python data/clean_products.py

Input:
    data/raw/amazon.csv      (smartphones from Amazon — Store A)
    data/raw/flipkart.csv    (smartphones from Flipkart — Store B)
    data/raw/meesho.csv      (smartphones from 3rd site — Store C)

Output:
    data/products.csv        (clean, merged, ready for agents)

Students:
- Column name mapping is in AMAZON_COLUMN_MAP / FLIPKART_COLUMN_MAP / MEESHO_COLUMN_MAP
- Spec profiles are in data/spec_profiles.py — edit there to add new categories
- TODO items show where to extend the pipeline
"""

import pandas as pd
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.spec_profiles import SPEC_PROFILES, get_profile

RAW_DIR    = os.path.join(os.path.dirname(__file__), "raw")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "products.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Column maps — maps each site's raw column names to our internal names
# These match Nandana's actual scraped columns
# ─────────────────────────────────────────────────────────────────────────────

AMAZON_COLUMN_MAP = {
    "product_name":       "product_name",
    "brand":              "brand",
    "selling_price":      "price",
    "mrp":                "mrp",
    "rating":             "rating",
    "review_count":       "review_count",
    "description":        "description",
    "ram":                "ram",
    "ram_source":         "ram_source",
    "storage":            "storage",
    "storage_source":     "storage_source",
    "processor":          "processor",
    "processor_source":   "processor_source",
    "battery":            "battery",
    "battery_source":     "battery_source",
    "display_size":       "display_size",
    "display_size_source":"display_size_source",
    "rear_camera":        "rear_camera",
    "rear_camera_source": "rear_camera_source",
    "front_camera":       "front_camera",
    "front_camera_source":"front_camera_source",
    "os":                 "os",
    "os_source":          "os_source",
    "ui_skin":            "ui_skin",
    "ui_skin_source":     "ui_skin_source",
}

# TODO: Update once Flipkart scraper is ready
FLIPKART_COLUMN_MAP = {
    "product_name":  "product_name",
    "brand":         "brand",
    "selling_price": "price",
    "mrp":           "mrp",
    "rating":        "rating",
    "review_count":  "review_count",
    "description":   "description",
    "ram":           "ram",
    "storage":       "storage",
    "processor":     "processor",
    "battery":       "battery",
    "display_size":  "display_size",
    "rear_camera":   "rear_camera",
    "os":            "os",
}

# TODO: Update once 3rd site scraper is ready
MEESHO_COLUMN_MAP = {
    "name":         "product_name",
    "brand":        "brand",
    "price":        "price",
    "mrp":          "mrp",
    "rating":       "rating",
    "reviews":      "review_count",
    "description":  "description",
    "ram":          "ram",
    "storage":      "storage",
    "processor":    "processor",
    "battery":      "battery",
    "display_size": "display_size",
    "rear_camera":  "rear_camera",
    "os":           "os",
}


# ─────────────────────────────────────────────────────────────────────────────
# Cleaning helpers
# ─────────────────────────────────────────────────────────────────────────────

def clean_price(val) -> float:
    """Strips ₹ and commas, returns float. Returns 0.0 on failure."""
    if pd.isna(val) or str(val).strip() in ["N/A", "", "nan"]:
        return 0.0
    cleaned = re.sub(r"[₹,\s]", "", str(val))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def clean_rating(val) -> float:
    """Extracts numeric rating. Handles '4.2 out of 5' style strings."""
    if pd.isna(val):
        return 0.0
    match = re.search(r"(\d+\.?\d*)", str(val))
    return float(match.group(1)) if match else 0.0


def clean_review_count(val) -> int:
    """Extracts integer review count. Handles '1,234 ratings' style strings."""
    if pd.isna(val):
        return 0
    cleaned = re.sub(r"[,\s]", "", str(val))
    match = re.search(r"(\d+)", cleaned)
    return int(match.group(1)) if match else 0


def clean_spec_value(val) -> str:
    """Cleans a spec value — strips whitespace, replaces N/A with empty."""
    if pd.isna(val) or str(val).strip() in ["N/A", "nan", ""]:
        return ""
    return str(val).strip()


def extract_numeric(val: str) -> float:
    """
    Extracts the first numeric value from a spec string.
    e.g. "6500 mAh" → 6500.0
         "6.72 inches" → 6.72
         "50 MP + 50 MP" → 50.0  (takes first number)
    """
    if not val:
        return 0.0
    match = re.search(r"(\d+\.?\d*)", str(val))
    return float(match.group(1)) if match else 0.0


def extract_ram_gb(val: str) -> float:
    """Extracts RAM in GB. Handles '8 GB', '12GB', '8 GB RAM'."""
    return extract_numeric(val)


def extract_storage_gb(val: str) -> float:
    """Extracts storage in GB. Handles '128 GB', '256GB'."""
    num = extract_numeric(val)
    if "TB" in str(val).upper():
        num *= 1024
    return num


def extract_battery_mah(val: str) -> float:
    """Extracts battery in mAh. Handles '6500 mAh', '7000mAh'."""
    return extract_numeric(val)


def extract_camera_mp(val: str) -> float:
    """Extracts primary camera MP. Takes the first number."""
    return extract_numeric(val)


def extract_display_inch(val: str) -> float:
    """Extracts display size in inches."""
    return extract_numeric(val)


def clean_product_name(name: str) -> str:
    """
    Shortens Amazon-style product titles.
    Removes colour variants and spec details crammed into the title.
    e.g. "REDMI Note 15 5G (Black, 8GB RAM 128GB Storage) | 108MP..."
      →  "Redmi Note 15 5G"
    """
    if not name:
        return name
    # Remove content in parentheses (colour, RAM info)
    name = re.sub(r'\(.*?\)', '', name)
    # Remove content after | or ,
    name = name.split('|')[0].split(',')[0]
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Spec confidence scoring
# ─────────────────────────────────────────────────────────────────────────────

def calculate_spec_confidence(row: pd.Series, profile: dict) -> str:
    """
    Calculates how reliable the spec data is for a product.

    Uses the _source columns from the scraper to determine if specs
    came from the structured spec table (most reliable), product title
    (reliable), or description text (least reliable).

    Returns: "high", "medium", or "low"
    """
    source_columns = profile.get("source_columns", {})
    trusted_sources = profile.get("trusted_sources", ["spec_table", "title"])

    if not source_columns:
        return "medium"

    reliable = 0
    total = 0

    for spec_col, source_col in source_columns.items():
        if source_col in row.index:
            source_val = str(row.get(source_col, "")).strip()
            if source_val and source_val not in ["N/A", "nan", ""]:
                total += 1
                if source_val in trusted_sources:
                    reliable += 1

    if total == 0:
        return "low"
    ratio = reliable / total
    if ratio >= 0.75:
        return "high"
    elif ratio >= 0.5:
        return "medium"
    return "low"


# ─────────────────────────────────────────────────────────────────────────────
# Spec string builder
# ─────────────────────────────────────────────────────────────────────────────

def build_key_specs(row: pd.Series, profile: dict) -> str:
    """
    Builds a clean key_specs display string from structured spec columns.

    Uses the display_specs mapping from the profile to know which
    columns to include and what label to use.

    e.g. "RAM: 8GB | Storage: 128GB | Processor: Snapdragon 6 Gen 3 |
          Battery: 5520mAh | Display: 6.7in | Rear Camera: 108MP | OS: Android 15"
    """
    display_specs = profile.get("display_specs", {})
    parts = []

    for label, col in display_specs.items():
        val = clean_spec_value(row.get(col, ""))
        if val:
            parts.append(f"{label}: {val}")

    return " | ".join(parts) if parts else ""


# ─────────────────────────────────────────────────────────────────────────────
# Numeric spec extraction for Compare Agent
# ─────────────────────────────────────────────────────────────────────────────

def extract_scoring_specs(row: pd.Series, profile: dict) -> dict:
    """
    Extracts numeric spec values used by the Compare Agent for scoring.

    Returns a dict of spec_name → numeric value.
    e.g. {"ram": 8.0, "storage": 128.0, "battery": 5520.0, ...}
    """
    scoring_specs = profile.get("scoring_specs", {})
    result = {}

    extractors = {
        "ram":          extract_ram_gb,
        "storage":      extract_storage_gb,
        "battery":      extract_battery_mah,
        "rear_camera":  extract_camera_mp,
        "display_size": extract_display_inch,
    }

    for spec_col, (unit, higher_is_better, max_val) in scoring_specs.items():
        raw_val = clean_spec_value(row.get(spec_col, ""))
        extractor = extractors.get(spec_col, extract_numeric)
        result[spec_col] = extractor(raw_val)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────

def load_and_map(filepath: str, column_map: dict, store_name: str) -> pd.DataFrame:
    """Loads raw CSV, maps columns to internal names, adds store label."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath} — skipping")
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from {filepath}")

    available = {k: v for k, v in column_map.items() if k in df.columns}
    df = df[list(available.keys())].rename(columns=available)
    df["store"] = store_name
    return df


def process_smartphones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies smartphone-specific cleaning using the Electronics/Smartphones profile.
    Adds: category, subcategory, key_specs, spec_confidence, and numeric spec columns.
    """
    if df.empty:
        return df

    profile = SPEC_PROFILES["Electronics/Smartphones"]

    # Clean prices
    df["price"] = df["price"].apply(clean_price)
    df["mrp"]   = df["mrp"].apply(clean_price)
    # If MRP missing, use price (0% discount)
    df["mrp"] = df.apply(
        lambda r: r["price"] if r["mrp"] == 0 else r["mrp"], axis=1
    )

    # Clean ratings and reviews
    df["rating"]       = df["rating"].apply(clean_rating)
    df["review_count"] = df["review_count"].apply(clean_review_count)

    # Preserve original name for deduplication
    df["raw_product_name"] = df["product_name"]

    # Clean name only for display
    df["product_name"] = df["product_name"].apply(clean_product_name)

    # Set category fields
    df["category"]    = profile["category"]
    df["subcategory"] = profile["subcategory"]

    # Build key_specs string
    df["key_specs"] = df.apply(
        lambda r: build_key_specs(r, profile), axis=1
    )

    # Calculate spec confidence per row
    df["spec_confidence"] = df.apply(
        lambda r: calculate_spec_confidence(r, profile), axis=1
    )

    # Extract numeric scoring specs as separate columns
    # These are used by the Compare Agent for spec-based scoring
    scoring_specs = profile.get("scoring_specs", {})
    for spec_col in scoring_specs:
        extractor_map = {
            "ram":          extract_ram_gb,
            "storage":      extract_storage_gb,
            "battery":      extract_battery_mah,
            "rear_camera":  extract_camera_mp,
            "display_size": extract_display_inch,
        }
        extractor = extractor_map.get(spec_col, extract_numeric)
        raw_col = spec_col if spec_col in df.columns else None
        if raw_col:
            df[f"spec_{spec_col}"] = df[raw_col].apply(
                lambda v: extractor(clean_spec_value(str(v)))
            )
        else:
            df[f"spec_{spec_col}"] = 0.0

    # Add default columns
    df["pros"]         = ""
    df["cons"]         = ""
    df["stock_status"] = "in_stock"

    # Drop rows missing name or price
    df = df.dropna(subset=["product_name", "price"])
    df = df[df["price"] > 0]

    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes exact duplicates within the same store.

    Uses the ORIGINAL product name rather than the cleaned display name.
    This prevents different variants from collapsing together after
    clean_product_name() removes RAM/storage/color information.
    """

    before = len(df)

    df = df.drop_duplicates(
        subset=["raw_product_name", "brand", "store", "price"]
    )

    after = len(df)

    print(
        f"Deduplication: {before} -> {after} rows "
        f"({before - after} removed)"
    )

    return df


def add_product_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Adds sequential product IDs."""
    df = df.reset_index(drop=True)
    df["product_id"] = ["P" + str(i + 1).zfill(3) for i in range(len(df))]
    return df


def main():
    print("Starting data cleaning pipeline...\n")

    # ── Load ──────────────────────────────────────────────────────────────────
    amazon_df   = load_and_map(
        os.path.join(RAW_DIR, "amazon.csv"),   AMAZON_COLUMN_MAP,   "Store A"
    )
    flipkart_df = load_and_map(
        os.path.join(RAW_DIR, "flipkart.csv"), FLIPKART_COLUMN_MAP, "Store B"
    )
    meesho_df   = load_and_map(
        os.path.join(RAW_DIR, "meesho.csv"),   MEESHO_COLUMN_MAP,   "Store C"
    )

    all_dfs = [df for df in [amazon_df, flipkart_df, meesho_df] if not df.empty]

    if not all_dfs:
        print("No raw data found. Add CSVs to data/raw/ and try again.")
        return

    merged = pd.concat(all_dfs, ignore_index=True)
    print(f"\nMerged: {len(merged)} rows from {len(all_dfs)} stores\n")

    # ── Process by category ───────────────────────────────────────────────────
    # Right now all data is smartphones — process with smartphone profile
    # When new categories arrive, add elif blocks here with their own processor
    cleaned = process_smartphones(merged)

    # ── Deduplicate ───────────────────────────────────────────────────────────
    cleaned = deduplicate(cleaned)

    # raw_product_name was only needed for deduplication
    if "raw_product_name" in cleaned.columns:
        cleaned = cleaned.drop(columns=["raw_product_name"])

    # ── Add IDs ───────────────────────────────────────────────────────────────
    cleaned = add_product_ids(cleaned)
    # ── Final column order ────────────────────────────────────────────────────
    base_columns = [
        "product_id", "product_name", "brand", "category", "subcategory",
        "store", "price", "mrp", "rating", "review_count",
        "stock_status", "key_specs", "spec_confidence",
        "pros", "cons",
    ]
    # Add numeric spec columns — exclude spec_confidence since it's
    # already in base_columns (it's a category label, not a numeric spec)
    spec_cols = [
        c for c in cleaned.columns
        if c.startswith("spec_") and c != "spec_confidence"
    ]
    column_order = base_columns + spec_cols
    existing = [c for c in column_order if c in cleaned.columns]
    cleaned = cleaned[existing]

    # ── Save ──────────────────────────────────────────────────────────────────
    cleaned.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")
    print(f"Total products: {len(cleaned)}")
    print(f"\nSpec confidence breakdown:")
    print(cleaned["spec_confidence"].value_counts().to_string())
    print(f"\nNumeric spec columns added:")
    for col in spec_cols:
        print(f"  {col}: {cleaned[col].describe()['mean']:.1f} avg")

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 1: Update FLIPKART_COLUMN_MAP and MEESHO_COLUMN_MAP
    #   - Once Flipkart and Meesho scrapers are ready, check actual column names
    #     and update the maps at the top of this file
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 2: Add new category processors
    #   - When laptops/earphones/skincare data arrives, add a new profile in
    #     data/spec_profiles.py and call it here:
    #     e.g. laptop_cleaned = process_laptops(laptop_df)
    #          final = pd.concat([cleaned, laptop_cleaned])
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # TODO 3: Auto-generate pros and cons using LLM
    #   - The description column has rich product text
    #   - Use Gemini/OpenAI to extract 2-3 pros and 1-2 cons per product
    #   - Only do this for products where pros/cons are empty
    # ─────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    main()
