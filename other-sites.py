
from log import log
import requests
import time
from discord_hooks import Webhook
from threading import Thread
from bs4 import BeautifulSoup as soup
import sqlite3
class FileNotFound(Exception):
    ''' Raised when a file required for the program to operate is missing. '''


class NoDataLoaded(Exception):
    ''' Raised when the file is empty. '''


class OutOfProxies(Exception):
    ''' Raised when there are no proxies left '''


class Product():
    def __init__(self, title, link, stock, keyword):
        '''
        (str, str, bool, str) -> None
        Creates an instance of the Product class.
        '''
    
        # Setup product attributes
        self.title = title
        self.stock = stock
        self.link = link
        self.keyword = keyword


def read_from_txt(path):
    '''
    (None) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''

    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(r'C:\Users\War_child\PycharmProjects\restock_monitor\other-sites.txt', "r")
        raw_lines = f.readlines()
        f.close()

    # Raise an error if the file couldn't be found
    except:
        log('e', "Couldn't locate <" + path + ">.")
        raise FileNotFound()

    if(len(raw_lines) == 0):
        raise NoDataLoaded()

    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Return the data
    return lines


def add_to_db(product):
    '''
    (Product) -> bool
    Given a product <product>, the product is added to a database <products.db>
    and whether or not a Discord alert should be sent out is returned. Discord
    alerts are sent out based on whether or not a new product matching
    keywords is found.
    '''

    # Initialize variables
    title = product.title
    stock = str(product.stock)
    link = product.link
    keyword = product.keyword
    alert = False

    # Create database
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products(title TEXT, link TEXT UNIQUE, stock TEXT, keywords TEXT)""")

    # Add product to database if it's unique
    try:
        c.execute("""INSERT INTO products (title, link, stock, keywords) VALUES (?, ?, ?, ?)""", (title, link, stock, keyword))
        log('s', "Found new product with keyword " + keyword + ". Link = " + link)        
        alert = True
    except:
        # Product already exists
        pass
        #log('i', "Product at URL <" + link + "> already exists in the database.")

    # Close connection to the database
    conn.commit()
    c.close()
    conn.close()

    # Return whether or not it's a new product
    return alert


def send_embed(product):

    url = 'https://discordapp.com/api/webhooks/818881746308169749/TB7nvYzt6A4ZwJPEJzGFVzuRKpYRHR61Ka329pMCwWyF4fFwpV4Lt2lCdy1y8FljjkGz'

    embed = Webhook(url, color=123123)

    embed.set_author(name='ARB', icon='https://sun9-74.userapi.com/impf/x8e2VAfW-ao86OPcoUeSKpB7sup-dlIC3bT-2g/I3Vwk9su7D8.jpg?size=564x532&quality=96&sign=423037df9ddf5c5400c93844710086c3&type=album')
    embed.set_desc("Found product based on keyword " + product.keyword)

    embed.add_field(name="Link", value=product.link)

    embed.set_footer(text='ARB by @JaqueFresco', icon='https://sun9-11.userapi.com/impf/DagUwT61wIcd0BeLtPOI3UFtf2nV2ZK9Gh-8NQ/ehNPfNbLWGA.jpg?size=754x750&quality=96&sign=ce4bfc72ef8fdcfbbf3c11dbd8589382&type=album', ts=True)

    embed.post()


def monitor(link, keywords):

    log('i', "Checking site <" + link + ">...")


    pos_https = link.find("https://")
    pos_http = link.find("http://")

    if(pos_https == 0):
        site = link[8:]
        end = site.find("/")
        if(end != -1):
            site = site[:end]
        site = "https://" + site
    else:
        site = link[7:]
        end = site.find("/")
        if(end != -1):
            site = site[:end]
        site = "http://" + site

    # Get all the links on the "New Arrivals" page
    try:
        r = requests.get(link, timeout=5, verify=False)
    except:
        log('e', "Connection to URL <" + link + "> failed. Retrying...")
        time.sleep(5)
        try:
            r = requests.get(link, timeout=8, verify=False)
        except:
            log('e', "Connection to URL <" + link + "> failed.")
            return

    page = soup(r.text, "html.parser")

    raw_links = page.findAll("a")
    hrefs = []

    for raw_link in raw_links:
        try:
            hrefs.append(raw_link["href"])
        except:
            pass

    # Check for links matching keywords
    for href in hrefs:
        found = False
        for keyword in keywords:
            if(keyword.upper() in href.upper()):
                found = True
                if("http" in href):
                    product_page = href
                else:
                    product_page = site + href
                product = Product("N/A", product_page, True, keyword)
                alert = add_to_db(product)

                if(alert):
                    send_embed(product)

if(__name__ == "__main__"):
    requests.packages.urllib3.disable_warnings()


    keywords = [
        "air-force-1",
        "blazer-mid",
        "dunk"
        "pharrell",
        "off-white",
        "kendrick",
        "tinker",
        "game-royal",
        "yeezy",
        "quantum",
        "human-race",
        "big-bang",
        "dont-trip",
        "kung-fu-kenny",
        "playstation",
        "valentine",
        "ovo-air-jordan",
        "ovo-jordan",
        "air-jordan-1",
        "Air-Jordan"
        "wotherspoon"
    ]
    

    sites = read_from_txt("other-sites.txt")


    while(True):
        threads = []
        for site in sites:
            t = Thread(target=monitor, args=(site, keywords))
            threads.append(t)
            t.start()
            time.sleep(2)
