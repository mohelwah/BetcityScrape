from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import threading
import time
import pickle
from random import randint
from time import sleep
import pandas as pd


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
            driver.get('https://www.livescorebet.com/nl-nl/sports/volleybal/SBTC1_19')
            
            # Cookie button
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
                time.sleep(5)
                driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
            except: 
                return
            
        # Scrapes a soccer league on Betcity
        def scrape(driver, link, worker):
            
            # List of team-names: ['teamname1'\n'teamname2', ....]
            active_links = []
            bet_links = []
            names = []
            winner = []
            handicap_points = []
            set_handicap = []
            over_under = []
            over_under_points = []
            winnar_trans = ["winner","winnaar"]
            set_trans = ["set Handicap", "set"]
            handicap_points_trans = ["handicap Points","handicap punten"]
            over_under_trans = ["over/under", "meer dan/minder dan"]
            over_under_points_trans = ["over/under points", "meer dan/minder dan punten"]
            def click(webElement):
                ActionChains(driver).move_to_element(webElement)
                webElement.click()
                
            def wait(xpath):
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
                except: 
                    return
            ## LiveScoreBet scraper  
            def scrape_teamsName():
                # get odds blocks  
                odds = driver.find_elements(By.CLASS_NAME, "fwc8o3-15")
                odds = [odd.text.lower() for odd in odds if odd.text != ""]
                for i in range(len(odds)):
                    type = odds[i].split(sep="\n")
                    if type[0] in winnar_trans:
                        name= type[1] + "\n" + type[3]
                        break
                    elif type[0] in handicap_points_trans:
                        name = type[1][:-4] + "\n" + type[3][:-4]
                        break
                    elif type[0] in set_trans:
                        name = type[1][:-4] + "\n" + type[3][:-4]
                    
                try:
                    names.append(name)
                except:
                    print('coudnt find name')
                #for debug
                print('this form scrape_teamsName function {}'.format(names))

            def scrape_odds():

                odds = driver.find_elements(By.CLASS_NAME, "fwc8o3-15")
                odds = [odd.text.lower() for odd in odds if odd.text != ""]
                for i in range(len(odds)):
                    type = odds[i].split(sep="\n")
                    if type[0] in winnar_trans:
                        temp = odds[i].split(sep="\n")
                        winner.append(temp[2] + "\n" + temp[4])

                    elif type[0] in handicap_points_trans:
                        temp = odds[i].split(sep="\n")
                        handicap_points.append(temp[2] + "\n" + temp[4])
                    elif type[0] in set_trans:
                        temp = odds[i].split(sep="\n")
                        set_handicap.append(temp[2] + "\n" + temp[4])
                    elif type[0] in over_under_trans:
                        temp = odds[i].split(sep="\n")
                        over_under.append(temp[3] + "\n" + temp[4] + "\n" + temp[5])
                    elif type[0] in over_under_points_trans:
                        temp = odds[i].split(sep="\n")
                        over_under_points.append(temp[3] + "\n" + temp[4] + "\n" + temp[5])
                #for debug
                print('this form scrape_odds function winner {}\n set {}\n hed{} \n over{} \npointer {}'.format(winner,set_handicap,handicap_points,over_under, over_under_points))

            
            
            driver.get(link)
            print('*' * 50)
            print("Scraping " + link)
            print('*' * 50)
            # The links of all singular matches
            matchLinks = []
        
            # Wait for the data to load
            try:
                wait(".//ul[@class='KambiBC-sandwich-filter__list']")
            except:
                print("Competition not found")
                return
        
            # Find all matches
            matches = driver.find_elements(By.CLASS_NAME, "effrky-4")
            print('there are {} matched'.format(len(matches)))
            if len(matches) != 0:
                active_links.append(link)
            # Loop through each match to extract the links
            for match in matches:
                print('current match is {}'.format(match))
                current_day = time.localtime()[6]
                try:
                    day = match.find_element(By.XPATH, ".//span[@class='sc-17p8rfo-0 dzNdgZ']").text
                    match_day = match.find_element(By.XPATH, ".//span[@class='sc-17p8rfo-0 dzNdgZ']").text.split(sep=",")[0]
                    
                except:
                    continue
                '''
                if match_day == "Today":
                    match_day = time.localtime()[6]
                elif match_day == "Tomorrow":
                    match_day = time.localtime()[6] + 1
                else:
                    match_day = match_day
                
                print('match day is {}'.format(match_day))
               
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
                
                date_diff = int(match_day) - current_day
                if current_day != 6:
                    if date_diff < 0 or date_diff > 1 :
                        continue
                else:
                    if match_day != 0 and match_day != 6:
                        continue
                    try:
                    amount = int(match.find_element(By.XPATH, ".//div[@class='KambiBC-sandwich-filter_show-more-right-text']").text.split("B", 1)[0])
                except:
                    print('no amount found')
                    continue
                '''
                link = match.find_element(By.XPATH, ".//a").get_attribute('href')
                
                #This condition is't working for this site
                #if link.find('live') == -1 and amount > 40:
                print('link is {}'.format(link))

                matchLinks.append(link)
        
            # Visit each single match to extract the needed data
            for link in matchLinks:
                driver.get(link)
                # sleep for random time to avoid being detected as a bot

                sleep(randint(3, 5))
                # Wait for the data to load
                #wait(".//button[@class='KambiBC-outcomes-list__toggler-toggle-button']")
                
                # Start livescoreBet Scraper
                scrape_teamsName()
                scrape_odds()
                bet_links.append(driver.current_url)
                '''
                From Betcity scraper

                # Scrape the result data
                if not scrape_result():
                    continue
                
                
                
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
                #End betcity scraper
                '''

            # After each competition we create a dataframe with the odds that we have so far collected
            dict_worker = {'Teams': names, 'winner' : winner, 'handicap points' : handicap_points, 'set handicap' : set_handicap, 'over under' : over_under, 'over under points' : over_under_points}

            dataframes[worker] = pd.concat([dataframes[worker], pd.DataFrame.from_dict(dict_worker)])

            with open('active_links.txt', 'w') as f:
                for link in active_links:
                    #write new line
                    f.write(link + "\n")
        
        
        ## Run the Scraper
        start_time = time.time()
        
        with open('livescore_links.txt', 'r') as f:
            links = f.read().split('\n')
        
        amount_links = len(links)
        links_used = 0
        
        for i in range(0, max_workers):
            try:
                executable_path = "C:\webdriver\chromedriver.exe"
                drivers.append(webdriver.Chrome(executable_path=executable_path,options=options))
            except:
                drivers.append(webdriver.Chrome(options=options))
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
            
            output = open('df_liveScore_volly', 'wb')
            pickle.dump(df_betcity, output)
            output.close()
            
            if stop:
                break
            
            time.sleep(1)
        
        for driver in drivers:
            driver.quit()
            
        print("Betcity finished in: %s seconds" % int((time.time() - start_time)))
        
Scraper.__call__(Scraper)