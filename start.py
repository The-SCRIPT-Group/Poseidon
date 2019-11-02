from selenium import webdriver
from PIL import Image
from io import BytesIO
from pathlib import Path
import pytesseract
import time

userName = str(input("Enter Username : "))
password = str(input("Enter Password : "))

driver = webdriver.Firefox()
driver.get("https://erp.mitwpu.edu.in/")

def getCaptcha():
    element = driver.find_element_by_id('imgCaptcha')
    location = element.location
    size = element.size
    captchaImage = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(captchaImage))
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    im.save(str(Path.home())+"/captcha.png")

    img = Image.open(str(Path.home())+"/captcha.png").convert("L")
    pixel_matrix = img.load()
    for col in range(0, img.height):
        for row in range(0, img.width):
            if pixel_matrix[row, col] != 0:
                pixel_matrix[row, col] = 255
    captcha = str(pytesseract.image_to_string(img, lang="eng", \
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=012'))
    return captcha

driver.find_element_by_id('txtUserId').send_keys(userName)
driver.find_element_by_id('txtPassword').send_keys(password)
driver.find_element_by_id('chkCheck').click()

while(driver.title!="MainLogin"):
    print(driver.title)
    captcha = getCaptcha()
    print(captcha)
    driver.find_element_by_id('txtCaptcha').send_keys(captcha)
    driver.find_element_by_id('btnLogin').click()
    try:
        alert = browser.switch_to_alert
        alert.accept()
        print("alert accepted")
    except:
        print("no alert")
    time.sleep(2)


driver.get("https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN")
