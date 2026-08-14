from pathlib import Path

HEADER = """# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Data Science Academy Pvt. Ltd.

"""

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

for file in ROOT.rglob("*.py"):
    if any(part in EXCLUDE_DIRS for part in file.parts):
        continue

    content = file.read_text(encoding="utf-8")

    if "SPDX-License-Identifier" in content:
        continue

    file.write_text(HEADER + content, encoding="utf-8")
    print(f"Added header -> {file}")

print("\nDone.")
