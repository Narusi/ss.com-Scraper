# SS.com Real Estate Scraper

A Python package for scraping real estate data from www.ss.com (Latvian classified ads website). This package collects apartment listing data including prices, locations, and property characteristics, storing them in a SQLite database for analysis.

## Installation

### From GitHub (Recommended for Google Colab)

```bash
pip install git+https://github.com/Narusi/ss.com-Scraper.git
```

### Local Installation

```bash
git clone https://github.com/Narusi/ss.com-Scraper.git
cd ss.com-Scraper
pip install -e .
```

## Updating

To update to the latest version:

```bash
pip install --upgrade git+https://github.com/Narusi/ss.com-Scraper.git
```

For local installations:

```bash
cd ss.com-Scraper
git pull origin master
pip install -e . --upgrade
```

## Quick Start

### Simple One-Command Workflow (v0.2.0+)

```python
import ss_re_scraper as sws

# Scrape, clean, and save to database in one command
data = sws.updateDB(
    'https://www.ss.com/en/real-estate/flats/riga/',
    auto_clean=True,  # Automatically remove outliers
    page_n=100,
    verbose=True
)

# Generate comprehensive Markdown report
sws.generateReport(
    dbName='miniSS.db',
    deal_type='SELL',  # or 'RENT'
    output_file='market_report.md',
    top_n=10,
    verbose=True
)
```

### Manual Step-by-Step Workflow

```python
import ss_re_scraper as sws

# Step 1: Gather district categories
districts = sws.gatherSubCats(initialLink='https://www.ss.com/en/real-estate/flats/riga/')

# Step 2: Scrape property listings
ipasumi = sws.readPostList(districts, page_n=100, verbose=True)

# Step 3: Clean data (optional but recommended)
ipasumi_clean = sws.cleanData(ipasumi, remove_outliers=True, verbose=True)

# Step 4: Save to SQLite database
ipasumi = sws.saveToDB(ipasumi_clean, tableName='PropertiesRAW',
                       uniqCols=sws.uniqCols)

# Step 5: Load from database
data = sws.loadFromDB(tableName='PropertiesRAW', dbName='miniSS.db')
```

## Database Structure

### Table: `PropertiesRAW`

The scraped data is stored in a SQLite database with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `index` | INTEGER | Auto-increment index |
| `ID` | TEXT | Unique identifier (combination of post ID and property details) |
| `Deal Type` | TEXT | Type of transaction: `RENT` or `SELL` |
| `Comment` | TEXT | Property description from the listing |
| `Link` | TEXT | URL to the original listing on ss.com |
| `District` | TEXT | District/neighborhood name in Riga |
| `Street Name` | TEXT | Street name |
| `Street No.` | TEXT | Street number/building identifier |
| `Rooms` | INTEGER | Number of rooms (1-6+) |
| `Size` | INTEGER | Property size in square meters (m²) |
| `Floor` | INTEGER | Floor number |
| `Max. Floor` | INTEGER | Total floors in the building |
| `Project` | TEXT | Building project type (e.g., "New", "Stalin pr.", "Chrusch.", "Private") |
| `Post Date` | TEXT | Date when the listing was posted (YYYY-MM-DD HH:MM:SS) |
| `Price of sqm` | FLOAT | Price per square meter (monthly for rent, total for sale) |
| `Alt. Price of sqm` | FLOAT | Alternative price per sqm (rent * 120 months for RENT, same as price for SELL) |
| `Total Price` | FLOAT | Total listing price (monthly rent or purchase price) |
| `Alt. Price` | FLOAT | Alternative total price (rent * 120 months for RENT, same as total for SELL) |

### Price Fields Explanation

- **For RENT listings:**
  - `Price of sqm` and `Total Price` = Monthly rent values
  - `Alt. Price of sqm` and `Alt. Price` = Annualized value (monthly rent × 120 months)
  - The 120-month multiplier represents an assumed fair market value conversion

- **For SELL listings:**
  - All price fields contain the purchase price
  - `Alt. Price` fields are identical to regular price fields

### Building Project Types

Common values in the `Project` column:
- `New` - New construction
- `Stalin pr.` - Stalin-era buildings
- `Chrusch.` - Khrushchyovka (Soviet-era apartments)
- `Perewar` - Pre-war buildings
- `Private` - Private houses
- `Lit pr.` - Lithuanian project
- `Czech pr.` - Czech project
- `602-th`, `467-th`, `119-th`, `103-th`, `104-th` - Series numbers
- `Recon.` - Reconstructed buildings
- `Spec. pr.` - Special projects

## Data Query Examples

### Basic Queries

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('miniSS.db')

# Get all apartments for rent in Centre district
query = """
SELECT * FROM PropertiesRAW
WHERE "Deal Type" = 'RENT'
  AND District = 'Centre'
"""
df = pd.read_sql(query, conn)

