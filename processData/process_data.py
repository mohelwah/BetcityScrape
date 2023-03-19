#import subprocess
import create_log as cl
import pandas as pd
import paramiko
import pickle
import time
from fuzzywuzzy import process, fuzz

logging.getLogger().setLevel(logging.ERROR)

#from sympy import symbols, Eq, solve
valuebet_low= 6.0
def run():
    # Set options for dataframe so it can contain all data
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    
    # Load to the binary data into panda dataframes to read from
    df_betcity = pickle.load(open('df_betcity', 'rb'))
    df_livescorebet = pickle.load(open('df_livescorebet', 'rb'))
    '''
    df_toto = pickle.load(open('df_toto', 'rb'))
    df_zebet = pickle.load(open('df_zebet', 'rb'))
    df_hollandcasino = pickle.load(open('df_hollandcasino', 'rb'))
    df_circus = pickle.load(open('df_circus', 'rb'))
    df_bingoal = pickle.load(open('df_bingoal', 'rb'))
    df_pinnacle = pickle.load(open('df_pinnacle', 'rb'))
    '''
    # List containing the names of the sites we are scraping
    names = ["livescorebet", "betcity"]#"betcity", "circus", "bingoal", "hollandcasino", "toto"]
    
    # This list contains all the dataframes corresponding to a site has the same order as names[]
    dataframes = [df_betcity, df_livescorebet] #, df_betcity, df_circus, df_bingoal, df_hollandcasino, df_toto]

    # This list conatains the names of all columns in wich a surebet can be found
    column_names = ['beide_teams_scoren', 'beide_teams_scoren_1e', 'beide_teams_scoren_2e', 'over_under', 'over_under_1e', 'over_under_2e', 'handicap', 'result', 'dubbele_kans']
    # with just binary odds
    column_names_type_1 = ['beide_teams_scoren', 'beide_teams_scoren_1e', 'beide_teams_scoren_2e']
    
    # Binary odds with an extra number for the required amount of goals
    column_names_type_2 = ['over_under', 'over_under_1e', 'over_under_2e', 'handicap']
    
    logbook = open('surebet_logbook.txt', 'a+', encoding='utf-8')
    valuebet_logbook = open('valuebet_logbook.txt', 'a+', encoding='utf-8')
    output = open('surebets.php', 'w', encoding='utf-8')
    
    def format1(str):
        str = str.replace(",", ".")
        return str.split("\n")
    
    def format2(str):
        str = str[:-1]# Remove the last '|' of a string
        str = str.replace(",", ".")
        # Create a list wit elements of the form goals\nodd1\nodd2
        odds_per_match = str.split("|")
        # Create a list of lists
        for n in range(len(odds_per_match)):
            odds_per_match[n] = odds_per_match[n].split("\n")
        return odds_per_match
    
    def format3(string, num):
        if 'over_under' in string:
            string = string.split(' ')
            goals = string[1]
            try:
                half = string[0].split('_')[2]
            except:
                half = ''
                
            if num == 0: 
                return str('Meer dan ' + goals + ' ' + half)
            else: return str('Minder dan ' + goals + ' ' + half)
            
        elif 'beide_teams_scoren' in string:
            try:
                if num == 0:
                    return str('Beide scoren ' + string.split('_')[3] + ' - Ja')
                else: return str('Beide scoren ' + string.split('_')[3] + ' - Nee')
            except:
                if num == 0:
                    return str('Beide scoren - Ja')
                else: return str('Beide scoren - Nee')
                
            
        elif 'handicap' in string:
            goals = string.split(" ")[1]
            if num == 0:
                return str('H(' + goals + ')')
            else: 
                if '-' in goals:
                    return str('H(' + goals + ')')
                else: return str('H(-' + goals + ')')
        else:
            if '0' in string:
                if 'result - dubbele kans' in string:
                    if num == 0: 
                        return '1'
                    else: return 'X2'
                else:
                    if num == 0: 
                        return '1X'
                    else: return '2'
            elif '1' in string:
                if 'result - dubbele kans' in string:
                    if num == 0: 
                        return 'X'
                    else: return '12'
                else:
                    if num == 0: 
                        return '12'
                    else: return 'X'
            else:
                if 'result - dubbele kans' in string:
                    if num == 0: 
                        return '2'
                    else: return '1X'
                else:
                    if num == 0: 
                        return 'X2'
                    else: return '1'
                    
    
    def print_surebet(odds_right, odds_wrong, site1, site2, matches1, matches2, subbet_name, link1, link2):
        subbets = format3(subbet_name)
        percentage = str(100*(1-(1/float(odds_right) + 1/float(odds_wrong))))[:5]
        localtime = time.localtime()
        names1 = matches1.split("\n")
        names2 = matches2.split("\n")
        print("SUREBET_FOUND PROFIT: " + str(percentage)[:4] + "%")
        print(link1 + ' ' + link2)
        
        logbook.seek(0)
        surebets = logbook.read()
        
        log = "SUBBET: " + subbets[0] + ' ; ' + subbets[1] + '\n' + "PROFIT: " + str(percentage)[:4] + "%"+ '\n' + "MATCH " +  site1 + ": " + names1[0] + " - " + names1[1]+ '\n' + "MATCH " +  site2 + ": " + names2[0] + " - " + names2[1]+ '\n' + "ODDS on " + site1 + " are: " + odds_right+ '\n' + "ODDS on " + site2 + " are: " + odds_wrong + '\n\n'
            
        if log not in surebets:
            log = "SUREBET_FOUND on: " + str(localtime[2]) + '/' + str(localtime[1]) + '/' + str(localtime[0]) + ' at: ' + str(localtime[3]) + ':' + str(localtime[4]) + ':' + str(localtime[5]) + '\n' + log
            cl.post_twitter("Surebet gevonden!\nSubbet: " + subbets[0] + ' ; ' + subbets[1] + "\nProfit: " + str(percentage)[:4] + '%\n' + site1 + " odds: " + odds_right + "\nTeams: " + names1[0] + " - " + names1[1]+ "\nLink: " + link1 + "\n" + site2 + " odds: " + odds_wrong + "\nTeams: " + names2[0] + " - " + names2[1]+ "\nLink: " + link2)
        
        logbook.write(log)
        
        output.write('\tgenerate_bet( "' + str(percentage) + '", "", "voetbal", "'
                 + str(names1[0]) + '", "' + str(names1[1]) + '", "' + str(site1) + '", "' + str(subbets[0]) + '", "'
                 + str(odds_right) + '", "' + str(site2) + '", "' + str(subbets[1]) + '", "' + str(odds_wrong) + '", "' 
                 + str(link1) + '", "' + str(link2) + '" );\n')
        
    def print_valuebet(odds_high, odds_low, site1, site2, matches1, matches2, subbet_name, link1, link2, num):
        subbets = format3(subbet_name, num)
        percentage = str((odds_high/(odds_low*1.03))*100 - 100)[:5]
        localtime = time.localtime()
        names1 = matches1.split("\n")
        # names2 = matches2.split("\n")
        # print("VALUEBET FOUND, PROFIT: " + percentage + "%")
        # print(link1 + ' ' + link2)
        print("VALUEBET: " + subbets + '\n' + "OVERVALUE: " + str(percentage)[:4] + "%"+ '\n' + "MATCH " +  site1 + ": " + names1[0] + " - " + names1[1] + '\n' + "ODDS on " + site1 + " are: " + str(odds_high))
        print(link1, link2)
        
        valuebet_logbook.seek(0)
        valuebets = valuebet_logbook.read()
        
        log = "VALUEBET: " + subbets + '\n' + "OVERVALUE: " + str(percentage)[:4] + "%"+ '\n' + "MATCH " +  site1 + ": " + names1[0] + " - " + names1[1] + '\n' + "ODDS on " + site1 + " are: " + str(odds_high)
            
        if log not in valuebets:
            log = "VALUEBET_FOUND on: " + str(localtime[2]) + '/' + str(localtime[1]) + '/' + str(localtime[0]) + ' at: ' + str(localtime[3]) + ':' + str(localtime[4]) + ':' + str(localtime[5]) + '\n' + log
            cl.post_twitter("Valuebet gevonden!\nSubbet: " + subbets + '\n' + "Overvalue: " + str(percentage)[:4] + "%"+ '\n'+ "Kans op winnen: "+ str(1/odds_low)[:4] + '\n' + site1 + " odds: " + str(odds_high) + '\n' + 'Teams: ' + names1[0] + " - " + names1[1] + "\nLink: " + link1 )
            valuebet_logbook.write(log)
        
    
    def find_result_and_dc_surebet(merged, df1_name, df2_name, matches1, matches2):
        result_site1 = merged['result_x'].tolist()
        result_site2 = merged['result_y'].tolist()
        dubbele_kans_site1 = merged['dubbele_kans_x'].tolist()
        dubbele_kans_site2 = merged['dubbele_kans_y'].tolist()
        links_site1 = merged['bet_links_x'].tolist()
        links_site2 = merged['bet_links_y'].tolist()
        for n in range(len(matches1)):
            if '(V)' in matches1[n] or '(V)' in matches2[n]:
                continue
            if result_site1[n] == 0 or result_site2[n] == 0 or dubbele_kans_site1[n] == 0 or dubbele_kans_site2[n] == 0:
                    continue
            result_odds_1 = format1(result_site1[n])
            result_odds_2 = format1(result_site2[n])
            dubbele_kans_odds_1 = format1(dubbele_kans_site1[n])
            dubbele_kans_odds_2 = format1(dubbele_kans_site2[n])
            for i in range(3):
                if ((1 / float(result_odds_1[i]) + (1 / float(dubbele_kans_odds_2[2-i]))) < 1):
                    print_surebet(result_odds_1[i], dubbele_kans_odds_2[2-i], df1_name, df2_name, matches1[n], matches2[n], "result - dubbele kans" + str(i), links_site1[n], links_site2[n])
                if ((1 / float(result_odds_2[i]) + (1 / float(dubbele_kans_odds_1[2-i]))) < 1):
                    print_surebet(result_odds_2[i], dubbele_kans_odds_1[2-i], df1_name, df2_name, matches1[n], matches2[n], "dubbele kans - result" + str(i), links_site1[n], links_site2[n])
    
    def find_result_and_dc_valuebet(merged, df1_name, df2_name, matches1, matches2):
        result_site1 = merged['result_x'].tolist()
        result_site2 = merged['result_y'].tolist()
        dubbele_kans_site1 = merged['dubbele_kans_x'].tolist()
        dubbele_kans_site2 = merged['dubbele_kans_y'].tolist()
        links_site1 = merged['bet_links_x'].tolist()
        links_site2 = merged['bet_links_y'].tolist()
        for n in range(len(matches1)):
            if '(V)' in matches1[n] or '(V)' in matches2[n]:
                continue
            if result_site1[n] == 0 or result_site2[n] == 0 or dubbele_kans_site1[n] == 0 or dubbele_kans_site2[n] == 0:
                    continue
            result_odds_1 = format1(result_site1[n])
            result_odds_2 = format1(result_site2[n])
            dubbele_kans_odds_1 = format1(dubbele_kans_site1[n])
            dubbele_kans_odds_2 = format1(dubbele_kans_site2[n])
            for i in range(3):
                # Valuebet odd 1
                if float(result_odds_1[i]) < 2.9 and float(result_odds_2[i]) < 2.9 and float(result_odds_1[i]) > 1.2 and float(result_odds_2[i]) > 1.2:
                    if(((float(result_odds_1[i])/(float(result_odds_2[i])*1.03))*100 - 100) > valuebet_low):
                        print_valuebet(float(result_odds_1[i]), float(result_odds_2[i]), df1_name, df2_name, matches1[n], matches2[n], "result - dubbele kans" + str(i), links_site1[n], links_site2[n], 0)
                #Valuebet odd 2
                if float(dubbele_kans_odds_1[i]) < 2.9 and float(dubbele_kans_odds_2[i]) < 2.9 and float(dubbele_kans_odds_1[i]) > 1.2 and float(dubbele_kans_odds_2[i]) > 1.2:
                    if(((float(dubbele_kans_odds_1[i])/(float(dubbele_kans_odds_2[i])*1.03))*100 - 100) > valuebet_low):
                        print_valuebet(float(dubbele_kans_odds_1[i]), float(dubbele_kans_odds_2[i]), df1_name, df2_name, matches1[n], matches2[n], "dubbele kans - result" + str(i), links_site1[n], links_site2[n], 1)
                    
    
    
    def find_binary_subbet(df1, df2, df1_name, df2_name):
        # First merge two dataframes based on team-names
        teams_site_2 = df2['Teams'].tolist()
        df1[['Teams_site_2', 'Fuzscore']] = df1['Teams'].apply(lambda x: process.extractOne(x, teams_site_2, scorer=fuzz.partial_ratio)).apply(pd.Series)
        merged = pd.merge(df1, df2, left_on='Teams_site_2', right_on='Teams')
        # Select only the rows where the teamnames are much alike
        merged = merged[merged['Fuzscore'] >= 90]
        # All of the matches as a list
        matches1 = merged['Teams_x'].tolist()
        matches2 = merged['Teams_site_2'].tolist()
        # Find the surebets between result and dubbele kans
        find_result_and_dc_surebet(merged, df1_name, df2_name, matches1, matches2)
    
        # Find surebets in subbets that consist of just the two odds
        for subbets in column_names_type_1:
            # Get lists of the odds for every match from both sites
            odds_list_1 = merged[subbets + '_x'].tolist()
            odds_list_2 = merged[subbets + '_y'].tolist()
            links_site1 = merged['bet_links_x'].tolist()
            links_site2 = merged['bet_links_y'].tolist()
            # Go through both lists simultaneously
            for n, odds in enumerate(odds_list_1):
                if '(V)' in matches1[n] or '(V)' in matches2[n]:
                    continue
                # Check if there were odds
                if(odds == 0) or odds_list_2[n] == 0:
                    continue
                # Format the odds so you can find surebets
                odds_site_1 = format1(odds)
                odds_site_2 = format1(odds_list_2[n])
                
                if odds_site_1[1] == '' or odds_site_1[0] == '' or odds_site_2[0] == '' or odds_site_2[1] == '':
                    continue
                
                # site 1 - site 2
                if((1/float(odds_site_1[0])) + (1/float(odds_site_2[1])) < 1):
                    print_surebet(odds_site_1[0], odds_site_2[1], df1_name, df2_name, matches1[n], matches2[n], subbets, links_site1[n], links_site2[n])
                # site 2 - site 1
                if((1/float(odds_site_1[1])) + (1/float(odds_site_2[0])) < 1):
                    print_surebet(odds_site_2[0], odds_site_1[1], df2_name, df1_name, matches1[n], matches2[n], subbets, links_site1[n], links_site2[n])
                
            # Find surebets in subbets that have a goal added as parameter
            for subbets in column_names_type_2:
                odds_list_1 = merged[subbets + '_x'].tolist()
                odds_list_2 = merged[subbets + '_y'].tolist()
                links_site1 = merged['bet_links_x'].tolist()
                links_site2 = merged['bet_links_y'].tolist()
                # Go through both lists simultaneously
                for n, odds in enumerate(odds_list_1):
                    if '(V)' in matches1[n] or '(V)' in matches2[n]:
                        continue
                    if(odds == 0 or odds_list_2[n] == 0):
                        continue
                    # Create list of lists
                    extra_odds_1 = format2(odds)
                    extra_odds_2 = format2(odds_list_2[n])
                    # Search for the same subbets on both sites based on the number of goals needed
                    for extra_odd_1 in extra_odds_1:
                        for extra_odd_2 in extra_odds_2:
                            goals = extra_odd_1[0]
                            # Match subbet
                            if(extra_odd_1[0] == extra_odd_2[0]):
                                try:
                                    if extra_odd_1[1] == '' or extra_odd_1[2] == '' or extra_odd_2[1] == '' or extra_odd_2[2] == '':
                                        continue
                                except:
                                    continue
                                # If found, the second and third list entry contain het rigth and wrong odds
                                if((1/float(extra_odd_1[1])) + (1/float(extra_odd_2[2])) < 1):
                                    print_surebet(extra_odd_1[1], extra_odd_2[2], df1_name, df2_name, matches1[n], matches2[n], subbets + ' ' + goals, links_site1[n], links_site2[n])
                                if((1/float(extra_odd_1[2])) + (1/float(extra_odd_2[1])) < 1):
                                    print_surebet(extra_odd_2[1], extra_odd_1[2], df2_name, df1_name, matches1[n], matches2[n], subbets + ' ' + goals, links_site1[n], links_site2[n])
        
                        
    def find_binary_valuebet(df1, df2, df1_name, df2_name):
        # First merge two dataframes based on team-names
        teams_site_2 = df2['Teams'].tolist()
        df1[['Teams_site_2', 'Fuzscore']] = df1['Teams'].apply(lambda x: process.extractOne(x, teams_site_2, scorer=fuzz.partial_ratio)).apply(pd.Series)
        merged = pd.merge(df1, df2, left_on='Teams_site_2', right_on='Teams')
        # Select only the rows where the teamnames are much alike
        merged = merged[merged['Fuzscore'] >= 90]
        # All of the matches as a list
        matches1 = merged['Teams_x'].tolist()
        matches2 = merged['Teams_site_2'].tolist()
        # Find the surebets between result and dubbele kans
        find_result_and_dc_valuebet(merged, df1_name, df2_name, matches1, matches2)
    
        # Find surebets in subbets that consist of just the two odds
        for subbets in column_names_type_1:
            # Get lists of the odds for every match from both sites
            odds_list_1 = merged[subbets + '_x'].tolist()
            odds_list_2 = merged[subbets + '_y'].tolist()
            links_site1 = merged['bet_links_x'].tolist()
            links_site2 = merged['bet_links_y'].tolist()
            # Go through both lists simultaneously
            for n, odds in enumerate(odds_list_1):
                if '(V)' in matches1[n] or '(V)' in matches2[n]:
                    continue
                # Check if there were odds
                if(odds == 0) or odds_list_2[n] == 0:
                    continue
                # Format the odds so you can find surebets
                odds_site_1 = format1(odds)
                odds_site_2 = format1(odds_list_2[n])
                
                if odds_site_1[1] == '' or odds_site_1[0] == '' or odds_site_2[0] == '' or odds_site_2[1] == '':
                    continue
                
                # Valuebet odd 1
                if float(odds_site_1[0]) < 2.9 and float(odds_site_2[0]) < 2.9 and float(odds_site_1[0]) > 1.2 and float(odds_site_2[0]) > 1.2:
                    if(((float(odds_site_1[0])/(float(odds_site_2[0])*1.03))*100 - 100) > valuebet_low):
                        print_valuebet(float(odds_site_1[0]), float(odds_site_2[0]), df1_name, df2_name, matches1[n], matches2[n], subbets, links_site1[n], links_site2[n], 0)
                
                #Valuebet odd 2
                if float(odds_site_1[1]) < 2.9 and float(odds_site_2[1]) < 2.9 and float(odds_site_1[1]) > 1.2 and float(odds_site_2[1]) > 1.2:
                    if(((float(odds_site_1[1])/(float(odds_site_2[1])*1.03))*100 - 100) > valuebet_low):
                        print_valuebet(float(odds_site_1[1]), float(odds_site_2[1]), df1_name, df2_name, matches1[n], matches2[n], subbets, links_site1[n], links_site2[n], 1)
    
        # Find surebets in subbets that have a goal added as parameter
        for subbets in column_names_type_2:
            odds_list_1 = merged[subbets + '_x'].tolist()
            odds_list_2 = merged[subbets + '_y'].tolist()
            links_site1 = merged['bet_links_x'].tolist()
            links_site2 = merged['bet_links_y'].tolist()
            # Go through both lists simultaneously
            for n, odds in enumerate(odds_list_1):
                if '(V)' in matches1[n] or '(V)' in matches2[n]:
                    continue
                if(odds == 0 or odds_list_2[n] == 0):
                    continue
                # Create list of lists
                extra_odds_1 = format2(odds)
                extra_odds_2 = format2(odds_list_2[n])
                # Search for the same subbets on both sites based on the number of goals needed
                for extra_odd_1 in extra_odds_1:
                    for extra_odd_2 in extra_odds_2:
                        goals = extra_odd_1[0]
                        # Match subbet
                        if(extra_odd_1[0] == extra_odd_2[0]):
                            try:
                                if extra_odd_1[1] == '' or extra_odd_1[2] == '' or extra_odd_2[1] == '' or extra_odd_2[2] == '':
                                    continue
                            except:
                                continue
                                
                            # Valuebet odd 1
                            if float(extra_odd_1[1]) < 2.9 and float(extra_odd_2[1]) < 2.9 and float(extra_odd_1[1]) > 1.2 and float(extra_odd_2[1]) > 1.2:
                                if(((float(extra_odd_1[1])/(float(extra_odd_2[1])*1.03))*100 - 100) > valuebet_low):
                                    print_valuebet(float(extra_odd_1[1]), float(extra_odd_2[1]), df1_name, df2_name, matches1[n], matches2[n], subbets + ' ' + goals, links_site1[n], links_site2[n], 0)
                            
                            # Valuebet odd 2
                            if float(extra_odd_1[2]) < 2.9 and float(extra_odd_2[2]) < 2.9 and float(extra_odd_1[2]) > 1.2 and float(extra_odd_2[2]) > 1.2:
                                if(((float(extra_odd_1[2])/(float(extra_odd_2[2])*1.03))*100 - 100) > valuebet_low):
                                    print_valuebet(float(extra_odd_1[2]), float(extra_odd_2[2]), df1_name, df2_name, matches1[n], matches2[n], subbets + ' ' + goals, links_site1[n], links_site2[n], 1)
                                    
    
    output.write('<?php\n')
    # print_surebet('2.5', '2.5', 'toto', 'zebet', 'Ajax\nFeyenoord', 'Ajax\nFeyenoord', 'result - dubbele kans2') # TEST
    # for n in range(len(dataframes)):
    #     for i in range(n, len(dataframes)):
    #         if(dataframes[n] is not dataframes[i]) and not dataframes[i].empty and not dataframes[n].empty:
    #             find_binary_subbet(dataframes[n], dataframes[i], names[n], names[i])
    
    for n in range(len(dataframes)):
        if n == 0:
            continue
        find_binary_valuebet(dataframes[n], dataframes[0], names[n], names[0])
        
    output.write('?>')
    output.close()
    
    # Open a transport
    # host,port = "ssh.strato.com",22
    # transport = paramiko.Transport((host,port))
    
    # # Auth    
    # username,password = "sftp_server@alphabetting.nl","FAhfQtCPk@U!38X"
    # transport.connect(None,username,password)
    
    # # Go!    
    # sftp = paramiko.SFTPClient.from_transport(transport)
    
    # # Upload
    # filepath = "php/surebets/voetbal_surebets.php"
    # localpath = "surebets.php"
    # sftp.put(localpath,filepath)
    
    # # Close
    # if sftp: sftp.close()
    # if transport: transport.close()
       
# run()
    