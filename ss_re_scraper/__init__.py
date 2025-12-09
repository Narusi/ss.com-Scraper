"""
SS.com Real Estate Scraper Package

A Python package for scraping real estate data from www.ss.com
"""

from .scraper import (
    getPostDate,
    cleanPrices,
    cleanPostRowDetails,
    GetProperties,
    gatherSubCats,
    readPostList,
    saveToDB,
    loadFromDB,
    cleanData,
    updateDB,
    getCostComparison,
    getCostTrends,
    getTopAffordable,
    getTopAffordableByDistrictAndProject,
    uniqCols
)

__version__ = '0.2.0'
__author__ = 'Nauris'
__all__ = [
    'getPostDate',
    'cleanPrices',
    'cleanPostRowDetails',
    'GetProperties',
    'gatherSubCats',
    'readPostList',
    'saveToDB',
    'loadFromDB',
    'cleanData',
    'updateDB',
    'getCostComparison',
    'getCostTrends',
    'getTopAffordable',
    'getTopAffordableByDistrictAndProject',
    'uniqCols'
]
