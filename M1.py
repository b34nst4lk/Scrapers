from bs4 import BeautifulSoup as bs
from requests import get
from pandas import DataFrame
import datetime
import os

print('Start! {}'.format(datetime.datetime.now()))


def getHTML(link, suffix):
    return bs(get(link.format(suffix)).content, "html.parser")


def cleanText(string):
    cleanDict = {"'": "`",
                 '"': "`",
                 "\n": " ",
                 "  ": " "}
    for key in cleanDict:
        string = string.replace(key, cleanDict[key])
    return string.strip()

Date = datetime.datetime.today().strftime('%y%m%d')

# Grab links from search pages
links = {'phone': "https://www.m1.com.sg/personal/mobile/phones/filters/all-plans/all/all/0/1500/0/0/none",
         'tablet': "https://www.m1.com.sg/personal/mobile-broadband/tablet/filters/all-plans/all/all/0/2000/0/0/none"}

output = {}

for type in links:
    html = get(links[type]).content
    div_tags = set(bs(html, 'html.parser').find_all('div', class_="td two description"))
    for div_tag in div_tags:
        a_tag = div_tag.find('a')
        suffix = a_tag['href']
        uin = suffix.split('/')[-1]
        output[uin] = {'name': uin, 'suffix': suffix, 'type': type}
print('{} Links Get! {}'.format(len(output), datetime.datetime.now()))

link = 'https://www.m1.com.sg{}'
for i, item in enumerate(output):
    if i % 10 == 0:
        print('{}: {}'.format(i, datetime.datetime.now()))
    html = getHTML(link, output[item]['suffix'])
    plans = html.find_all('section', class_='plan-panel')
    for plan in plans:
        plan_name = cleanText(plan.find('div', class_='title').get_text())
        prices = plan.find('div', class_='price').get_text()
        phone_price = cleanText(prices.split('Pay Now')[0])
        output[item][plan_name] = phone_price

print('Data Scrapped! {}'.format(datetime.datetime.now()))

output_df = DataFrame()

for i in output:
    output_df = output_df.append(output[i], ignore_index=True)

output_df.to_csv('{}\M1 {}.csv'.format(os.getcwd(), Date), index=False)
print('End! {}'.format(datetime.datetime.now()))
