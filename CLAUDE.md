# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web scraper for ss.com (Latvian real estate classifieds) that collects apartment listing data from Riga, stores it in SQLite, and performs statistical analysis. The project consists of a Python scraping module and a Jupyter notebook for data analysis.

**Technology Stack:** Python 3.8+, BeautifulSoup4, pandas, requests, SQLite3, scikit-learn, matplotlib/seaborn/plotly (for analysis)

## Running the Scraper

No build system or CLI exists. The scraper is used as a Python module:

```python
import ssWebScraper as sws

# 1. Gather district subcategories
districts = sws.gatherSubCats(initialLink='https://www.ss.com/en/real-estate/flats/riga/')

# 2. Scrape properties (100 pages per district)
ipasumi = sws.readPostList(districts, page_n=100, verbose=True)

# 3. Save to database (with deduplication)
newIpasumi = sws.saveToDB(ipasumi, tableName='PropertiesRAW',
                         uniqCols=['District','Street Name','Street No.',
                                   'Rooms', 'Size','Floor', 'Max. Floor', 'Project'])

# 4. Load from database
db = sws.loadFromDB(tableName='PropertiesRAW', dbName='miniSS.db')
```

**Run analysis notebook:**
```bash
jupyter notebook "ss.com Dzīvokļu datu nolasīšana.ipynb"
```

## Architecture

**ETL Pipeline Pattern:**

1. **Extraction** (`gatherSubCats`, `GetProperties`):
   - Scrapes HTML from ss.com using requests/BeautifulSoup
   - Iterates through both rental (`hand_over/`) and sale (`sell/`) pages
   - Handles pagination (up to `pages` parameter, default 10)

2. **Transformation** (`cleanPrices`, `cleanPostRowDetails`):
   - Normalizes price formats (/day, /week, /month → monthly equivalent)
   - **Key assumption**: Rental prices are converted to "equivalent sale price" by multiplying by 120 months
   - Extracts structured fields from HTML table rows
   - Filters invalid entries (rooms=0, price=0)

3. **Storage** (`saveToDB`, `loadFromDB`):
   - SQLite database (`miniSS.db`) with deduplication based on `uniqCols`
   - Merges new data with existing data, sorting by Post Date
   - CSV exports available for portability

4. **Analysis** (Jupyter notebook):
   - PCA, Linear Regression, OLS regression
   - Price analysis by district and building type
   - Rental vs sale comparisons

## Core Functions (ssWebScraper.py)

- **`gatherSubCats(initialLink)`** (lines 148-159): Returns dict of district names → URLs
- **`GetProperties(path, district, pages, result)`** (lines 104-143): Main scraper, returns list of property records
- **`readPostList(subCats, categories, page_n, verbose)`** (lines 164-196): Orchestrates scraping, returns pandas DataFrame
- **`saveToDB(newData, tableName, uniqCols, dbName)`** (lines 201-229): Saves to SQLite with deduplication
- **`loadFromDB(tableName, dbName, uniqCols)`** (lines 231-242): Loads from SQLite with type conversion
- **`getPostDate(link)`** (lines 13-21): Fetches individual listing page to extract post date
- **`cleanPrices(priceStr)`** (lines 26-44): Normalizes price strings to float, handles /day, /week, /month

## Database Schema

**Table: PropertiesRAW** (17 columns)

Unique constraint on: `['District','Street Name','Street No.', 'Rooms', 'Size','Floor', 'Max. Floor', 'Project']`

Key columns:
- `ID`: Composite identifier (row_id + address + details)
- `Deal Type`: RENT or SELL
- `District`: Riga district name
- `Street Name`, `Street No.`: Parsed address
- `Rooms`: 1-6 (0 filtered out)
- `Size`: Square meters
- `Floor`, `Max. Floor`: Floor info (format: "3/5")
- `Project`: Building type (New, Chrusch., Perewar, etc.)
- `Post Date`: When listing was posted
- `Price of sqm`, `Total Price`: Original prices
- `Alt. Price of sqm`, `Alt. Price`: For rentals, multiplied by 120 to create "equivalent sale price"

## Important Notes

### Code Quality Issues

1. **Deprecated pandas methods**: Uses `.append()` (deprecated in pandas 2.0). Should use `pd.concat()` instead
   - Affected: lines 182, 219 in ssWebScraper.py

2. **No rate limiting**: Requests have no delays, may trigger anti-scraping measures

3. **Minimal error handling**: Try/except blocks are sparse, failures may be silent

4. **Hardcoded values**:
   - Database name: `'miniSS.db'`
   - Table name: `'PropertiesRAW'`
   - Base URL: `'https://www.ss.com/en/real-estate/flats/riga/'`

### Missing Infrastructure

- **No requirements.txt**: Dependencies not documented
- **No tests**: No unit or integration tests
- **No linting/formatting**: No black, flake8, mypy, etc.
- **No .gitignore**: Should exclude `*.db`, `*.csv`, `__pycache__/`, `*.pyc`
- **No logging**: Uses print statements instead

### Data Assumptions

- Fair rental price = sale price ÷ 120 months (line 58)
- ss.com prices represent fair market prices
- Properties with rooms=0 or price=0 are invalid and filtered out
