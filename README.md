<!--
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
#-->
# AI Shopping Assistant

An agentic shopping assistant that understands user intent, searches products across multiple stores, compares options, and delivers context-aware recommendations powered by an LLM.

Built under the DSA Open Source Initiative.

---

## What It Does

- Accepts a free-text query from the user ("Best Samsung phone under ₹30,000")
- Searches a smartphone product dataset across multiple stores
- Scores and ranks the top products based on price, rating, popularity, and category-specific specs (RAM, battery, camera, storage)
- Sends the top products to an LLM and returns a plain English recommendation
- Exposes everything via a single REST API endpoint

This repository is licensed under **Apache License 2.0** — see [License](#license) below.

---

## Folder Structure

```
ai-shopping-assistant/
│
├── agents/
│   ├── search.py          # Filter phones by query, budget, category
│   ├── compare.py         # Score and rank top products (one per active store)
│   └── recommend.py       # Call LLM, return natural language reply
│
├── backend/
│   └── main.py            # FastAPI server — /chat and /health
│
├── data/
│   ├── products.csv          # Smartphone dataset (multiple stores)
│   ├── spec_profiles.py      # Category-aware spec scoring rules (RAM/battery/camera, etc.)
│   ├── clean_products.py     # Cleaning pipeline for raw scraped CSVs
│   ├── load_products.py      # Pushes cleaned products into WooCommerce via REST API
│   └── raw/                  # Raw scraped CSVs — not committed to GitHub
│
├── scripts/
│   └── add_license_header.py # Adds the Apache-2.0 SPDX header to Python files (run by pre-commit)
│
├── tests/
│   ├── test_search.py
│   ├── test_compare.py
│   ├── test_recommend.py
│   └── test_evals.py         # Evaluation tests — pipeline output quality and fairness
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── CONTRIBUTING.md
│
├── AGENTS.md               # Instructions for AI coding assistants (Claude Code, Copilot, Cursor)
├── config.py
├── requirements.txt
├── LICENSE                 # Apache License 2.0
├── license_header.txt      # Template used by scripts/add_license_header.py
├── .pre-commit-config.yaml # Pre-commit hooks (whitespace, EOF, YAML/JSON, license headers, etc.)
├── docker-compose.yml      # WooCommerce mock-store containers
├── setup.sh                # One-shot setup — macOS/Linux
├── setup.bat               # One-shot setup — Windows
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

### 5. Install the pre-commit hooks

```bash
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

These hooks automatically check for trailing whitespace, missing end-of-file
newlines, merge conflict markers, invalid YAML/JSON, large files, mixed line
endings, and the Apache-2.0 SPDX header on every Python file.

### 6. Set up your own WooCommerce stores (Docker)

Per Minu: this is no longer a centrally-hosted store — **every intern installs Docker and stands up their own Store A and Store B locally.** Follow this from a fresh start each time (don't assume anything is already running).

Containers, per Docker Compose:

| Store | Database | WordPress | WP-CLI | Port |
|---|---|---|---|---|
| Store A | `db` | `wordpress` | `wpcli` | 8080 |
| Store B | `db_b` | `wordpress_b` | `wpcli_b` | 8081 |
| Store C (reserved, no data yet) | `db_c` | `wordpress_c` | `wpcli_c` | 8082 |

1. **Open Docker Desktop.** Wait for the green whale icon in the system tray (~1-2 minutes).
2. **Open Git Bash** (right-click Desktop → "Git Bash Here", or search Start Menu).
3. **Navigate to your project folder:**
   ```bash
   cd /c/Users/<you>/Desktop/ai-shopping-assitant
   ```
4. **Activate your virtual environment:**
   ```bash
   source venv/Scripts/activate
   ```
   You should see `(venv)` at the start of the prompt.
5. **Place the raw datasets** at `data/raw/amazon.csv` (Store A) and `data/raw/flipkart.csv` (Store B), then confirm with `ls data/raw/`.
6. **Clean the data:**
   ```bash
   python data/clean_products.py
   ```
   Should print a product count and write `data/products.csv`. Spot-check with `head -3 data/products.csv`.
7. **Start all containers:**
   ```bash
   docker compose up -d
   docker ps
   ```
   Should list 6 containers (`db`, `wordpress`, `wpcli`, `db_b`, `wordpress_b`, `wpcli_b` — plus the reserved `_c` set). If empty, wait ~30 seconds and re-check.

#### Store A (Amazon dataset, port 8080)

8. **Install WordPress** (skip if it says already installed):
   ```bash
   docker compose run --rm wpcli core install \
     --url="http://localhost:8080" \
     --title="AI Shopping Assistant Store A" \
     --admin_user="admin" \
     --admin_password="admin123" \
     --admin_email="admin@example.com" \
     --allow-root
   ```
9. **Install WooCommerce:**
   ```bash
   docker compose run --rm wpcli plugin install woocommerce --activate --allow-root
   ```
10. **Permalink fix** — required after every fresh install, or `/wp-json/` returns HTML instead of JSON and the REST API calls below will fail:
    ```bash
    docker compose run --rm wpcli rewrite structure '/%postname%/' --hard --allow-root
    docker compose run --rm wpcli rewrite flush --hard --allow-root
    ```
11. **Basic Auth fix** — WooCommerce's REST API rejects Basic Auth over plain HTTP by default. On Windows Git Bash, prefix with `MSYS_NO_PATHCONV=1` or the path gets mangled:
    ```bash
    MSYS_NO_PATHCONV=1 docker compose exec -T wordpress mkdir -p /var/www/html/wp-content/mu-plugins
    MSYS_NO_PATHCONV=1 docker compose exec -T wordpress bash -c "cat > /var/www/html/wp-content/mu-plugins/enable-basic-auth.php << 'EOF'
    <?php
    add_filter( 'woocommerce_rest_is_request_to_rest_api', function() { return true; } );
    add_filter( 'woocommerce_rest_check_permissions', function( \$permission, \$context, \$object_id, \$post_type ) {
        return true;
    }, 10, 4 );
    EOF"
    docker compose restart wordpress
    ```
12. **Confirm the store loads** at `http://localhost:8080/wp-admin` (login `admin` / `admin123`) — you should see the WordPress dashboard with WooCommerce in the sidebar.
13. **Generate API keys:** WooCommerce → Settings → Advanced → REST API → Add key. User: `admin`, Permissions: `Read/Write`, then Generate — copy the Consumer key and Consumer secret.
14. **Add the keys to `.env`:**
    ```
    WC_CONSUMER_KEY=ck_paste_here
    WC_CONSUMER_SECRET=cs_paste_here
    ```
    Verify with `cat .env | grep WC_CONSUMER`.
15. **Load the products:**
    ```bash
    python data/load_products.py --store A --clear
    ```
    Should end with a success count and `0 failed`.

#### Store B (Flipkart dataset, port 8081)

Repeat the same process, swapping `wpcli` → `wpcli_b` and `wordpress` → `wordpress_b`:

```bash
docker compose run --rm wpcli_b core install \
  --url="http://localhost:8081" \
  --title="AI Shopping Assistant Store B" \
  --admin_user="admin" \
  --admin_password="admin123" \
  --admin_email="admin@example.com" \
  --allow-root

docker compose run --rm wpcli_b plugin install woocommerce --activate --allow-root

docker compose run --rm wpcli_b rewrite structure '/%postname%/' --hard --allow-root
docker compose run --rm wpcli_b rewrite flush --hard --allow-root

MSYS_NO_PATHCONV=1 docker compose exec -T wordpress_b mkdir -p /var/www/html/wp-content/mu-plugins
MSYS_NO_PATHCONV=1 docker compose exec -T wordpress_b bash -c "cat > /var/www/html/wp-content/mu-plugins/enable-basic-auth.php << 'EOF'
<?php
add_filter( 'woocommerce_rest_is_request_to_rest_api', function() { return true; } );
add_filter( 'woocommerce_rest_check_permissions', function( \$permission, \$context, \$object_id, \$post_type ) {
    return true;
}, 10, 4 );
EOF"
docker compose restart wordpress_b
```

Confirm at `http://localhost:8081/wp-admin`, generate a **separate** set of API keys, and add them to `.env` as `STORE_B_CONSUMER_KEY` / `STORE_B_CONSUMER_SECRET`. Then:

```bash
python data/load_products.py --store B --clear
```

**Verify both stores:**
- `http://localhost:8080/wp-admin/edit.php?post_type=product` (Store A)
- `http://localhost:8081/wp-admin/edit.php?post_type=product` (Store B)

Go through these one step at a time and confirm each test passes before moving to the next — don't skip ahead. Windows users can also try the one-shot `setup.bat`; macOS/Linux `bash setup.sh` — but if either script fails partway, fall back to the manual steps above so you can see exactly where it broke.

### 7. Run the API server

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
  -d '{"message": "best 5G phone under 25000"}'
```

With optional budget and category:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Samsung phone", "max_budget": 25000, "category": "Smartphones"}'
```

### Sample response

```json
{
  "user_message": "best 5G phone under 25000",
  "recommendation": "The Samsung Galaxy M36 5G offers the best overall value under your budget with its AMOLED display, reliable performance, excellent battery life, and strong camera system.",
  "top_products": [
    {
      "product_name": "Samsung Galaxy M36 5G",
      "brand": "Samsung",
      "store": "Store B",
      "price": 23999,
      "mrp": 26999,
      "rating": 4.6,
      "review_count": 3850,
      "score": 91.3
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

Read `docs/CONTRIBUTING.md` before raising a PR. If you're using an AI coding
assistant (Claude Code, Copilot, Cursor, etc.), point it at `AGENTS.md` first.

The short version:
- Create a branch: `git checkout -b your-name/feature-name`
- Make your changes, following the TODO comments already in the file
- Keep every Python file's Apache-2.0 SPDX header intact — the pre-commit hook adds it automatically for new files
- Run `pytest tests/ -v` — all existing tests must still pass
- Record a short demo video (max 3 minutes), upload it to your Google Drive folder, share it with `varsha.dsa2024@gmail.com`, and post the link in Discord
- Once approved by a mentor, commit and raise a PR — tag Varsha or Minu for review
- Never push directly to `main`, and never merge your own PR

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

---

## License

This project is licensed under the **Apache License 2.0** — see the `LICENSE` file for details.
Every Python source file carries an SPDX header:

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Data Science Academy Pvt. Ltd.
```

Headers are added automatically by `scripts/add_license_header.py` via the pre-commit hook — you shouldn't need to add them by hand, but never remove or reformat one on an existing file.