# Get average price per sqm by district for new apartments
query = """
SELECT District,
       AVG("Price of sqm") as avg_price_sqm,
       COUNT(*) as count
FROM PropertiesRAW
WHERE Project = 'New' AND "Deal Type" = 'SELL'
GROUP BY District
ORDER BY avg_price_sqm DESC
"""
avg_prices = pd.read_sql(query, conn)
print(avg_prices)

conn.close()
```

### Advanced Queries

```python
# Find 2-room apartments under €500/month
query = """
SELECT District, "Street Name", Size, Floor, "Total Price", Link
FROM PropertiesRAW
WHERE "Deal Type" = 'RENT'
  AND Rooms = 2
  AND "Total Price" < 500
ORDER BY "Total Price" ASC
"""
affordable = pd.read_sql(query, conn)

# Calculate price per sqm statistics by building type
query = """
SELECT Project,
       COUNT(*) as listings,
       ROUND(AVG("Alt. Price of sqm"), 2) as avg_price_sqm,
       ROUND(MIN("Alt. Price of sqm"), 2) as min_price_sqm,
       ROUND(MAX("Alt. Price of sqm"), 2) as max_price_sqm,
       ROUND(AVG(Size), 1) as avg_size
FROM PropertiesRAW
WHERE "Deal Type" = 'SELL'
GROUP BY Project
HAVING COUNT(*) > 10
ORDER BY avg_price_sqm DESC
"""
project_stats = pd.read_sql(query, conn)

# Find properties with best price/value ratio
query = """
SELECT District, "Street Name", Rooms, Size,
       "Total Price", "Price of sqm",
       Floor || '/' || "Max. Floor" as floor_info,
       Project, Link
FROM PropertiesRAW
WHERE "Deal Type" = 'SELL'
  AND Rooms >= 2
  AND "Price of sqm" < 1000
ORDER BY "Price of sqm" ASC
LIMIT 20
"""
best_deals = pd.read_sql(query, conn)
```

## New Features in v0.2.0

### Analytics Functions

The package now includes built-in analytics functions that simplify data analysis:

#### Cost Comparison Between Districts

```python
import ss_re_scraper as sws

# Compare average costs across districts
comparison = sws.getCostComparison(dbName='miniSS.db', deal_type='SELL')
print(comparison)

# Returns: District, listings_count, avg_price_sqm, min/max prices, avg_size, avg_rooms
```

#### Cost Trends Over Time

```python
# Analyze price trends over the last 6 months
trends = sws.getCostTrends(dbName='miniSS.db', months=6)
print(trends)

# Returns: month, District, Deal Type, avg_price_sqm, total listings
```

#### Top Affordable Listings

```python
# Find top 10 most affordable apartments
top10 = sws.getTopAffordable(
    dbName='miniSS.db',
    deal_type='RENT',
    top_n=10
)

# Filter by district
top10_centre = sws.getTopAffordable(
    district='Centre',
    deal_type='RENT',
    top_n=10
)

# Filter by project type
top10_new = sws.getTopAffordable(
    project='New',
    deal_type='SELL',
    top_n=10
)
```

#### Database Status

```python
# Get comprehensive database statistics
status = sws.getDatabaseStatus(dbName='miniSS.db')

print(f"Total records: {status['total_records']:,}")
print(f"Date range: {status['date_range']}")
print(f"By deal type:")
print(status['by_deal_type'])
print(f"\nTop projects:")
print(status['by_project'])
```

### Report Generation

Generate comprehensive Markdown reports with a single command:

```python
# Generate full market report for SELL transactions
report_file = sws.generateReport(
    dbName='miniSS.db',
    tableName='PropertiesRAW',
    output_file='sell_report.md',
    deal_type='SELL',
    top_n=10,
    verbose=True
)

# Generate report for RENT transactions
rent_report = sws.generateReport(
    deal_type='RENT',
    output_file='rent_report.md',
    top_n=20
)
```

**Report Contents:**
- 📊 **Database Status**: Total records, date coverage, breakdowns by deal type/project/district
- 💰 **Cost Comparison**: Average prices across all districts with key insights
- 📈 **Cost Trends**: Monthly price trends over the last 6 months
- 🏆 **Top Affordable Listings**: Best deals with clickable links to original listings
- 📝 **Notes**: Metadata and data source information

The generated Markdown reports are:
- ✅ Viewable in GitHub, VS Code, and any browser
- ✅ Easy to convert to PDF/HTML if needed
- ✅ Version control friendly
- ✅ Professional formatting with tables and insights

### Data Cleaning

Automatic data cleaning with outlier removal:

```python
# Clean data with default settings
clean_df = sws.cleanData(raw_df, remove_outliers=True, verbose=True)

