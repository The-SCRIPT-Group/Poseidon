#!/usr/bin/env python3
import os
from base64 import b64decode
from json import dumps, loads
from re import search, DOTALL
from uuid import uuid4

import pytesseract as loki
import requests
from pandas import read_html

payload = {
    "__VIEWSTATE": "/wEPDwULLTE5ODI5MDAxMzMPFgIeDkxPR0lOX0JBU0VEX09OZRYCAgEPZBYCAgMPZBYCZg9kFgYCDw9kFgICAQ8QZA8WAWYWARAFA1dQVQUDV1BVZxYBZmQCEw8PFgIeB0VuYWJsZWRnZGQCGQ9kFgICAQ8QZGQWAWZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQhjaGtDaGVja+/IxmsP3IoCwjVYbsmN45kfOjGivX4s7e93RISZwDsW",
    "__EVENTTARGET": "btnLogin",
    "chkCheck": "on",
    "__VIEWSTATEGENERATOR": "B8B84CAE",
}


def attendance(username, password):
    captcha_file = str(uuid4().hex) + ".png"
    count = 0

    while True:
        with requests.session() as s:
            captcha_text = ""
            while captcha_text == "":
                headers = {"Content-Type": "application/json; charset=utf-8"}
                data = s.post(
                    "https://erp.mitwpu.edu.in/AdminLogin.aspx/funGenerateCaptcha",
                    headers=headers,
                ).text
                img = loads(data)["d"]
                with open(captcha_file, "wb") as captcha:
                    captcha.write(b64decode(img))
                captcha_text = loki.image_to_string(captcha_file,
                                                    config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdef")
            os.remove(captcha_file)

            payload['txtUserId'] = username
            payload["txtPassword"] = password
            payload["txtCaptcha"] = captcha_text

            # Headers for logging in and fetching the data
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
            headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                                    "Chrome/77.0.3865.120 Safari/537.36"
            # POST request to log in
            s.post(
                "https://erp.mitwpu.edu.in/AdminLogin.aspx", headers=headers, data=payload
            )

            data = s.get(
                "https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN"
            ).text
            title = search('(?<=<title>).+?(?=</title>)', data, DOTALL).group().strip()
            if title == 'Self Attendance Report':
                return data
            count += 1
            if title == 'LOGIN' and count > 5:
                return "Error"


def attendance_json(username, password):
    while True:
        attendance_data = attendance(username, password)
        if attendance_data == "Error":
            return dumps({"status": "error"})
        try:
            table = read_html(attendance_data)[0]
        except ValueError:
            continue
        break

    data = list()

    for i in range(len(table['SrNo'])):
        if str(table['SrNo'][i]) == 'nan':
            break
        elif i > 0 and str(table['Subject'][i]) == str(table['Subject'][i - 1]):
            data[-1][str(table['Subject Type'][i].lower()) + '_present'] = int(table['Present'][i])
            data[-1][str(table['Subject Type'][i].lower()) + '_total'] = int(table['Total Period'][i])
            data[-1][str(table['Subject Type'][i].lower()) + '_missed'] = int(table['Total Period'][i]) - int(
                table['Present'][i])
            data[-1][str(table['Subject Type'][i].lower()) + '_percent'] = round(
                ((int(table['Present'][i])) / int(table['Total Period'][i])) * 100, 2)
        else:
            data.append(
                {
                    'subject': str(table['Subject'][i]),
                    str(table['Subject Type'][i].lower()) + '_present': int(table['Present'][i]),
                    str(table['Subject Type'][i].lower()) + '_total': int(table['Total Period'][i]),
                    str(table['Subject Type'][i].lower()) + '_missed': int(table['Total Period'][i]) - int(
                        table['Present'][i]),
                    str(table['Subject Type'][i].lower()) + '_percent': round(
                        ((int(table['Present'][i])) / int(table['Total Period'][i])) * 100, 2)
                }
            )

    return dumps(data)
