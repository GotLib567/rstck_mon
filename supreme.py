'''
NERYS
supreme module

left to do:
save products to sql db
load products from sql db on startup
'''

from log import log
import requests
import time
from discord_hooks import Webhook
from bs4 import BeautifulSoup as soup
import random
from other-sites import FileNotFound

class Product:
    def __init__(self, link, image, title = "", stock = False):
        self.link = link
        self.image = image
        self.title = title
        self.stock = stock

def read_from_txt(path):

    raw_lines = []
    lines = []

    try:
        f = open(path, "r")
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


def get_proxy(proxy_list):

    proxy = random.choice(proxy_list)


    proxies = {
        "http": str(proxy),
        "https": str(proxy)
    }

    # Return the proxy
    return proxies


def send_embed(alert_type, product):
    url = discord_webhook
    embed = Webhook(url, color=123123)
    embed.set_author(name='ARB', icon='https://sun9-74.userapi.com/impf/x8e2VAfW-ao86OPcoUeSKpB7sup-dlIC3bT-2g/I3Vwk9su7D8.jpg?size=564x532&quality=96&sign=423037df9ddf5c5400c93844710086c3&type=album')
    if(alert_type == "RESTOCK"):
        embed.set_desc("RESTOCK: " + product.title)
    elif(alert_type == "NEW"):
        embed.set_desc("NEW: " + product.title)

    embed.add_field(name="Product", value=product.title)
    embed.add_field(name="Link", value=product.link)
    embed.add_field(name="Stock", value=str(product.stock))

    # Set product image
    embed.set_thumbnail(product.image)
    embed.set_image(product.image)

    # Set footer
    embed.set_footer(text='ARB by @JaqueFresco', icon='https://sun9-11.userapi.com/impf/DagUwT61wIcd0BeLtPOI3UFtf2nV2ZK9Gh-8NQ/ehNPfNbLWGA.jpg?size=754x750&quality=96&sign=ce4bfc72ef8fdcfbbf3c11dbd8589382&type=album', ts=True)

    # Send Discord alert
    embed.post()

def monitor():
    # GET "view all" page
    link = "http://www.supremenewyork.com/shop/all"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        }
    proxies = get_proxy(proxy_list)

    try:
        r = requests.get(link, timeout=5, verify=False)
    except:
        log('e', "Connection to URL <" + link + "> failed. Retrying...")
        try:
            if(use_proxies):
                proxies = get_proxy(proxy_list)
                r = requests.get(link, proxies=proxies, timeout=8, verify=False)
            else:
                r = requests.get(link, timeout=8, verify=False)                
        except:
            log('e', "Connection to URL <" + link + "> failed.")
            return

    page = soup(r.text, "html.parser")
    products = page.findAll("div", {"class": "inner-article"})

    log('i', "Checking stock of Supreme products...")
    for product in products:
        link = "https://www.supremenewyork.com" + product.a["href"]
        monitor_supreme_product(link, product)


def monitor_supreme_product(link, product):
    # Product info
    image = "https:" + product.a.img["src"]
    if(product.text == "sold out"):
        stock = False
    else:
        stock = True
        
    # Product already in database
    try:
        if(stock is True and products_list[link].stock is False):
            log('s', products_list[link].title + " is back in stock!")
            products_list[link].stock = True
            send_embed("RESTOCK", products_list[link])
        elif(stock is False and products_list[link].stock is True):
            log('s', products_list[link].title + " is now out of stock.")
            products_list[link].stock = False
    # Add new product to database
    except:
        # GET product name
        try:
            if(use_proxies):
                proxies = get_proxy(proxy_list)
                r = requests.get(link, proxies=proxies, timeout=8, verify=False)
            else:
                r = requests.get(link, timeout=8, verify=False)
        except:
            log('e', "Connection to URL <" + link + "> failed. Retrying...")
            try:
                if(use_proxies):
                    proxies = get_proxy(proxy_list)
                    r = requests.get(link, proxies=proxies, timeout=8, verify=False)
                else:
                    r = requests.get(link, timeout=8, verify=False)                  
            except:
                log('e', "Connection to URL <" + link + "> failed.")
                return

        title = soup(r.text, "html.parser").find("title").text

        # Add product to database
        products_list[link] = Product(link, image, title, stock)
        log('s', "Added " + title + " to the database.")
        send_embed("NEW", products_list[link])


def build_db():
    # GET "view all" page
    link = "http://www.supremenewyork.com/shop/all"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        }
    proxies = get_proxy(proxy_list)

    try:
        r = requests.get(link, timeout=5, verify=False)
    except:
        log('e', "Connection to URL <" + link + "> failed. Retrying...")
        try:
            if(use_proxies):
                proxies = get_proxy(proxy_list)
                r = requests.get(link, proxies=proxies, timeout=8, verify=False)
            else:
                r = requests.get(link, timeout=8, verify=False)
        except:
            log('e', "Connection to URL <" + link + "> failed.")
            return

    page = soup(r.text, "html.parser")
    products = page.findAll("div", {"class": "inner-article"})

    log('i', "Checking stock of Supreme products...")
    for product in products:
        link = "https://www.supremenewyork.com" + product.a["href"]

        # Product info
        image = "https:" + product.a.img["src"]
        if(product.text == "sold out"):
            stock = False
        else:
            stock = True        

        # GET product name
        try:
            if(use_proxies):
                proxies = get_proxy(proxy_list)
                r = requests.get(link, proxies=proxies, timeout=8, verify=False)
            else:
                r = requests.get(link, timeout=8, verify=False)
        except:
            log('e', "Connection to URL <" + link + "> failed. Retrying...")
            proxies = get_proxy(proxy_list)
            r = requests.get(link, proxies=proxies, timeout=8, verify=False)
            try:
                if(use_proxies):
                    proxies = get_proxy(proxy_list)
                    r = requests.get(link, proxies=proxies, timeout=8, verify=False)
                else:
                    r = requests.get(link, timeout=8, verify=False)                  
            except:
                proxies = get_proxy(proxy_list)
                log('e', "Connection to URL <" + link + "> failed.")
                return

        title = soup(r.text, "html.parser").find("title").text

        # Add product to database
        products_list[link] = Product(link, image, title, stock)
        log('s', "Added " + title + " to the database.")


if(__name__ == "__main__"):
    # Ignore insecure messages
    requests.packages.urllib3.disable_warnings()

    # Load proxies (if available)
    proxy_list = read_from_txt("proxies.txt")
    log('i', "Loaded " + str(len(proxy_list)) + " proxies.")
    if(len(proxy_list) == 0):
        use_proxies = False
    else:
        use_proxies = True    

    # Initialize variables
    products_list = {}
    proxies = get_proxy(proxy_list)
    discord_webhook = ""  # Put your webhook here

    # Build database
    build_db()

    # Monitor products
    while(True):
        monitor()
        time.sleep(8)