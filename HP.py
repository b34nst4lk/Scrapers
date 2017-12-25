from requests import get
from bs4 import BeautifulSoup as bs
from csv import DictWriter
from datetime import datetime
from pprint import pprint
from unidecode import unidecode
import os
import re

PAGE_URL = 'http://h20386.www2.hp.com/SingaporeStore/Merch/List.aspx?sel={}&ctrl=f&take=1000&skip=0' 
ITEM_URL = 'http://h20386.www2.hp.com/SingaporeStore/Merch/{}'

MERCH_LIST = ['NTB', 'DTP']

def getHTML(link, suffix=''):
    return bs(get(link.format(suffix)).content, "html.parser")


def cleanText(string):
    # Remove non-ascii characters
    string = unidecode(string)

    # remove any text that may screw with Excel, and clearn up the text to look pretty
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


def getItemDetails(suffix=''):
    item = {}
    content = getHTML(ITEM_URL, suffix)
    print(suffix)
    item['name'] = content.find('h1', {'class': 'pb-product__name'}).text
    item['price'] = content.find('p', {'class': 'pb-price__now'}).text 
    table = content.find('table', {'class': 'specs-table'})
    for spec in table.find_all('tr'):
        key = spec.find('th', {'class': 'specs-table__key'})
        value = spec.find('td', {'class': 'specs-table__value'})
        if key and value:
            key_string = cleanText(key.text)
            value_string = cleanText(value.text)

            item[key_string] = value_string
    return item


def getItemList(suffix):
    item_list = getHTML(PAGE_URL, suffix).find_all('div', {'class': 'product__title'})
    print(len(item_list))
    for item in item_list:
        link = item.find('a', {'itemprop': 'url'})['href']
        item_id = re.search(r'id=\w*', link).group().split('=')[-1]
        yield {'link': link, 'id': item_id}


if __name__ == '__main__':
    for category in MERCH_LIST:
        all_data  = []
        headers = []
        for item in getItemList(category):
            item.update(getItemDetails(item['link']))
            all_data.append(item)
            headers.extend([key for key in item.keys() if key not in headers])

        with open('{}_{}.csv'.format(category, datetime.now()), 'w') as w:
            writer = DictWriter(w, fieldnames=headers)

            writer.writeheader()
            writer.writerows(all_data)
