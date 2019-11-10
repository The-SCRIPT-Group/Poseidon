import os
import uuid
from base64 import b64decode
from time import sleep

import pandas as pd
import pytesseract
from dotenv import load_dotenv
from flask import Flask, request
from selenium import webdriver

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'

app = Flask(__name__)


def get_details(username, password, desired_attendance):
    captcha_file = str(uuid.uuid4().hex) + '.png'
    if os.getenv("USE_FIREFOX"):
        options = webdriver.FirefoxOptions
        options.headless = False
        driver = webdriver.Firefox(options=options)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument('--disable-dev-shm-usage') 
        if os.getenv("GOOGLE_CHROME_PATH") is not None:
            options.binary_location = os.getenv("GOOGLE_CHROME_PATH")
        if os.getenv("CHROMEDRIVER_PATH") is not None:
            driver = webdriver.Chrome(chrome_options=options, executable_path=os.getenv("CHROMEDRIVER_PATH"))
        else:
            driver = webdriver.Chrome(chrome_options=options)

    driver.get("https://erp.mitwpu.edu.in/")
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
    table = table.iloc[:, 1:]
    are = table.to_numpy()

    req = desired_attendance
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
    return table.to_json()


@app.route("/api/attendance", methods=["POST"])
def attendance():
    username = request.form["username"]
    password = request.form["password"]
    desired_attendance = 75
    try:
        desired_attendance = float(request.form['desired_attendance'])
    except KeyError:
        pass
    return get_details(username, password, desired_attendance)


if __name__ == "__main__":
    app.run()
