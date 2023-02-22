from selenium import webdriver
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import requests
import urllib.parse
from flask import jsonify, request
import re
import os
from urllib.parse import urlparse
import requests.packages.urllib3
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from selenium.webdriver.chrome.options import Options
requests.packages.urllib3.disable_warnings()


def userBot(filename):
    options = webdriver.ChromeOptions()
    #options = Options()
    options.add_argument('--no-sandbox') #Bypass OS security model
    options.add_argument('--headless')  # 無界面
    options.add_argument('disable-infobars')
    options.add_argument('--start-maximized')  # 最大化
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--disable-dev-shm-usage') #overcome limited resource problems
    options.add_argument('--disable-gpu')  #applicable to windows os only
    options.use_chromium = True

    #driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
    #driver = webdriver.Chrome(options=options)

    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Content-Type": "application/x-www-form-urlencoded", 'Connection': 'close'
    }

    dirname = os.path.dirname(__file__)
    #file = os.path.join(dirname, f'\\XSS-reflected-project\\answers\\{filename}.json') ### for windows dir path
    file = os.path.join(dirname, f'../XSS-reflected-project/answers/{filename}.json') ### for linux dir path
    f = open(file)
    data = json.load(f)
    ans = data['cmd']
    with open('dvwaIP.txt', 'r') as f:
    	dvwaIP = f.read()
    u = f"http://{dvwaIP}/dvwa/vulnerabilities/xss_r/?name="

    # encode url ans
    encode_ans = urllib.parse.quote(ans)
    queryTab = u+encode_ans
    # print(queryTab)

    driver.get(f"http://{dvwaIP}/dvwa")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/div/form/fieldset/input[1]'))).send_keys(Keys.TAB)
    driver.find_element(
        By.XPATH, '/html/body/div/form/fieldset/input[1]').send_keys("admin")
    driver.find_element(
        By.XPATH, '/html/body/div/form/fieldset/input[2]').send_keys("password", Keys.ENTER)
    
    with open('flag.txt', 'r') as f:
    	flag = f.read()
    	
    # Change severity to low
    sleep(1)
    driver.delete_cookie('security')              
    
    driver.get(f"http://{dvwaIP}/dvwa/vulnerabilities")
    #driver.add_cookie({'domain': dvwaIP, 'httpOnly': False, 'name': 'PHPSESSID',
    #                   'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'f7702f72363477ebb9886b66065fa4c8'})
    driver.add_cookie({'domain': dvwaIP, 'httpOnly': False,
                       'name': 'security', 'sameSite': 'Lax',  'path': '/dvwa', 'secure': False, 'value': 'low'})
    driver.add_cookie({'domain': dvwaIP, 'httpOnly': False, 'name': 'security',
                       'path': '/vulnerabilities/xss_r', 'secure': False,  'sameSite': 'Lax', 'value': 'low'})
    driver.add_cookie({'domain': dvwaIP, 'httpOnly': False,
                       'name': 'flag', 'path': '/dvwa', 'sameSite': 'Lax', 'secure': False, 'value': flag})
    newCookie = driver.get_cookies()
    
    #print(newCookie)

    sessionID = newCookie[0]['value']
    # print(sessionID)
    url = f"http://{dvwaIP}/dvwa/login"
    data = "username=admin&password=password&Login=Login"
    try:
        res = requests.post(url, headers=header, data=data, verify=False)
    except requests.exceptions.ConnectionError:
        s = requests.session()
        s.keep_alive = False
        s.status_code = "Connection refused"

    #res.headers.update({"Cookie": "PHPSESSID={}; flag=123".format(sessionID)})

    # Open a new tab
    #driver.execute_script("window.open('');")
    # Switch to the new tab
    #driver.switch_to.window(driver.window_handles[1])
    driver.get(queryTab)
    sleep(1)
    #try:
    #    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
    #        (By.CLASS_NAME, "loginInput"))).send_keys(Keys.TAB)
    #    driver.find_element(
    #        By.XPATH, '/html/body/div/form/fieldset/input[1]').send_keys("admin")
    #    driver.find_element(
    #        By.XPATH, '/html/body/div/form/fieldset/input[2]').send_keys("password", Keys.ENTER)
    #    print("It needs to login twice in the first time.")
    #except:
    #    print("It's no need to login twice.")
    #sleep(1)

    # Send "finish msg" to Attacker Kali server
    try:
        # server uses IP format
        match = re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ans)
        # server uses URL format like ngrok
        ans_search = re.search(
            "(?P<url>https?://[^\s]+)", ans)
        ans_URL = ans_search.group("url")
        if ans_URL is None:
            print(f"There's no URL syntax found in {filename}.'\n")
        elif(len(match) < 0):
            print(f"There's no IP syntax found in {filename}'\n")
        elif(len(match) > 0):
            KaliIPport = match[0]  # <class 'list'>
            print('Kali server\'s IP & port: ', KaliIPport)
            try:
                requests.get(
                    f"http://{KaliIPport}/?msg=finish", headers=header, verify=False, timeout=1)
            except requests.exceptions.ReadTimeout:
                pass
        else:
            ans_domain = urlparse(ans_URL).netloc
            print('Kali server\'s domain: ', ans_domain)
            requests.get(
                f"http://{ans_domain}/?msg=finish", headers=header, verify=False)
    except:
        print(
            f"User {filename}'s Exception: Please check the server connection.\n")

    f.close()
    driver.close()
