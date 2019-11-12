#!/usr/bin/env python3
import os
from base64 import b64decode
from json import dumps, loads
from uuid import uuid4

import pytesseract as loki
import requests
from pandas import read_html

payload = {
    "__LASTFOCUS": "",
    "__VIEWSTATE": "/wEPDwULLTE5ODI5MDAxMzMPFgIeDkxPR0lOX0JBU0VEX09OZRYCAgEPZBYCAgMPZBYCZg9kFgYCDw9kFgICAQ8QZA8WAWYWARAFA1dQVQUDV1BVZxYBZmQCEw8PFgIeB0VuYWJsZWRnZGQCGQ9kFgICAQ8QZGQWAWZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQhjaGtDaGVja+/IxmsP3IoCwjVYbsmN45kfOjGivX4s7e93RISZwDsW",
    "__EVENTTARGET": "btnLogin",
    "__EVENTARGUMENT": "",
    "chkCheck": "on",
    "__VIEWSTATEGENERATOR": "B8B84CAE",
    "hdnMsg": "",
    "hdtype": "",
    "hdloginid": "",
    "hdnFlag": "R",
}

headers = {"Content-Type": "application/json; charset=utf-8"}


def attendance(username, password):
    captcha_file = str(uuid4().hex) + ".png"
    boo = True

    with requests.session() as s:
        while boo:
            try:
                data = s.post(
                    "https://erp.mitwpu.edu.in/AdminLogin.aspx/funGenerateCaptcha",
                    headers=headers,
                ).text
                img = loads(data)["d"]
                with open(captcha_file, "wb") as captcha:
                    captcha.write(b64decode(img))
                captcha_text = loki.image_to_string(captcha_file,
                                                    config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdef")
                if captcha_text == '':
                    raise ValueError()
                print(f"Captcha is {captcha_text}")

                payload['txtUserId'] = username
                payload["txtPassword"] = password
                payload["txtCaptcha"] = captcha_text

                # headers for logging in
                headers["X-MicrosoftAjax"] = "Delta=true"
                headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
                headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                                        "Chrome/77.0.3865.120 Safari/537.36"
                # api call to log in
                response = s.post(
                    "https://erp.mitwpu.edu.in/AdminLogin.aspx", headers=headers, data=payload
                )
                print(response)
                table = read_html(s.get(
                    "https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN"
                ).text)[0]

                boo = False

            except ValueError:
                print('retrying...')

        os.remove(captcha_file)

    data = list()

    for i in range(len(table['SrNo'])):
        if str(table['SrNo'][i]) == 'nan':
            break
        else:
            data.append(
                {
                    'subject': str(table['Subject'][i]),
                    'type': str(table['Subject Type'][i]),
                    'present': int(table['Present'][i]),
                    'total': int(table['Total Period'][i])
                }
            )

    return dumps(data)
