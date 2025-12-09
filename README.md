# SS.com Real Estate Scraper

A Python package for scraping real estate data from www.ss.com (Latvian classified ads website).

## Installation

### From GitHub

```bash
pip install git+https://github.com/Narusi/ss.com-Scraper.git
```

### Local Installation

```bash
git clone https://github.com/Narusi/ss.com-Scraper.git
cd ss.com-Scraper
pip install -e .
```

## Usage

```python
import ss_re_scraper as sws

# Gather district categories
districts = sws.gatherSubCats(initialLink='https://www.ss.com/en/real-estate/flats/riga/')

# Read property listings
ipasumi = sws.readPostList(districts, page_n=100, verbose=True)

# Save to database
ipasumi = sws.saveToDB(ipasumi, tableName='PropertiesRAW',
                       uniqCols=sws.uniqCols)

# Load from database
data = sws.loadFromDB(tableName='PropertiesRAW', dbName='miniSS.db')
```

## Features

- Scrape real estate listings from ss.com
- Support for both rent and sale listings
- Automatic price normalization
- SQLite database integration
- Duplicate detection and removal

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- pandas
- numpy

## License

MIT License