# Cleaning removes:
# - Properties with size > 1000 m²
# - Floor > Max Floor inconsistencies
# - Unrealistic room counts (> 10)
# - Price anomalies
# - NaN values
```

## Use Cases

### Use Case 1: Market Research Report

```python
import ss_re_scraper as sws

# Update database with latest listings
sws.updateDB(
    'https://www.ss.com/en/real-estate/flats/riga/',
    auto_clean=True,
    page_n=100,
    verbose=True
)

# Generate comprehensive report
sws.generateReport(
    deal_type='SELL',
    output_file='market_analysis_2025.md',
    top_n=20
)
```

### Use Case 2: Find Best Rental Deals

```python
import ss_re_scraper as sws

# Get top affordable rentals in Centre
centre_deals = sws.getTopAffordable(
    district='Centre',
    deal_type='RENT',
    top_n=10
)

# Get top new construction rentals
new_rentals = sws.getTopAffordable(
    project='New',
    deal_type='RENT',
    top_n=15
)

print("Best deals in Centre:")
print(centre_deals[['District', 'Rooms', 'Size', 'Total Price', 'Link']])
```

### Use Case 3: Investment Analysis

```python
import ss_re_scraper as sws

# Compare costs across districts
comparison = sws.getCostComparison(deal_type='SELL')

# Find districts with best price/size ratio
comparison['price_per_room'] = comparison['avg_total_price'] / comparison['avg_rooms']
best_value = comparison.nsmallest(5, 'price_per_room')

print("Best value districts for investment:")
print(best_value[['District', 'avg_price_sqm', 'avg_total_price', 'price_per_room']])
```

### Use Case 4: Automated Daily Updates

```python
import ss_re_scraper as sws
from datetime import datetime

# Daily update script
def daily_update():
    # Scrape and update database
    data = sws.updateDB(
        'https://www.ss.com/en/real-estate/flats/riga/',
        auto_clean=True,
        page_n=50,
        verbose=True
    )

    # Generate daily report
    today = datetime.now().strftime('%Y-%m-%d')
    sws.generateReport(
        deal_type='RENT',
        output_file=f'reports/rent_report_{today}.md',
        top_n=10
    )

    # Check for new affordable listings
    new_deals = sws.getTopAffordable(deal_type='RENT', top_n=5)
    return new_deals

# Run daily
daily_update()
```

## Example Data Analysis Workflow

### 1. Data Collection and Cleaning

```python
import ss_re_scraper as sws
import pandas as pd
import numpy as np

# Scrape data
districts = sws.gatherSubCats('https://www.ss.com/en/real-estate/flats/riga/')
ipasumi = sws.readPostList(districts, page_n=100, verbose=True)

# Save to database
ipasumi = sws.saveToDB(ipasumi, tableName='PropertiesRAW',
                       uniqCols=sws.uniqCols)

# Load and clean data
cleanDF = ipasumi.copy()

# Remove outliers
cleanDF = cleanDF.loc[cleanDF['Size'] <= 1000]
cleanDF = cleanDF.loc[cleanDF['Floor'] <= cleanDF['Max. Floor']]

# Handle price anomalies
altPrInex = cleanDF['Alt. Price of sqm'] >= cleanDF['Price of sqm'].max()
cleanDF.loc[altPrInex, 'Alt. Price of sqm'] = cleanDF.loc[altPrInex, 'Price of sqm']

# Convert dates
cleanDF['Post Date'] = pd.to_datetime(cleanDF['Post Date'])
```

### 2. Calculate Derived Features

```python
# Add relative floor position (0 = ground floor, 1 = top floor)
cleanDF['Relative_Floor'] = (cleanDF['Floor'] - 1) / cleanDF['Max. Floor']
cleanDF.loc[cleanDF['Max. Floor'] == 1, 'Relative_Floor'] = 1.0

# Calculate average price per sqm for similar properties
cleanDF['AVG_Price_SQM'] = 0.0

for r in cleanDF.index:
    # Find similar properties (same district, project, deal type)
    similar = cleanDF.loc[
        (cleanDF['District'] == cleanDF.loc[r, 'District']) &
        (cleanDF['Project'] == cleanDF.loc[r, 'Project']) &
        (cleanDF['Deal Type'] == cleanDF.loc[r, 'Deal Type'])
    ]

    # Calculate average excluding current property
    cleanDF.loc[r, 'AVG_Price_SQM'] = similar.drop(r, axis=0)['Alt. Price of sqm'].mean()
```

### 3. Exploratory Data Analysis

```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Distribution of prices by district
fig = px.box(cleanDF, x='District', y='Alt. Price of sqm',
             color='Deal Type', title='Price Distribution by District')
fig.show()

# Average price by building project type
project_avg = cleanDF.groupby('Project')['Alt. Price of sqm'].mean().sort_values()
fig = px.bar(project_avg, title='Average Price per sqm by Building Type')
fig.show()

