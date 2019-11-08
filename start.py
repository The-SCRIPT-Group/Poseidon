from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image
from io import BytesIO
import pytesseract
from time import sleep
import pandas as pd
import uuid
import os
import getpass
from base64 import b64decode

captcha_file = str(uuid.uuid4().hex)+'.png'
userName = input("Enter Username : ").strip()
password = getpass.getpass(prompt='Enter Password : ', stream=None).strip()
options = Options()
options.headless = False
driver = webdriver.Firefox(options=options) if not os.getenv("USE_CHROME") else webdriver.Chrome()
driver.get("https://erp.mitwpu.edu.in/")

driver.find_element_by_id('txtUserId').send_keys(userName)
driver.find_element_by_id('txtPassword').send_keys(password)
driver.find_element_by_id('chkCheck').click()

while(driver.title!="MainLogin"):
    sleep(1/2)
    img = driver.find_element_by_id('imgCaptcha').get_attribute('src')[22:]
    with open('captcha.png', 'wb') as captcha:
        captcha.write(b64decode(img))
    captcha_text = pytesseract.image_to_string('captcha.png', lang="eng", \
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdef')
    print(captcha_text)
    driver.find_element_by_id('txtCaptcha').send_keys(captcha_text)
    driver.find_element_by_id('btnLogin').click()
    try:
        alert = driver.switch_to.alert
        sleep(2)
        alert.accept()
    except:
        pass

driver.get("https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN")
df = pd.read_html(driver.page_source)
driver.close()

table = df[0]
table = table.iloc[:, 1:]
are = table.to_numpy()

calc_flag = 0
while calc_flag==0:
    req = float(input("What's your target for attendece (75 to 100) : "))
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
        attendence = attended / total * 100
        count=-1
        if attendence >= req:
            while attendence >= req:
                total += 1
                attendence = attended / total * 100
                count +=1
            status = 'you can bunk '+str(count)+' lecture'
            if count != 1:
                status += 's'
        else:
            while attendence <= req:
                total +=1
                attended += 1
                count += 1
                attendence = attended / total * 100
            status = 'You have to attend '+str(count)+' lecture'
            if count != 1:
                status += 's'
    else:
        status = 'You have to attend 1 lecture'
    stat.append(status)
    subcount += 1
table['Status']=stat
table = table.fillna('')
print('')
print(table)
