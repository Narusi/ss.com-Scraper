# CLAUDE.md - AI Assistant Guide for ss.com-Scraper

## Project Overview

**Purpose**: Web scraper for ss.com (Latvian classifieds website) that extracts real estate listings (apartments/flats) in Riga, Latvia, and performs statistical analysis on pricing and market trends.

**Technology Stack**:
- Python 3
- Web scraping: `requests`, `BeautifulSoup4`
- Data processing: `pandas`, `numpy`
- Database: SQLite3
- Visualization: `matplotlib`, `plotly`, `seaborn`
- Machine Learning: `scikit-learn`, `statsmodels`

**Language Context**: The codebase contains mixed languages:
- Code: English (function names, variables)
- Comments: Mix of English and Latvian/Russian
- Data: Latvian (street names, districts)

---

## Repository Structure

```
ss.com-Scraper/
├── ssWebScraper.py              # Main scraper module (252 lines)
├── ss.com Dzīvokļu datu nolasīšana.ipynb  # Jupyter analysis notebook
├── miniSS.db                     # SQLite database with scraped data
├── data.csv                      # Exported data (~795KB)
├── ssDzivokli.csv               # Apartment-specific data (~1.5MB)
└── __pycache__/                 # Python cache directory
```

---

## Core Module: ssWebScraper.py

### Main Functions

#### 1. **Data Extraction**

**`getPostDate(link)`** (lines 13-21)
- Fetches individual listing post date from detail page
- **Input**: Full URL to listing
- **Output**: Date string
- **Pattern**: Uses BeautifulSoup to parse 'msg_footer' table cells

**`GetProperties(path, district='Unknown', pages=10, result='prices')`** (lines 104-143)
- Core scraping function that extracts property listings
- **Input**:
  - `path`: Base URL for category
  - `district`: District name for tagging
  - `pages`: Number of pages to scrape (default: 10)
- **Output**: List of property records
- **Deal Types**: Handles both 'RENT' (hand_over/) and 'SELL' (sell/) listings
- **Pagination**: Handles page1.html, page2.html, etc.

**`gatherSubCats(initialLink)`** (lines 148-159)
- Discovers all district subcategories from main page
- **Input**: Base category URL
- **Output**: Dictionary mapping district names to URLs
- **Pattern**: Finds all links with class 'a_category'

#### 2. **Data Processing**

**`cleanPrices(priceStr)`** (lines 26-44)
- Normalizes price strings to floats
- **Handles**:
  - Daily rates → monthly (×30)
  - Weekly rates → monthly (×4)
  - Removes commas, spaces
  - Handles special cases ('buy', '-', etc.)
- **Returns**: Float price value

**`cleanPostRowDetails(district, tradeType, rr, links, temp, postTable, postID)`** (lines 46-102)
- Parses and validates individual listing rows
- **Validation Rules**:
  - Must have rooms > 0 and price > 0
  - Filters out invalid entries
- **Data Enrichment**:
  - Calculates alternative price (rent → sale estimate using 120-month multiplier)
  - Generates unique ID from composite fields
  - Parses street name/number from combined field

**`readPostList(subCats, categories=[], page_n=100, verbose=False)`** (lines 164-196)
- Orchestrates scraping across multiple districts
- **Process**:
  1. Iterate through districts
  2. Call GetProperties for each
  3. Combine into DataFrame
  4. Clean and validate data
  5. Convert types (numeric, datetime)
- **Returns**: Cleaned pandas DataFrame

#### 3. **Database Operations**

**`saveToDB(newData, tableName, uniqCols, dbName='miniSS.db', cols=[])`** (lines 201-229)
- Upserts data to SQLite database
- **Deduplication**: Uses `uniqCols` to prevent duplicates
- **Merge Strategy**: Appends new data, removes duplicates, keeps latest by Post Date
- **Error Handling**: Creates table if doesn't exist

**`loadFromDB(tableName, dbName='miniSS.db', uniqCols=uniqCols)`** (lines 231-242)
- Loads data from database
- **Auto-converts**: Date columns (any column with 'date' in name)
- **Cleans**: Removes duplicate rows based on unique columns

---

## Data Schema

### DataFrame Columns (17 total)

