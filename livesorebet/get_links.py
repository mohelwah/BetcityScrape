from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from time import sleep
from random import randint
import pandas as pd



url = "https://www.livescorebet.com/nl-nl/sports/volleybal/SBTC1_19"

try:
    executable_path = "C:\webdriver\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=executable_path)
except:
    driver = webdriver.Chrome()
    
driver.get(url)
sleep(10)
soup = BeautifulSoup(driver.page_source, 'html.parser')

base_url = "https://www.livescorebet.com"


def get_links(class_name):
    links = []
    for link in soup.find_all(class_=class_name, href=True):
        links.append(base_url + link['href'])
    return links
match_class = "sc-1dob51z-0 kTvekW sc-10e4yro-1 esgLjE"
links = get_links(match_class)
# write the links in a txt file 
with open('livescore_links.txt', 'w') as f:
    for link in links:
        #write new line
        f.write(link + "\n")
