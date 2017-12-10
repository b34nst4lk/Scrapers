from requests import get
from bs4 import BeautifulSoup as bs
from csv import DictWriter
from datetime import datetime
import os
from pprint import pprint

PAGE_URL = 'https://www.quotz.com.sg/cars_for_bidding/{}'
CAR_URL = 'https://www.quotz.com.sg/biddingdetails?AID={}'


def getHTML(link, suffix):
    #beautiful soup tells the software to get the link from website as content
    return bs(get(link.format(suffix)).content, "html.parser")


def cleanText(string):
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


def getCarDetails(car_id):
    car = {}
    car['id'] = car_id
    content = getHTML(CAR_URL, car_id).find('div', {'class': 'bidding-details'})
    car['Model'] = content.find('h1').text
    car['Bidprice'], car['NoOfBids'] = [info.text for info in content.find_all('span', {'class': 'bid-style'})]
    for row in content.find_all('div', {'class': 'car-details'}):
        info = row.find_all('div')
        car[cleanText(info[1].text)] = cleanText(info[2].text)
    return car, car.keys()


def getCarList(limit=0):
    page_num = 0
    while True:
        page_num += 1
        car_list= getHTML(PAGE_URL, page_num).find_all('div', {'class': 'box-01'})

        if (limit and limit <  page_num) or len(car_list) == 0:
            return
        else:
            for car in car_list:
                link = car.find('a')['href']
                car_id = link.split('=')[-1]
                yield car_id


#----------------------------------------
#       Scraping  begins here
#----------------------------------------

print('Start! {}'.format(datetime.now()))
cars = []
all_headers = []
for count, car_id in enumerate(getCarList(1)):
    if count % 100 == 0:
        print('{} cars scraped'.format(count))

    car_details, headers = getCarDetails(car_id)
    cars.append(car_details)
    # Ensure that all headers are accounted for
    all_headers.extend([header for header in headers if header not in all_headers])
print('Scraping complete')

print('Preparing csv file...')
path = os.path.dirname(os.path.realpath(__file__))
path += '/' if '/' in path else '\\'

with open('{}quotz_{}'.format(path, datetime.now().strftime('%y%m%d')), 'w') as output_file:
    csv = DictWriter(output_file, all_headers)
    csv.writeheader()
    csv.writerows(cars)
    print('File saved at {}'.format(path))
