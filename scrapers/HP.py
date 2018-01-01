from bs4 import BeautifulSoup as bs
from csv import DictWriter
from datetime import datetime
from requests import get
from pprint import pprint
from unidecode import unidecode
from mongo import MongoSession
import os
import re

PAGE_URL = 'http://h20386.www2.hp.com/SingaporeStore/Merch/List.aspx?sel={}&ctrl=f&take=1000&skip=0' 
ITEM_URL = 'http://h20386.www2.hp.com/SingaporeStore/Merch/{}'
MAIN_URL = 'http://h20386.www2.hp.com/SingaporeStore/Merch'

def getHTML(link, suffix=''):
    return bs(get(link.format(suffix)).content, "html.parser")


def cleanText(string):
    # Remove non-ascii characters
    string = unidecode(string)

    # remove any text that may screw with Excel, and clean up the text to look pretty
    line_breaks = {'\n': '', '\r': '', '\t': ''}
    cleanDict = {"'": "`", '"' : "`", "  ": " "}
    string = string.strip()

    # remove all line breaks and tabs in a string first
    for key in line_breaks:
        string = string.replace(key, line_breaks[key])

    # replace all double spaces with single spaces, and replace all quotes with backticks `
    for key in cleanDict:
        string = string.replace(key, cleanDict[key])

    return string.strip()


def getItemDetails(url=ITEM_URL, suffix=''):
    item = {}
    content = getHTML(url, suffix)
    item['name'] = content.find('h1', {'class': 'pb-product__name'}).text
    item['price'] = content.find('p', {'class': 'pb-price__now'}).text 
    table = content.find('table', {'class': 'specs-table'})
    if table:
        for spec in table.find_all('tr'):
            key = spec.find('th', {'class': 'specs-table__key'})
            value = spec.find('td', {'class': 'specs-table__value'})
            if key and value:
                key_string = cleanText(key.text)
                value_string = cleanText(value.text)

                item[key_string] = value_string
    return item


def getItemList(url=PAGE_URL, suffix=''):
    item_list = getHTML(url, suffix).find_all('div', {'class': 'product__title'})
    for item in item_list:
        link = item.find('a', {'itemprop': 'url'})['href']
        item_id = re.search(r'id=\w*', link).group().split('=')[-1]
        yield {'link': link, 'id': item_id}

def getCatList(url=MAIN_URL):
    category_list = getHTML(url).find_all('a', {'class': 's-h-nav-item__link'})
    for category in category_list:
        string = re.findall('sel=\w*', category['href'])
        if string:
            yield string[0].split("=")[-1]
     


if __name__ == '__main__':
    session = MongoSession('mongodb://localhost:10101', db='hp')
    
    for category in getCatList():
        print('Scraping {}'.format(category))
        headers = []
        print('Scraping items...')
        for count, item in enumerate(getItemList(url=PAGE_URL, suffix=category)):
            if count % 5 == 1:
                print('{} items scraped'.format(count))
            item.update(getItemDetails(url=ITEM_URL, suffix=item['link']))
            filter_dict = {'id': item['id']}
            session.update(filter_dict, item, category, upsert=True)