| Column | Type | Description |
|--------|------|-------------|
| `ID` | object | Composite unique identifier |
| `Deal Type` | object | 'RENT' or 'SELL' |
| `Comment` | object | Listing description text |
| `Link` | object | Full URL to listing |
| `District` | object | Riga district name |
| `Street Name` | object | Parsed street name |
| `Street No.` | object | Building number |
| `Rooms` | int64 | Number of rooms (filtered: 1-10) |
| `Size` | int64 | Square meters (filtered: ≤1000) |
| `Floor` | int64 | Apartment floor |
| `Max. Floor` | int64 | Building total floors |
| `Project` | object | Building type (see Building Types) |
| `Post Date` | datetime64[ns] | When listing was posted |
| `Price of sqm` | float64 | Price per square meter |
| `Alt. Price of sqm` | float64 | Adjusted price (rent×120 for sales comparison) |
| `Total Price` | float64 | Total listing price |
| `Alt. Price` | float64 | Adjusted total price |

### Building Types (Project Types)

Common values in the `Project` column:
- `New` - New construction
- `Spec. pr.` - Special project
- `Chrusch.` - Khrushchyovka (Soviet-era)
- `Stalin pr.` - Stalinist architecture
- `Perewar` - Pre-war
- `Lit pr.` - Lithuanian project
- `Private` - Private house
- `Czech pr.` - Czech project
- `602-th`, `467-th`, `119-th`, `103-th`, `104-th` - Numbered series
- `Recon.` - Reconstructed
- `Small` - Small building

### Unique Columns for Deduplication

```python
uniqCols = ['District', 'Street Name', 'Street No.', 'Rooms',
            'Size', 'Floor', 'Max. Floor', 'Project']
```

---

## Typical Usage Workflow

### Example: Scrape Riga Apartments

```python
import ssWebScraper as sws

# 1. Discover districts
districts = sws.gatherSubCats(
    initialLink='https://www.ss.com/en/real-estate/flats/riga/'
)

# 2. Scrape listings (100 pages per district)
ipasumi = sws.readPostList(districts, page_n=100, verbose=True)

# 3. Save to database
ipasumi = sws.saveToDB(
    ipasumi,
    tableName='PropertiesRAW',
    uniqCols=['District', 'Street Name', 'Street No.',
              'Rooms', 'Size', 'Floor', 'Max. Floor', 'Project']
)

# 4. Load from database for analysis
db = sws.loadFromDB(tableName='PropertiesRAW', dbName='miniSS.db')
```

---

## Jupyter Notebook Analysis

The notebook `ss.com Dzīvokļu datu nolasīšana.ipynb` performs:

1. **Data Loading** - Uses ssWebScraper module
2. **Data Cleaning**:
   - Outlier detection (>10 standard deviations)
   - Size validation (≤1000 sqm)
   - Floor validation (Floor ≤ Max Floor)
   - Price normalization
3. **Feature Engineering**:
   - `AVG_Price_SQM` - Average price for similar properties
   - `Relative_Floor` - Floor position ratio
4. **Visualizations**:
   - Scatter matrices
   - District/project price comparisons
   - Box plots by building type
5. **Statistical Modeling**:
   - PCA (Principal Component Analysis)
   - Linear Regression
   - OLS (Ordinary Least Squares)

---

## Development Conventions

### Code Style

1. **Function Naming**: camelCase (e.g., `getPostDate`, `cleanPrices`)
2. **Variable Naming**: camelCase for locals, snake_case for some
3. **Constants**: Defined at module level (e.g., `uniqCols`)

### Error Handling

- **Try-finally blocks** used in scraping to ensure cleanup
- **Silent failures** for individual listings (continues scraping)
- **Type validation** before processing (e.g., checking rooms > 0)

### Data Validation Rules

```python
# Applied in cleanPostRowDetails():
if rooms > 0 and price > 0.0:  # Only process valid listings
    # Additional parsing...

# Applied in readPostList():
dataDF = dataDF[np.logical_and(
    dataDF['Total Price'] > 0,
    dataDF['Rooms'] != 'Other'
)]
```

---

## AI Assistant Guidelines

### When Extending the Scraper

1. **Preserve data validation logic** - Don't bypass rooms/price checks
2. **Maintain deduplication strategy** - Use composite keys
3. **Keep 120-month rent multiplier** - It's a deliberate assumption (line 55-62)
4. **Handle encoding carefully** - Data contains UTF-8 Latvian/Russian text

### When Modifying Data Processing

1. **Check data types** - The code expects specific types after cleaning
2. **Test with existing database** - Ensure backwards compatibility
3. **Preserve unique ID generation** - Used for deduplication (line 93)
4. **Maintain column order** - Some operations depend on column positions

### When Adding Features

1. **Add new columns to DataFrame** - Append, don't replace
2. **Update `saveToDB` column mappings** if needed
3. **Consider updating `uniqCols`** if adding identifying fields
4. **Document units** - Prices are in EUR, size in m²

