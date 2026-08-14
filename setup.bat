::
:: # SPDX-License-Identifier: Apache-2.0
:: # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
:: #::
@echo off
title Data Science Academy Git Setup

echo ==========================================
echo Data Science Academy - Git Setup
echo ==========================================
echo.

echo Installing pre-commit...
python -m pip install pre-commit

echo.
echo Installing Git hooks...
pre-commit install

echo.
echo Running initial setup...
pre-commit install-hooks

echo.
echo ==========================================
echo Setup Complete!
echo.
echo From now on every git commit will:
echo.
echo  * Remove trailing spaces
echo  * Fix missing end-of-file newlines
echo  * Check YAML files
echo  * Check JSON files
echo  * Prevent merge conflicts
echo  * Prevent very large files
echo.
echo Happy Coding!
echo ==========================================

pause
