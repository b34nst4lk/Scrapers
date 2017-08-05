from requests import get
from bs4 import BeautifulSoup as bs
from math import ceil
from pandas import DataFrame
import datetime
import os

print('Start! {}'.format(datetime.datetime.now()))

def getHTML(link, counter):
    return bs(get(link.format(counter)).content, "html.parser")

Date = datetime.datetime.today().strftime('%y%m%d')

# Grab links from search pages
## To filter for specific search results, update the suffixes of the url below.
link = 'http://www.sgcarmart.com/used_cars/listing.php?BRSR={}&RPG=100&AVL=2&VEH=2'

## Get the total page count for search results
page_count = getHTML(link, 0).find('p', class_='vehiclenum').get_text()
page_count = int(ceil(int(page_count.split(' ')[0].replace(',',''))/100))
print('Page Count: {}'.format(page_count))

## Get all <a> tags with "info.php?ID=" in the href attribute from the search result pages and store in id and link in dictionary
## URL of individual cars in SGCarMart contain "info.php?ID="
output = {}

for i in range(page_count):
    print('Page Progress: {} {}'.format(i, datetime.datetime.now()))
    html = set(getHTML(link, i * 100).find_all('a'))
    for a_tags in html:
        if a_tags['href'].find('info.php?ID=') == 0:
            suffix = a_tags['href']
            key = int(suffix.replace('info.php?ID=', '').split('&')[0])
            output[key] = {'suffix': suffix, 'id': key}

print('Links Get! {}'.format(datetime.datetime.now()))

# For each car, find the first <div> tag with class "box". Go through each row within the table in the <div> and scrape data from columns 1 and 2.
link = 'http://www.sgcarmart.com/used_cars/{}'
for i, key in enumerate(output):
    html = getHTML(link, output[key]['suffix'])
    table = html.find('div', id='main_left').find('div', class_='box')

    # For monitoring progress
    if i % 10 == 0:
        print('{}: {}'.format(i, datetime.datetime.now()))
    rows = table.find_all('tr')

    for row in rows:
        cells = row.find_all('td')

        # If statement excludes rows that are not required.
        if len(cells) >= 2 and \
                cells[0].get_text() and cells[1].get_text() and \
                (cells[0].get_text().find('View specs of') == -1 or
                 cells[0].get_text().find('Available') == -1):

            output[key][cells[0].get_text().strip()] = cells[1].get_text().strip()
print('Data Scrapped! {}'.format(datetime.datetime.now()))

output_df = DataFrame(output)

output_df.to_csv('{}\SGCarMart{}.csv'.format(os.getcwd(), Date), index=True)
print('End! {}'.format(datetime.datetime.now()))