### Common Pitfalls to Avoid

1. **Don't hardcode prices/dates** - Data is time-sensitive
2. **Don't assume complete data** - Handle missing fields gracefully
3. **Don't break pagination** - URL pattern is critical (pageN.html)
4. **Encoding issues** - Use `.encode("ascii", "ignore")` pattern (line 32)

### Testing Approach

```python
# Test scraping on limited pages first
test_data = sws.readPostList(districts, page_n=2, verbose=True)

# Verify data structure
print(test_data.info())
print(test_data.describe())

# Check for expected districts
print(test_data['District'].unique())
```

---

## URL Structure Reference

### Base URL Patterns

```
Main category: https://www.ss.com/en/real-estate/flats/riga/
Districts: https://www.ss.com/en/real-estate/flats/riga/{district}/

Rent listings (hand_over):
  Page 1: {district_url}hand_over/
  Page N: {district_url}hand_over/pageN.html

Sale listings (sell):
  Page 1: {district_url}sell/
  Page N: {district_url}sell/pageN.html

Individual listing:
  https://www.ss.com/msg/en/real-estate/flats/riga/{district}/{id}.html
```

---

## Database Management

### Table Schema

```sql
-- PropertiesRAW table (inferred from code)
CREATE TABLE PropertiesRAW (
    index INTEGER,
    ID TEXT,
    "Deal Type" TEXT,
    Comment TEXT,
    Link TEXT,
    District TEXT,
    "Street Name" TEXT,
    "Street No." TEXT,
    Rooms INTEGER,
    Size INTEGER,
    Floor INTEGER,
    "Max. Floor" INTEGER,
    Project TEXT,
    "Post Date" TEXT,  -- Stored as text, converted to datetime on load
    "Price of sqm" REAL,
    "Alt. Price of sqm" REAL,
    "Total Price" REAL,
    "Alt. Price" REAL
);
```

### Maintenance Operations

```python
# Reload all data
db = sws.loadFromDB('PropertiesRAW')

# Re-scrape and merge
new_data = sws.readPostList(districts, page_n=100)
merged = sws.saveToDB(new_data, 'PropertiesRAW', uniqCols)
```

---

## Known Issues & Limitations

1. **No rate limiting** - May need delays between requests for large scrapes
2. **Page parsing failures** - Silent failures may miss some listings
3. **Encoding assumptions** - `.encode("ascii", "ignore")` loses non-ASCII chars
4. **Hardcoded assumptions**:
   - 120-month multiplier for rent-to-sale conversion
   - Max 1000 sqm size filter
   - Floor validation assumes Floor ≤ Max Floor
5. **No resume capability** - Scraping interruption requires restart
6. **Database append-only** - No UPDATE mechanism, only INSERT after dedup

## Compatibility Notes

### Pandas 2.x Compatibility

The code has been updated for pandas 2.x compatibility:
- Replaced deprecated `DataFrame.append()` with `pd.concat()`
- Lines 186, 220: Now using `pd.concat([df1, df2], ignore_index=True)`

**Tested with**:
- Python 3.11
- pandas 2.3.3
- numpy 2.3.5
- beautifulsoup4 4.14.3

---

## Future Enhancement Ideas

1. **Add rate limiting/politeness delays**
2. **Implement checkpoint/resume for long scrapes**
3. **Add logging instead of silent failures**
4. **Export configuration** - Externalize URLs, page limits
5. **Add data validation schema**
6. **Implement incremental updates** (only fetch new listings)
7. **Add error metrics/monitoring**
8. **Support other cities** beyond Riga
9. **Add image scraping** capability
10. **Create REST API** for data access

---

## Quick Reference Commands

```python
# Import module
import ssWebScraper as sws

# Full scrape workflow
districts = sws.gatherSubCats('https://www.ss.com/en/real-estate/flats/riga/')
data = sws.readPostList(districts, page_n=100, verbose=True)
data = sws.saveToDB(data, 'PropertiesRAW', sws.uniqCols)

# Load existing data
db = sws.loadFromDB('PropertiesRAW')

# Quick analysis
print(db.info())
print(db.describe())
print(db['District'].value_counts())
print(db['Project'].value_counts())
```

---

## Contact & Contribution

- **Git Branch**: Work on feature branches, commit descriptive messages
- **Data Privacy**: Be mindful that scraped data is public but respect robots.txt
- **Code Comments**: Add inline docs for complex logic, especially in Latvian/Russian sections

---

**Last Updated**: 2025-12-09
**Repository**: ss.com-Scraper
**Maintainer**: (See git log for contributors)
