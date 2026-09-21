## PR Checklist

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No `.env` file committed
- [ ] No `data/raw/*.csv` files committed
- [ ] License header present in all new Python files
- [ ] Function docstrings and type hints added

### Security
- [ ] No hardcoded API keys, URLs, or passwords in source files
- [ ] No real credentials in any committed file
- [ ] LLM provider routed through `config.LLM_PROVIDER` — not hardcoded
- [ ] No auto-purchasing or live transaction logic added
- [ ] WooCommerce keys only in `.env`, never in source

### Agent Safety (Phase 3+)
- [ ] ReAct loop has a hard iteration cap (max 3-5 loops)
- [ ] LLM fallback returns a clear placeholder — never crashes silently
- [ ] New tools do not expose write access to production data

### PR Description
- [ ] What was changed and why is clearly stated
- [ ] Demo video uploaded (max 3 min) and link posted in Discord
- [ ] Branch follows naming convention: `internname/feature-name`
- [ ] Reviewer tagged (@Varsha or @Nandana)
