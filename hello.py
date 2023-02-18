from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from time import sleep
from random import randint
import pandas as pd

executable_path = "C:\webdriver\chromedriver.exe"
try:
    driver = webdriver.Chrome()
except:
    driver = webdriver.Chrome(executable_path=executable_path)

driver.get('https://www.google.com/')

sleep(500)