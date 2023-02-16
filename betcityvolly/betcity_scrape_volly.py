from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import threading
import time
import pickle
from random import randint

def small_sleep(low=1, high=5):
    time.sleep(randint(low, high))

import pandas as pd
executable_path = "C:\webdriver\chromedriver.exe"

class Scraper:
    
    def __call__(self):
        
        # Changing chromedriver default options
        options = Options()
        #options.headless = False # Change to False if you want it to happen visually
        options.add_argument("--start-maximized") #Headless = True
        
        max_workers = 1
        drivers = []
        threads = []
        dataframes = [pd.DataFrame() for _ in range(max_workers)]
        links = []

        def cookies(driver):
            driver.get('https://www.betcity.nl/sportsbook#sports-hub/volleyball')
            
            # Cookie button
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonAccept"]')))
                time.sleep(5)
                driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonAccept"]').click()
            except: 
                return
            
        # Scrapes a soccer league on Betcity
        def scrape(driver, link, worker):
            
                       
            # for Vollyball srip
            teams_list = []
            winnar_list = []
            top2_list = []

            def click(webElement):
                ActionChains(driver).move_to_element(webElement)
                webElement.click()
                
            def wait(xpath):
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
                except: 
                    return
            
            def volly_scrape(soup):
                teams = []
                winnar = []
                top2 = []
   
                t = soup.find_all(class_="KambiBC-outcomes-list__label")
                for i in range(len(t)):
                    teams.append(t[i].text)
                
                numbers = soup.find_all(class_="OutcomeButton__Odds-sc-lxwzc0-6")
                for i in range(len(numbers)):
                    if i < len(numbers)/2:
                        winnar.append(float(numbers[i].text))
                    else:
                        top2.append(float(numbers[i].text))
                
                teams_list.append(teams)
                winnar_list.append(winnar)
                top2_list.append(top2)

                return(teams,  winnar, top2)

            driver.get(link)
            
            # The links of all singular matches
            matchLinks = []
        
            # Wait for the data to load
            
            try:
                wait(".//ul[@class='KambiBC-sandwich-filter__list']")
            except:
                print("Competition not found")
                return
           
            # Find all matches
            matches = driver.find_elements(By.XPATH, ".//li[@class='KambiBC-sandwich-filter__event-list-item KambiBC-sandwich-filter__event-list-competition-item']")
            print(f'this is Matches: {matches}')
            # Loop through each match to extract the links
            for match in matches:
                print(f'his is Match: {match}')
                current_day = time.localtime()[6]
                try:
                    match_day = match.find_element(By.XPATH, ".//span[@class='KambiBC-event-item__start-time--date']").text
                    print(f'his is Match_day: {match_day}')

                except:
                    continue
                '''
                if match_day == "ma":
                    match_day = 0
                elif match_day == "di":
                    match_day = 1
                elif match_day == "wo":
                    match_day = 2
                elif match_day == "do":
                    match_day = 3
                elif match_day == "vr":
                    match_day = 4
                elif match_day == "za":
                    match_day = 5
                elif match_day == "zo":
                    match_day = 6
                else:
                    continue
                
                date_diff = match_day - current_day
                if current_day != 6:
                    if date_diff < 0 or date_diff > 1 :
                        continue
                else:
                    if match_day != 0 and match_day != 6:
                        continue
                '''


                link = match.find_element(By.XPATH, ".//a").get_attribute('href')
                print(f'his is Link: {link}')

                try:
                    amount = int(match.find_element(By.XPATH, ".//div[@class='KambiBC-sandwich-filter_show-more-right-text']").text.split("B", 1)[0])
                    print(f'his is Amount: {amount}')

                except:
                    continue
                if link.find('live') == -1 and amount < 40:
                    matchLinks.append(link)
                    print(f'his is MatchLinks: {matchLinks}')
                
            # Visit each single match to extract the needed data
            for link in matchLinks:
                
                driver.get(link)
                print('got to link')
                # Wait for the data to load
                #wait(".//button[@class='KambiBC-outcomes-list__toggler-toggle-button']")
                # selelenium wait page to load
                small_sleep(high=10)
                
                # Scrape the result data
                #if not scrape_result():
                    #continue
                
                #bet_links.append(driver.current_url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                print(volly_scrape(soup=soup))
                # Scrape the dubbele kans data
                #scrape_dubbele_kans()
                
                # Scrape the over/under data
                #scrape_over_under()
                
                # Scrape the beide teams scoren data
                #scrape_beide_teams_scoren()
                
                # Scrape the handicap data
                #scrape_handicap()
                
                # Scrape the halves odds category data
                #scrape_halves()

            '''
            for vollyball
            '''
            # After each competition we create a dataframe with the odds that we have so far collecte
            dict_worker = {"Teams": teams_list, "Winnar": winnar_list, "Top2": top2_list} 
            print(f'his is dict_worker: {dict_worker}')

            '''    
            # After each competition we create a dataframe with the odds that we have so far collected
            dict_worker = {'Teams': names, 'result' : result_list, 'over_under' : over_under_list, 'over_under_1e' : over_under_1e_list,
                        'over_under_2e' : over_under_2e_list, 'handicap' : handicap_list, 'beide_teams_scoren' : beide_teams_scoren_list,
                        'beide_teams_scoren_1e' : beide_teams_scoren_1e_list, 'beide_teams_scoren_2e' : beide_teams_scoren_2e_list, 'dubbele_kans' : dubbele_kans_list, 'bet_links' : bet_links}
            '''
            dataframes[worker] = pd.concat([dataframes[worker], pd.DataFrame.from_dict(dict_worker)])
            print(f'his is dataframes[worker]: {dataframes[worker].head()}')
        
        ## Run the Scraper
        start_time = time.time()
        print('starting scraper')
        with open('betcity_volly.txt', 'r') as f:
            links = f.read().split('\n')
        
        amount_links = len(links)
        links_used = 0
        
        for i in range(0, max_workers):
            drivers.append(webdriver.Chrome(executable_path=executable_path,options=options))
            #drivers.append(webdriver.Chrome(options=options))
            threads.append(threading.Thread(target=cookies, args=[drivers[i]]))
            threads[i].start()
        
        while True:
            skip = False
            
            try:
                df_betcity = pd.concat([i for i in dataframes if not i.empty])
            except:
                skip = True
            
            stop = True
            
            for i in range(max_workers):
                if links_used >= amount_links:
                    if threads[i].is_alive():
                        stop = False
                        
                elif not threads[i].is_alive():
                    if links[links_used] == '':
                        links_used += 1
                        continue
                    
                    threads[i] = threading.Thread(target=scrape, args=[drivers[i], links[links_used], i])
                    threads[i].start()
                    links_used += 1
                    stop = False
                    
                else: stop = False
            
            if skip:
                continue
            
            output = open('df_betcity_volly_test', 'wb')
            pickle.dump(df_betcity, output)
            output.close()
            
            if stop:
                break
            
            time.sleep(1)
        
        for driver in drivers:
            driver.quit()
            
        print("Betcity finished in: %s seconds" % int((time.time() - start_time)))
        
Scraper.__call__(Scraper)