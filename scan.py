# import pandas as pd 
import requests
from requests_html import HTMLSession
from collections import Counter
from urllib.parse import urlparse

user_agent=None
# user agent so it doesn't show as python and get blocked, set global for request that need to allow for redirects
def get(websiteToScan):
    global user_agent
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    }
    return requests.get(websiteToScan, allow_redirects=False, headers=user_agent)


# Begin scan
def scan(df, websiteToScan):
    
    print(df, websiteToScan)
    # Check the input for HTTP or HTTPS and then remove it, if nothing is found assume HTTP
    if websiteToScan.startswith('http://'):
        proto = 'http://'
        websiteToScan = websiteToScan[7:]
    elif websiteToScan.startswith('https://'):
        proto = 'https://'
        websiteToScan = websiteToScan[8:]
    else:
        proto = 'http://'
    # Check the input for an ending / and remove it if found
    if websiteToScan.endswith('/'):
        websiteToScan = websiteToScan.strip('/')
    # Combine the protocol and site
    websiteToScan = proto + websiteToScan
    # Check to see if the site is online
    print ("Checking to see if the site is online...")
    try:
        onlineCheck = get(websiteToScan)
    except requests.exceptions.ConnectionError as ex:
        print (f"{websiteToScan} appears to be offline.")
    else:
        if onlineCheck.status_code == 200 or onlineCheck.status_code == 301 or onlineCheck.status_code == 302:
            print (f"{websiteToScan} appears to be online.")
            print ("Beginning scan...")
            print ("Checking to see if the site is redirecting...")
            redirectCheck = requests.get(websiteToScan, headers=user_agent)
            if len(redirectCheck.history) > 0:
                if '301' in str(redirectCheck.history[0]) or '302' in str(redirectCheck.history[0]):
                    print ("[!] The site entered appears to be redirecting, please verify the destination site to ensure accurate results!")
                    print (f"It appears the site is redirecting to {redirectCheck.url}")
            elif 'meta http-equiv="REFRESH"' in redirectCheck.text:
                print ("The site entered appears to be redirecting, please verify the destination site to ensure accurate results!")
            else:
                print ("Site does not appear to be redirecting...")
            for header in onlineCheck.headers:
                try:
                    print (f"{header}: {onlineCheck.headers[header]}")
                except Exception as ex:
                    print (f"Error: {ex.message}")
        else:
            print (f"{websiteToScan} appears to be online but returned a {str(onlineCheck.status_code)} error.")
            df.at[websiteToScan,'Status'] = 'No'
            exit()
        print ("Attempting to get the HTTP headers...")
        for header in onlineCheck.headers:
            try:
                print (f"{header}: {onlineCheck.headers[header]}")
            except Exception as ex:
                print (f"Error: {ex.message}")
        ####################################################
        # WordPress Scans
        ####################################################
        # Use requests.get allowing redirects otherwise will always fail
        wpLoginCheck=requests.get(websiteToScan + '/wp-login.php', headers=user_agent)
        if wpLoginCheck.status_code == 200:
            return 'Yes'
        else:
            return'No'

        df['Status'] = df.apply(wpLoginCheck, axis=1)
        df.to_csv('updated.csv', index=False)