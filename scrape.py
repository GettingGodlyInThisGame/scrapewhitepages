import requests, re
from pymongo import MongoClient
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

searchterm = 'johnson'
client = MongoClient('localhost', 27017)
db = client['whitepages']
collection = db['scraped']

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

r = requests.get('https://whitepages.co.nz/white-all/'+searchterm+'/new-zealand/')
page = r.text

soup = BeautifulSoup(page, 'html.parser')

#<section class="pagination">
pagination = soup.find('section', class_="pagination")
lis = pagination.find_all("li")
lis.pop(3)

safe = int(strip_tags(str(lis[-1])))
safe_list = range(1, safe+1)

def run(num, searchterm):
    r = requests.get('https://whitepages.co.nz/white-all/'+searchterm+'/new-zealand/'+str(num)+'/')
    page = r.text

    soup = BeautifulSoup(page, 'html.parser')

    pagination = soup.find('section', class_="pagination")
    lis = pagination.find_all("li")
    addlist = strip_tags(str(lis[2]))
    safe_list.append(addlist)

    results = soup.find(id="contentMainSearchResults")
    section = results.find_all('section')[1]
    sections = section.find_all('li', {"data-ga-catid":"bus", "data-ga-catid":"res"})
    for item in sections:
        #<a href="/w/albany-johnson-eden/" data-ga-id="Listing_Name_Link">Albany Johnson Ltd</a>
        name = item.find('h2')
        #<p class="itemAddress">
        address = item.find('p', class_="itemAddress")
        #<a href="javascript:void(0);" style="cursor: pointer;" class="button buttonAlt actionContact phoneLink" data-ga-id="Phone_Call_Us" data-listingid="100592294_BUS" data-telephone="09-585-2475"><i class="icon-phone after-text"></i> Show number</a>
        phone_num = item.find('a', class_="button buttonAlt actionContact phoneLink")
        #<a href="/w/albany-johnson-eden/" class="button actionMoreInfo" data-ga-id="More_Info_Link"><i class="icon-info after-text"></i> More info</a>
        url = item.find('a', class_="button actionMoreInfo")

        #print "Name: "+strip_tags(str(name))
        name = strip_tags(str(name))
        #print "Address: "+strip_tags(str(address))
        address = strip_tags(str(address))
        #print "Number: "+str(phone_num["data-telephone"])
        phone_num = str(phone_num["data-telephone"])
        #print "URL: https://whitepages.co.nz"+str(url["href"])
        url = "https://whitepages.co.nz"+str(url["href"])
        post = {"name": name,
            "address": address,
            "phone_num": phone_num,
            "url": url}
        posts = db.scraped
        posts.insert_one(post)
        print "Imported: "+name
    safe_list.pop(0)

while True:
    run(safe_list[0], searchterm)
