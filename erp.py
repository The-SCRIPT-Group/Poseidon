#!/usr/bin/env python3
import os

import pytesseract as loki
import requests
import json
from base64 import b64decode
from uuid import uuid4

username = "S1032170015"
password = input("Enter password: ")

captcha_file = str(uuid4().hex) + ".png"
with requests.session() as s:
    headers = {"Content-Type": "application/json; charset=utf-8"}

    captcha_text = ""
    while captcha_text == "":
        data = s.post(
            "https://erp.mitwpu.edu.in/AdminLogin.aspx/funGenerateCaptcha",
            headers=headers,
        ).text
        img = json.loads(data)["d"]
        with open(captcha_file, "wb") as captcha:
            captcha.write(b64decode(img))
        captcha_text = loki.image_to_string(captcha_file)
    print(f"Captcha is {captcha_text}")

    payload = {
        "__LASTFOCUS": "",
        "__VIEWSTATE": "/wEPDwULLTE5ODI5MDAxMzMPFgIeDkxPR0lOX0JBU0VEX09OZRYCAgEPZBYCAgMPZBYCZg9kFgYCDw9kFgICAQ8QZA8WAWYWARAFA1dQVQUDV1BVZxYBZmQCEw8PFgIeB0VuYWJsZWRnZGQCGQ9kFgICAQ8QZGQWAWZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQhjaGtDaGVja+/IxmsP3IoCwjVYbsmN45kfOjGivX4s7e93RISZwDsW",
        "__EVENTTARGET": "btnLogin",
        "__EVENTARGUMENT": "",
        "txtUserId": username,
        "txtPassword": password,
        "txtCaptcha": captcha_text,
        "chkCheck": "on",
        "__VIEWSTATEGENERATOR": "B8B84CAE",
        "hdnMsg": "",
        "hdtype": "",
        "hdloginid": "",
        "hdnFlag": "R",
    }

    # headers for logging in
    headers["X-MicrosoftAjax"] = "Delta=true"
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    # api call to log in
    response = s.post(
        "https://erp.mitwpu.edu.in/AdminLogin.aspx", headers=headers, data=payload
    )
    print(response)
    print(response.text)

    with open("response.html", "w") as f:
        f.write(
            s.get(
                "https://erp.mitwpu.edu.in/STUDENT/SelfAttendence.aspx?MENU_CODE=MWEBSTUATTEN_SLF_ATTEN"
            ).text
        )
os.remove(captcha_file)
