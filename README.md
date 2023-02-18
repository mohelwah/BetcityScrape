[![Scrape with power bi integeration](https://github.com/mohelwah/powerBi_scrape_intgration/actions/workflows/main.yml/badge.svg)](https://github.com/mohelwah/powerBi_scrape_intgration/actions/workflows/main.yml)


# Project Type: Scrape Project
# Project Name : Betcity 

this is scaffold template for Betcity Scrape in python 
 Create the following:
 - Makefile
 - requirement.txt
 -Linux system:
    - virtial enviroment: python -m venv ~/.betcity
    - activate venv envi: source ~/.betcity/bin/activate
 - Windows system:
    - virtial enviroment: python -m venv c:\venv\betcity
    - activate venv envi:   C:\venv\betcity\Scripts\activate.ps1
 - hello.py file
 - test_hello.py file 
 - to check the python version:
    - in linux : which python  
    - in windows: Get-Command python | fl *
 - get pack list:
    - pip freeze or pip list 
    test

## To run selenuim in github codespace
-  sudo apt-get updata 
- apt-get install libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb
* install chrome 
- wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
- sudo apt install ./google-chrome-stable_current_amd64.deb