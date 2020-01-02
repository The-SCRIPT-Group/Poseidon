#!/usr/bin/env python3
import os
from base64 import b64decode
from json import dumps, loads
from re import search, DOTALL
from uuid import uuid4

import pytesseract as loki
import requests
from bs4 import BeautifulSoup

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
                response = s.post(
                    "https://erp.mitwpu.edu.in/AdminLogin.aspx/funGenerateCaptcha",
                    headers=headers,
                )
                if response.status_code != 200:
                    return "ERP is down!"
                data = response.text
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
            count += 1
            if "AdminLogin.aspx" in data and count < 5:
                continue
            if title == 'Self Attendance Report':
                return data
            if count > 5:
                return "Error"


def get_attendance(data):
    soup = BeautifulSoup(data)
    tables = soup.findAll("table")
    if len(tables) != 4:
        return "Error"
    table = tables[1]
    titles = [h.text for h in table.find("thead").find('tr')]
    body = table.find('tbody')
    ret = []
    for row in body.findAll('tr'):
        attendance = {}
        if len(row) == 6:
            for element in range(len(row.findAll('td'))):
                attendance[titles[element]] = row.findAll('td')[element].text.strip()
        elif len(row) == 4:
            attendance[titles[0]] = ret[-1][titles[0]]
            attendance[titles[1]] = ret[-1][titles[1]]
            for element in range(len(row.findAll('td'))):
                attendance[titles[element + 2]] = row.findAll('td')[element].text.strip()
        else:
            continue
        ret.append(attendance)
    return ret


def attendance_json(username, password):
    while True:
        attendance_data = attendance(username, password)
        if attendance_data == "Error":
            return dumps({"response": "error"})
        if attendance_data == "ERP is down!":
            return dumps({"response": attendance_data})
        ret = get_attendance(attendance_data)
        if ret == "Error":
            return dumps({"response": "error"})
        break

    data = list()
    table = ret
    for i in range(len(table)):
        if "SrNo" not in table[i].keys():
            break
        elif i > 0 and str(table[i]['Subject']) == str(table[i - 1]['Subject']):
            data[-1][str(table[i]['Subject Type'].lower()) + '_present'] = int(table[i]['Present'])
            data[-1][str(table[i]['Subject Type'].lower()) + '_total'] = int(table[i]['Total Period'])
        else:
            data.append(
                {
                    'subject': str(table[i]['Subject']),
                    str(table[i]['Subject Type'].lower()) + '_present': int(table[i]['Present']),
                    str(table[i]['Subject Type'].lower()) + '_total': int(table[i]['Total Period']),
                }
            )

    return dumps(data)
