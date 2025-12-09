"""
Module file for web-scraping www.ss.com

This module provides a simple interface to the ss_re_scraper package.
All functionality has been moved to the ss_re_scraper package.
"""

# Import all functions from the ss_re_scraper package
from ss_re_scraper import (
    getPostDate,
    cleanPrices,
    cleanPostRowDetails,
    GetProperties,
    gatherSubCats,
    readPostList,
    saveToDB,
    loadFromDB,
    uniqCols
)

# For backwards compatibility, export all functions
__all__ = [
    'getPostDate',
    'cleanPrices',
    'cleanPostRowDetails',
    'GetProperties',
    'gatherSubCats',
    'readPostList',
    'saveToDB',
    'loadFromDB',
    'uniqCols'
]

# Example usage (commented out):
# districts = gatherSubCats(initialLink='https://www.ss.com/en/real-estate/flats/riga/')
# ipasumi = readPostList(districts, page_n=100, verbose=True)
# newIpasumi = saveToDB(ipasumi, tableName='PropertiesRAW',
#                       uniqCols = ['District','Street Name','Street No.',
#                                   'Rooms', 'Size','Floor', 'Max. Floor', 'Project'])
# print(newIpasumi.info())

# db = loadFromDB(tableName='PropertiesRAW', dbName = 'miniSS.db')
# print(db.info())
