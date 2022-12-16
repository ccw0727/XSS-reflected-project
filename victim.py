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
from urllib.parse import urlparse
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


def userBot(filename):
    options = webdriver.ChromeOptions()
    options.add_argument('disable-infobars')
    options.add_argument('--start-maximized')  # 最大化
    options.add_argument('--headless')  # 無界面
    options.use_chromium = True
    driver = webdriver.Chrome(options=options)

    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    f = open(f"{filename}.json")
    data = json.load(f)
    ans = data['cmd']
    metaIP = '192.168.155.129'
    u = f"http://{metaIP}/dvwa/vulnerabilities/xss_r/?name="

    # encode url ans
    encode_ans = urllib.parse.quote(ans)
    queryTab = u+encode_ans
    # print(queryTab)

    driver.get(f"http://{metaIP}/dvwa")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/form/fieldset/input[1]"))).send_keys(Keys.TAB)
    driver.find_element(
        By.XPATH, "/html/body/div[1]/form/fieldset/input[1]").send_keys("admin")
    driver.find_element(
        By.XPATH, "/html/body/div[1]/form/fieldset/input[2]").send_keys("password", Keys.ENTER)

    # Change severity to low
    # 因 /xss_r session會卡在high，所以要先全部刪掉重加。
    sleep(1)
    driver.delete_all_cookies()
    driver.add_cookie({'domain': metaIP, 'httpOnly': False, 'name': 'PHPSESSID',
                       'path': '/', 'secure': False, 'value': 'f7702f72363477ebb9886b66065fa4c8'})
    driver.add_cookie({'domain': metaIP, 'httpOnly': False,
                       'name': 'security', 'path': '/dvwa', 'secure': False, 'value': 'low'})
    driver.add_cookie({'domain': metaIP, 'httpOnly': False, 'name': 'security',
                       'path': '/dvwa/vulnerabilities/xss_r', 'secure': False, 'value': 'low'})
    driver.add_cookie({'domain': metaIP, 'httpOnly': False,
                       'name': 'flag', 'path': '/dvwa', 'secure': False, 'value': 'URSoSmart!'})
    newCookie = driver.get_cookies()
    # print(newCookie)

    sessionID = newCookie[0]['value']
    # print(sessionID)
    url = f"http://{metaIP}/dvwa/login"
    data = "username=admin&password=password&Login=Login"
    res = requests.post(url, headers=header, data=data, verify=False)
    res.headers.update({"Cookie": "PHPSESSID={}; flag=123".format(sessionID)})

    # Open a new tab
    driver.execute_script("window.open('');")
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    driver.get(queryTab)
    sleep(1)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "loginInput"))).send_keys(Keys.TAB)
        driver.find_element(
            By.XPATH, "/html/body/div[1]/form/fieldset/input[1]").send_keys("admin")
        driver.find_element(
            By.XPATH, "/html/body/div[1]/form/fieldset/input[2]").send_keys("password", Keys.ENTER)
        print("It needs to login twice in the first time.")
    except:
        print("It's no need to login twice.")

    sleep(1)

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
