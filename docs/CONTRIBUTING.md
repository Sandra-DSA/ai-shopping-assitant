# Contributing to AI Shopping Assistant

## Workflow

1. Never push directly to `main`
2. Create a branch: `git checkout -b your-name/feature-name`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Raise a PR and tag Varsha or Nandana for review

## Branch Naming

```
your-name/what-you-built
```
Examples:
- `rahul/fuzzy-search`
- `priya/gemini-integration`
- `arun/compare-scoring`

## Commit Messages

Keep them short and clear:
```
feat: add fuzzy matching to search agent
fix: handle missing MRP in scoring
docs: update README setup steps
```

## Code Standards

- Add docstrings to every function
- Add type hints to function arguments and return values
- Do not hardcode API keys, URLs, or passwords — use `.env`
- Run `pytest` before raising a PR — do not raise a PR with failing tests

## File Ownership

| File | Owner |
|---|---|
| `agents/search.py` | Open to all |
| `agents/compare.py` | Open to all |
| `agents/recommend.py` | Open to all |
| `backend/main.py` | Open to all |
| `data/products.csv` | Nandana |
| `data/clean_products.py` | Open to all |
| `config.py` | Varsha |
| `docker-compose.yml` | Minu |

## Questions

Drop a message in the Discord channel. Tag Varsha for project questions, Minu for Docker/setup questions.
