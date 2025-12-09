"""
SS.com Web Scraping Module

This module provides functionality for scraping real estate data from www.ss.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# Unique columns for identifying duplicate entries
uniqCols = ['District','Street Name','Street No.', 'Rooms', 'Size','Floor', 'Max. Floor', 'Project']

##=============================================================##
##=====================  GET POSTS DATE =======================##
##=============================================================##
def getPostDate(link):
    """
    Get the post date from a property listing page.

    Args:
        link (str): URL of the property listing

    Returns:
        str: Post date string
    """
    r = requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')

    date = ''
    for x in soup.find_all('td',"msg_footer",):
        if x.text.find('Date') >= 0:
            date = (x.text[6:])
    return date

##=============================================================##
##=================  READ POSTLINE DETAILS  ===================##
##=============================================================##
def cleanPrices(priceStr):
    """
    Clean and normalize price strings to float values.

    Args:
        priceStr (str): Price string from listing

    Returns:
        float: Normalized price value
    """
    priceStr = str(priceStr)

    if len(priceStr)<2 and priceStr == '-':
        price = 0.00
    elif priceStr.find('/') < 0 and priceStr != 'buy ':
        price = float(priceStr.replace(',','').encode("ascii", "ignore"))
    else:
        if priceStr.find('/day') < 0 and priceStr.find('/week') < 0 and priceStr != 'buy ':
            price = float(priceStr.replace('/mon.', '').replace(',','').replace(' ','').encode("ascii", "ignore"))
        elif priceStr.find('/day') < 0 and priceStr.find('/week') > 0 and priceStr!='buy ':
            price = float(priceStr.replace('/week', '').replace(',','').replace(' ','').encode("ascii", "ignore"))
            price = price  * 4
        elif priceStr.find('/day')>0 and priceStr.find('/week') < 0 and priceStr!='buy ':
            price = float(priceStr.replace('/day', '').replace(',','').replace(' ','').encode("ascii", "ignore"))
            price = price  * 30
        else:
            price = 0.00
    return price

def cleanPostRowDetails(district, tradeType, rr, links, temp, postTable, postID):
    """
    Extract and clean details from a post row.

    Args:
        district (str): District name
        tradeType (str): Type of trade (RENT/SELL)
        rr: BeautifulSoup row element
        links (dict): Dictionary to store links
        temp (list): Temporary data list
        postTable (list): Table to append post data
        postID (list): List of post IDs

    Returns:
        tuple: Updated postTable and postID
    """

    if str(temp[8]) == '-':
        sqmPrice = 0.00
    else:
        sqmPrice = cleanPrices(temp[8])

    price = cleanPrices(temp[9])

    #   WE MAKE AN ASSUMPTION THAT FAIR RENT IS EQUAL TO PROPERTY PRICE DEVIDED BY 120 MONTHS
    #   AND WE ALSO ASSUME THAT SS.COM PRICES REPRESENT FAIR MARKET PRICES
    if tradeType == 'RENT':
        altPrice = float(price) * 120
        altSQMprice = float(sqmPrice) * 120
    else:
        altPrice = price
        altSQMprice = sqmPrice

    for x in rr.find_all('a'):
        links[rr.get('id')] = 'https://www.ss.com/' + str(x.get('href'))

    try:
        if len(str(temp[4])) > 2 or len(str(temp[4])) == 0:
            rooms = 0
        elif len(str(temp[4])) > 0:
            rooms = int(temp[4])
    except:
        rooms = 0

    if rooms > 0 and price > 0.0:
        size = temp[5]
        floor = str(temp[6]).split('/')[0]
        maxFloor = str(temp[6]).split('/')[-1]
        project = str(temp[7])

        if len(temp[3].split(' ')[0]) > 3:
            streetName = temp[3].split(' ')[0]
            streetNo = temp[3].split(' ')[-1]
        elif len(temp[3].split(' ')) > 2:
            streetName =  str(temp[3].split(' ')[0]) + str(temp[3].split(' ')[1])
            streetNo = temp[3].split(' ')[-1]
        else:
            streetName =  str(temp[3])
            streetNo = ''

        postDate = getPostDate(links[rr.get('id')])
        comment = str(temp[2])
        pID = str(str(rr.get('id')) + temp[3] + temp[4] + temp[5] + temp[6] + temp[7])

        postTable.append([pID, tradeType, comment, links[rr.get('id')], \
                        district, streetName, streetNo, rooms, size, \
                        floor, maxFloor, project, postDate, \
                        sqmPrice, altSQMprice, price, altPrice])

        postID.append(pID)

    return postTable, postID

def GetProperties(path, district='Unknown', pages=10, result='prices'):
    """
    Get property listings from ss.com for a specific district.

    Args:
        path (str): Base URL path for the district
        district (str): District name
        pages (int): Number of pages to scrape
        result (str): Type of result (default: 'prices')

    Returns:
        list: List of property listings
    """

    postTable = []
    deals = ['hand_over/', 'sell/']
    postID = []
    links = {}

    try:
        for dd in deals:
            if dd == deals[1]:
                tradeType = 'SELL'
            elif dd == deals[0]:
                tradeType = 'RENT'
            else:
                tradeType = 'BUY'

            for n in range(1, pages):

                if n == 1:
                    fullPath = path + dd
                else:
                    fullPath = path + dd + 'page' + str(n) + '.html'

                r = requests.get(fullPath)
                soup = BeautifulSoup(r.text, 'html.parser')

                raw = soup.find_all('tr')
                for rr in raw:
                    temp = []

                    for ss in rr.find_all('td'):
                        temp.append(ss.text)

                    if len(temp) == 10 and str(rr.get('id') + temp[3] + temp[4] + temp[5] + temp[6] + temp[7]) not in postID:
                        postTable, postID = cleanPostRowDetails(district, tradeType, rr,
                                                                links, temp, postTable, postID)
    finally:
        postID = []

    return postTable

##=============================================================##
##===================  GATHER SUB-CATEGORIES  =================##
##=============================================================##
def gatherSubCats(initialLink):
    """
    Gather all sub-categories (districts) from the main category page.

    Args:
        initialLink (str): URL of the main category page

    Returns:
        dict: Dictionary mapping district names to their URLs
    """
    subCats = {}

    #GET ALL SUB-CATEGORIES AND THEIR LINKS
    r = requests.get(initialLink)
    soup = BeautifulSoup(r.text, 'html.parser')

    raw = soup.find_all('a','a_category')
    for r in raw:
        subCats[r.text] = 'https://www.ss.com' + r.get('href')

    return subCats

##=============================================================##
##==============  GATHER ALL POST TABLE RECORDS  ==============##
##=============================================================##
def readPostList(subCats, categories=[], page_n=100, verbose=False):
    """
    Read all property listings from specified categories.

    Args:
        subCats (dict): Dictionary of subcategories (districts)
        categories (list): List of specific categories to scrape (empty = all)
        page_n (int): Number of pages to scrape per category
        verbose (bool): Print progress messages

    Returns:
        pd.DataFrame: DataFrame containing all scraped property data
    """

    numCols = ['Rooms', 'Size','Floor', 'Max. Floor','Price of sqm',
               'Alt. Price of sqm','Total Price', 'Alt. Price']
    cols = ['ID', 'Deal Type', 'Comment', 'Link', 'District', 'Street Name',
            'Street No.', 'Rooms', 'Size','Floor', 'Max. Floor','Project',
            'Post Date', 'Price of sqm', 'Alt. Price of sqm','Total Price', 'Alt. Price']

    dataframes = []

    if len(categories) > 0:
        keyList = categories
    else:
        keyList = subCats.keys()

    for key in keyList:
        if key != 'All announcements':
            if verbose: print('Processing', key);

            df_chunk = pd.DataFrame(GetProperties(subCats[key],
                                                  district = key,
                                                  pages=page_n),
                                   columns=cols)
            dataframes.append(df_chunk)

    dataDF = pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame(columns=cols)

    dataDF = dataDF.dropna()
    dataDF = dataDF[np.logical_and(dataDF['Total Price'] > 0, dataDF['Rooms'] != 'Other')]

    for col in numCols:
        dataDF[col] = pd.to_numeric(dataDF[col])

    # Parse dates with European format (day first: DD.MM.YYYY HH:MM)
    dataDF['Post Date'] = pd.to_datetime(dataDF['Post Date'], format='%d.%m.%Y %H:%M', errors='coerce')
    dataDF = dataDF.dropna()

    return dataDF

##=============================================================##
##========================  SAVE TO DB  =======================##
##=============================================================##
def saveToDB(newData, tableName, uniqCols, dbName = 'miniSS.db', cols = []):
    """
    Save scraped data to SQLite database.

    Args:
        newData (pd.DataFrame): New data to save
        tableName (str): Name of the database table
        uniqCols (list): Columns to use for identifying duplicates
        dbName (str): Database filename
        cols (list): Column names to save

    Returns:
        pd.DataFrame: Combined and deduplicated DataFrame
    """
    import sqlite3

    if len(cols) == 0: cols = newData.columns.to_list();

    conn = sqlite3.connect(dbName)
    try:
        oldData = pd.read_sql('SELECT * FROM ' + tableName, conn, index_col='ID').drop('index', axis = 1)

        #Format data to match between data tables
        for c in newData.dtypes[np.logical_or(newData.dtypes == 'float64',
                                              newData.dtypes == 'int64')].index:
            oldData[c] = pd.to_numeric(oldData[c])

        for c in newData.dtypes[newData.dtypes == 'datetime64[ns]'].index:
            oldData[c] = pd.to_datetime(oldData[c], errors='coerce')

        #Append and save to database
        newData = pd.concat([newData, oldData], ignore_index=True).sort_values(by=['Post Date'], ascending=False)
        newData = newData.drop_duplicates(uniqCols)
        newData.to_sql(tableName, conn, if_exists='append')
    except:
        newData = newData.drop_duplicates(uniqCols)
        newData.to_sql(tableName, conn, if_exists='append')

    conn.commit()
    conn.close

    return newData

def loadFromDB(tableName, dbName = 'miniSS.db', uniqCols = uniqCols):
    """
    Load data from SQLite database.

    Args:
        tableName (str): Name of the database table
        dbName (str): Database filename
        uniqCols (list): Columns to use for identifying duplicates

    Returns:
        pd.DataFrame: Loaded and deduplicated DataFrame
    """
    import sqlite3

    conn = sqlite3.connect(dbName)
    dbDF = pd.read_sql('SELECT * FROM ' + tableName, conn).drop(['index','ID'], axis = 1)

    for c in dbDF.columns:
        if "date" in c.lower(): dbDF[c] = pd.to_datetime(dbDF[c], errors='coerce');

    dbDF = dbDF.drop_duplicates(uniqCols)

    return dbDF