# Correlation analysis
numeric_cols = ['Rooms', 'Size', 'Floor', 'Max. Floor',
                'Price of sqm', 'Alt. Price of sqm', 'Relative_Floor']
corr_matrix = cleanDF[numeric_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Feature Correlation Matrix')
plt.show()
```

### 4. Statistical Modeling

```python
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
import statsmodels.api as sm

# Prepare data for modeling
features = ['Rooms', 'Size', 'Floor', 'Max. Floor']
X = cleanDF[cleanDF['Deal Type'] == 'SELL'][features]
y = cleanDF[cleanDF['Deal Type'] == 'SELL']['Price of sqm']

# Standardize features
X_scaled = preprocessing.scale(X)

# Linear regression
model = sm.OLS(y, X_scaled)
results = model.fit()
print(results.summary())

# Feature importance
reg = LinearRegression().fit(X_scaled, y)
coefficients = pd.Series(reg.coef_, index=features)
print("\nFeature Coefficients:")
print(coefficients.sort_values(ascending=False))
```

### 5. Market Insights

```python
# Compare rent vs buy decisions (120-month assumption)
rent_data = cleanDF[cleanDF['Deal Type'] == 'RENT'].groupby('District').agg({
    'Alt. Price': 'mean',  # Rent * 120
    'Size': 'mean'
})

sell_data = cleanDF[cleanDF['Deal Type'] == 'SELL'].groupby('District').agg({
    'Total Price': 'mean',
    'Size': 'mean'
})

comparison = pd.DataFrame({
    'Rent_120mo': rent_data['Alt. Price'],
    'Buy_Price': sell_data['Total Price'],
    'Difference': sell_data['Total Price'] - rent_data['Alt. Price']
})
comparison['Rent_Better'] = comparison['Difference'] > 0
print(comparison.sort_values('Difference'))
```

## Known Limitations

### Data Quality Issues

1. **Missing Data**
   - Some listings may have incomplete information (e.g., missing floor numbers)
   - Street numbers are not always standardized
   - Post dates may not reflect actual listing availability

2. **Price Inconsistencies**
   - Daily and weekly rental prices are converted to monthly (×30 and ×4 respectively)
   - The 120-month multiplier for rent-to-buy comparison is an assumption, not market data
   - Currency fluctuations are not accounted for
   - Prices may include or exclude utilities inconsistently

3. **Duplicate Detection**
   - Duplicates are identified by: District, Street Name, Street No., Rooms, Size, Floor, Max. Floor, Project
   - Legitimate different apartments with identical characteristics may be incorrectly marked as duplicates
   - Relisted properties with price changes may be missed

### Scraping Limitations

1. **Rate Limiting**
   - No built-in rate limiting; excessive requests may get blocked
   - Each page scrape requires a separate HTTP request
   - Scraping large datasets (100+ pages × 45 districts) can take significant time

2. **Dynamic Content**
   - Only scrapes visible listing tables, not JavaScript-loaded content
   - Detailed property features (renovation, amenities) are in comments, requiring NLP to extract

3. **Language Issues**
   - Mixed Latvian/English content in comments
   - District names may vary between Latvian and English
   - Building project names are not standardized

### Analysis Limitations

1. **Market Assumptions**
   - 120-month rent multiplier is arbitrary
   - Does not account for:
     - Property appreciation/depreciation
     - Maintenance costs
     - Property taxes
     - Opportunity cost of capital

2. **Temporal Factors**
   - No historical price tracking for same property
   - Seasonal market variations not captured
   - Economic events (COVID-19, etc.) may skew data

3. **Selection Bias**
   - Only includes actively listed properties
   - Expensive properties may have shorter listing times (underrepresented)
   - Distressed sales not distinguished from regular listings

4. **Geographic Limitations**
   - Currently only supports Riga apartments
   - No geocoding (exact coordinates) available
   - District boundaries may overlap or be imprecise

### Technical Limitations

1. **Database**
   - SQLite has limited concurrent write support
   - No built-in backup/versioning
   - Schema changes require manual migration

2. **Dependencies**
   - Requires BeautifulSoup4 (HTML structure changes will break scraper)
   - pandas `.append()` is deprecated in newer versions
   - No async/parallel scraping support

3. **Error Handling**
   - Network errors may cause incomplete data collection
   - Malformed HTML may crash the scraper
   - No retry logic for failed requests

## Future Improvements

- [ ] Add geocoding for exact property locations
- [ ] Implement rate limiting and retry logic
- [ ] Support for other cities and property types
- [ ] Historical price tracking
- [ ] Automated data quality checks
- [ ] Export to CSV/Excel functionality
- [ ] REST API for data access
- [ ] Real-time alerts for new listings

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- pandas
- numpy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
