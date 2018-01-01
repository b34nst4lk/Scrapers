from requests import get
from bs4 import BeautifulSoup as bs
from csv import DictWriter
from datetime import datetime
from mongo import MongoSession
from unidecode import unidecode
import os

PAGE_URL = 'https://www.quotz.com.sg/cars_for_bidding/{}'
CAR_URL = 'https://www.quotz.com.sg/biddingdetails?AID={}'


def getHTML(link, suffix):
    return bs(get(link.format(suffix)).content, "html.parser")


def cleanText(string, key=False):
    # Remove non-ascii characters
    string = unidecode(string)

    # remove any text that may screw with Excel, and clean up the text to look pretty
    line_breaks = {'\n': '', '\r': '', '\t': ''}
    cleanDict = {"'": "`", '"' : "`", "  ": " "}
    if key:
        cleanDict["."] = ""
    string = string.strip()

    # remove all line breaks and tabs in a string first
    for key in line_breaks:
        string = string.replace(key, line_breaks[key])

    # replace all double spaces with single spaces, and replace all quotes with backticks `
    for key in cleanDict:
        string = string.replace(key, cleanDict[key])

    return string.strip()


def getCarDetails(car_id):
    car = {}
    content = getHTML(CAR_URL, car_id).find('div', {'class': 'bidding-details'})
    car['Model'] = content.find('h1').text
    car['Bidprice'], car['NoOfBids'] = [info.text for info in content.find_all('span', {'class': 'bid-style'})]
    for row in content.find_all('div', {'class': 'car-details'}):
        info = row.find_all('div')
        car[cleanText(info[1].text, key =True)] = cleanText(info[2].text)
    car['Posted at'] = cleanText(content.find('div', {'class': 'etc-info'}).text.split('|')[0].split(":")[1])
    return car, car.keys()


def getCarList(limit=0):
    page_num = 0
    while True:
        page_num += 1
        car_list= getHTML(PAGE_URL, page_num).find_all('div', {'class': 'box-01'})

        if (limit and limit <  page_num) or len(car_list) == 0:
            return
        else:
            for each_car in car_list:
                link = each_car.find('a')['href']
                car_id = link.split('=')[-1]
                car_status = each_car.find('div', {'class': 'solid-btn'}).text
                car = {'id': car_id,
                        'status': car_status}
                yield car


#----------------------------------------
#       Scraping  begins here
#----------------------------------------
session = MongoSession('mongodb://localhost:10101', db='quotz')

print('Start! {}'.format(datetime.now()))
for count, car_info in enumerate(getCarList()):
    if count % 10 == 0:
        print('{} cars scraped'.format(count))

    car_details, headers = getCarDetails(car_info['id'])
    filter_dict = {'id': car_info['id']}
    car_details.update(filter_dict)
    session.update(filter_dict , car_details, 'quotz', upsert=True)
    
print('Scraping complete')
