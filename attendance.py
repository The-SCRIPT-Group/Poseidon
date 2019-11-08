import getpass
import os
import uuid
from base64 import b64decode
from time import sleep

import pandas as pd
import pytesseract
from dotenv import load_dotenv
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver import firefox, chrome

load_dotenv()

app = Flask(__name__)

captcha_file = str(uuid.uuid4().hex) + '.png'
username, password = os.getenv("erp_user"), os.getenv("erp_pass")
if username is None:
    username = input("Enter Username : ").strip()
if password is None:
    password = getpass.getpass(prompt='Enter Password : ', stream=None)


def get_details(username, password):
    if os.getenv("USE_CHROME"):
        options = chrome.options.Options()
        options.headless = False
        driver = webdriver.Chrome(options=options)
    else:
        options = firefox.options.Options()
        options.headless = False
        driver = webdriver.Firefox(options=options)

    driver.get("https://erp.mitwpu.edu.in/", )
    driver.execute_script('document.getElementsByTagName("body")[0].removeAttribute("style")')

    driver.find_element_by_id('txtUserId').send_keys(username)
    driver.find_element_by_id('txtPassword').send_keys(password)
    driver.find_element_by_id('chkCheck').click()

    while driver.title != "MainLogin":
        sleep(1 / 2)
        img = driver.find_element_by_id('imgCaptcha').get_attribute('src')[22:]
        with open(captcha_file, 'wb') as captcha:
            captcha.write(b64decode(img))
        captcha_text = pytesseract.image_to_string(captcha_file,
                                                   config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdef")
        print(captcha_text)
        driver.find_element_by_id('txtCaptcha').send_keys(captcha_text)
        driver.find_element_by_id('btnLogin').click()
        try:
            alert = driver.switch_to.alert
            sleep(2)
            alert.accept()
        except:
            sleep(5)

    driver.get("https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN")
    df = pd.read_html(driver.page_source)
    driver.close()
    os.remove(captcha_file)

    table = df[0]
    return table.to_json()
    table = table.iloc[:, 1:]
    are = table.to_numpy()

    calc_flag = 0
    while calc_flag == 0:
        req = float(input("What's your target for attendance (75 to 100) : "))
        if req < 75 or req > 100:
            print('Read question carefully')
        else:
            calc_flag = 1

    subcount = 0
    stat = []
    for sub in are:
        if sub[3] != 0:
            attended = sub[2]
            total = sub[3]
            attendance = attended / total * 100
            count = -1
            if attendance >= req:
                while attendance >= req:
                    total += 1
                    attendance = attended / total * 100
                    count += 1
                status = 'you can bunk ' + str(count) + ' lecture'
                if count != 1:
                    status += 's'
            else:
                while attendance <= req:
                    total += 1
                    attended += 1
                    count += 1
                    attendance = attended / total * 100
                status = 'You have to attend ' + str(count) + ' lecture'
                if count != 1:
                    status += 's'
        else:
            status = 'You have to attend 1 lecture'
        stat.append(status)
        subcount += 1
    table['Status'] = stat
    table = table.fillna('')
    print('')
    print(table)

    print(table.to_json())


@app.route("/api/attendance", methods=["POST"])
def attendance():
    username = request.form["username"]
    password = request.form["password"]
    return get_details(username, password)

if __name__ == "__main__":
    app.run()
