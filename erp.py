#!/usr/bin/env python3
import os
from base64 import b64decode
from io import BytesIO
from json import dumps, loads
from re import search, DOTALL

import pytesseract as loki
import requests
from PIL import Image
from bs4 import BeautifulSoup
from decouple import config

from telegram import TG

api_key = None
chat_id = None

tg = TG(api_key)


def log(
    user: str,
    data: str,
    captcha: str,
    param: str,
    captcha_image: Image,
    login_response: str,
):
    """
    A function to parse some data and send it to our log channel on Telegram
    :param user: ERP User ID
    :param data: HTML content of the erroneous page
    :param captcha: The last tried captcha text
    :param param: The name of the asp document that was being accessed
    :param captcha_image: The base64encoded captcha image
    :param login_response: The response to the initial login request
    :return: Nothing, tbh
    """
    if api_key is None or chat_id is None:
        return

    document = f"{user}.html"
    with open(document, "w") as f:
        f.write(data)

    login_document = "login_response.html"
    with open(login_document, "w") as f:
        f.write(login_response)

    image_file = f"{captcha}.png"
    with open(image_file, "wb") as f:
        f.write(b64decode(captcha_image))

    tg.send_message(chat_id, f"<b>Poseidon</b>:\nUser {user}")
    tg.send_image(chat_id, image_file, f"Captcha: {captcha}")
    tg.send_document(chat_id, param, document)
    tg.send_document(chat_id, "Login Response", login_document)
    os.remove(document)
    os.remove(image_file)


"""
Required for login to ERP
chkCheck is pretty simple, just checking the "I am not a robot checkbox"
__VIEWSTATE,__VIEWSTATEGENERATOR are for hidden values in form
"""
payload = {
    "__VIEWSTATE": "/wEPDwULLTE5ODI5MDAxMzMPFgIeDkxPR0lOX0JBU0VEX09OZRYCAgEPZBYCAgMPZBYCZg9kFgYCDw9kFgICAQ8QZA8WAWYWARAFA1dQVQUDV1BVZxYBZmQCEw8PFgIeB0VuYWJsZWRnZGQCGQ9kFgICAQ8QZGQWAWZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQhjaGtDaGVja+/IxmsP3IoCwjVYbsmN45kfOjGivX4s7e93RISZwDsW",
    "__EVENTTARGET": "btnLogin",
    "chkCheck": "on",
    "__VIEWSTATEGENERATOR": "B8B84CAE",
}

# Just to easily get error messages, because these can be repeated
ERRORS = {
    "e": "ERP is down!",
    "w": "Wrong credentials!",
    "c": "Captcha issue! Please refresh!",
    "r": "Record not found!",
}

# List of valid titles
VALID_TITLES = {
    "Self Attendance Report",
    "MainLogin",
    "Academic And Non Academic Fees Status",
}


def get_erp_data(
    username: str, password: str, param: str, parent: str = "student"
) -> str:
    """
    Parameters
    ----------
    username - ERP ID
    password - ERP Password
    param - Page of ERP to be loaded

    Returns
    -------
    Page's HTML content if successful, else corresponding error code
    """

    # We give up after 10 tries
    count = 0

    while True:

        # Use the same session so that login actually persists
        with requests.session() as s:
            captcha_text = ""

            # Keep fetching and parsing a captcha until we receive some text
            while len(captcha_text) != 6:
                headers = {"Content-Type": "application/json; charset=utf-8"}
                response = s.post(
                    "https://erp.mitwpu.edu.in/AdminLogin.aspx/funGenerateCaptcha",
                    headers=headers,
                )
                if response.status_code != 200:
                    return "e"
                data = response.text
                img = loads(data)["d"]

                stream = BytesIO(b64decode(img))
                # Use tesseract-ocr to read the captcha text
                image = Image.open(stream)

                captcha_text = loki.image_to_string(
                    image,
                    config='--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789abcdef --tessdata-dir "C:\\Users\\gjadd\\AppData\\Local\\Tesseract-OCR\\tessdata"',
                )

            # Set the payload for the actual login part
            payload["txtUserId"] = username
            payload["txtPassword"] = password
            payload["txtCaptcha"] = captcha_text

            # Headers for logging in and fetching the data
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"

            # POST request to log in
            response = s.post(
                "https://erp.mitwpu.edu.in/AdminLogin.aspx",
                headers=headers,
                data=payload,
            )

            # Upon entering wrong credentials, ERP gives us a popup containing this text
            if "USER Id/ Password Mismatch" in response.text:
                return "w"

            # Check for the new useless ratelimits of allowing us to login only every 30 minutes
            if m := search(r'You are allowed to login after \d+ min\.', response.text):
                error_key = f'{username}-ratelimit'
                ERRORS[error_key] = m.group()
                return error_key

            # Increment count so we can break out after 10 tries and assume captcha reading failed
            count += 1

            # Retrieve the page content
            data = s.get(
                f"https://erp.mitwpu.edu.in/{os.path.join(parent, param)}.aspx"
            ).text

            # Check the title of retrieved page
            title = search("(?<=<title>).+?(?=</title>)", data, DOTALL).group().strip()

            # Before a new trimester starts, ERP records are seemingly wiped
            if "Record Not Found" in data:
                return "r"

            # For attendance and timetable, this is the page title
            # However even wrong captcha page has the same title, so ensure no traces of AdminLogin.aspx
            if title in VALID_TITLES and "AdminLogin.aspx" not in data:
                return data

            # A reference to AdminLogin.aspx means login failed. Since the credentials are correct, is it most likely
            # captcha
            if "AdminLogin.aspx" in data and count < 10:
                continue

            # At this point, all we can do is give up and assume that reading the captcha fail
            # There is also the possibility of ERP forcing a password change or something similar, that needs to be
            # accounted for
            if count >= 10:
                log(username, data, captcha_text, param, img, response.text)
                return "c"


def attendance(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    Either error code, or attendance page data
    """
    return get_erp_data(username, password, "SelfAttendence")


def timetable(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    Either error code, or timetable page data
    """
    return get_erp_data(username, password, "StudentSelfTimeTable")


def fees(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    Either error code, or payable fees page data
    """
    return get_erp_data(username, password, "AcademicfeesAll", parent="student")


def miscellaneous(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    Either error code, or miscellaneous data
    """
    return get_erp_data(username, password, "MainNew")


def get_attendance(data: str) -> list:
    """

    Parameters
    ----------
    data -> Attendance HTML page to be parsed

    Returns
    -------
    List of dicts containing attendance data
    """
    soup = BeautifulSoup(data, features="html.parser")
    tables = soup.findAll("table")

    # ERP Attendance page contains 4 tables
    if len(tables) != 4:
        return ["Error"]

    # Attendance data is in the second table
    table = tables[1]

    # Get all the table titles
    titles = [h.text for h in table.find("thead").find("tr")]

    # Get the table body
    body = table.find("tbody")
    ret = []

    # Iterate over all the rows in the body to get the actual data
    for row in body.findAll("tr"):
        attendance = {}
        # Length 6 contains subject name and serial number as well
        if len(row) == 6:
            for element in range(len(row.findAll("td"))):
                attendance[titles[element]] = row.findAll("td")[element].text.strip()
        # Length 4 means its the 2nd row for the subject, so need the previous subject name
        elif len(row) == 4:
            attendance[titles[0]] = ret[-1][titles[0]]
            attendance[titles[1]] = ret[-1][titles[1]]
            for element in range(len(row.findAll("td"))):
                attendance[titles[element + 2]] = row.findAll("td")[
                    element
                ].text.strip()
        # Any other structure means its one of the totals which is easier to compute on our own than parse
        else:
            continue
        ret.append(attendance)
    return ret


def attendance_json(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    JSON body containing attendance data
    """

    # Keep trying to get attendance until we succeed or hit one of our error messages
    while True:
        attendance_data = attendance(username, password)
        if attendance_data in ERRORS.keys():
            return dumps([{"response": ERRORS[attendance_data]}])
        ret = get_attendance(attendance_data)
        if ret == ["Error"]:
            return dumps([{"response": "Error parsing attendance!"}])
        break

    # Convert the data BeautifulSoup gave us into a list of dicts
    data = list()
    table = ret
    for i in range(len(table)):
        # Ignore serial number
        if "SrNo" not in table[i].keys():
            break
        # Practical / Tutorial
        elif i > 0 and str(table[i]["Subject"]) == str(table[i - 1]["Subject"]):
            data[-1][str(table[i]["Subject Type"].lower()) + "_present"] = int(
                table[i]["Present"]
            )
            data[-1][str(table[i]["Subject Type"].lower()) + "_total"] = int(
                table[i]["Total Period"]
            )
        # Theory lecture
        else:
            data.append(
                {
                    "subject": str(table[i]["Subject"]),
                    str(table[i]["Subject Type"].lower())
                    + "_present": int(table[i]["Present"]),
                    str(table[i]["Subject Type"].lower())
                    + "_total": int(table[i]["Total Period"]),
                }
            )
    # Return the data after calling json.dumps() on it
    return dumps(data)


def get_fees(data: str) -> list:
    """

    Parameters
    ----------
    data -> Fees HTML page to be parsed

    Returns
    -------
    List of dicts containing fees data
    """
    soup = BeautifulSoup(data, features="html.parser")
    tables = soup.findAll("table")

    # ERP Fees page contains 2 tables
    if len(tables) != 2:
        return ["Error"]

    # Fees data is in the second table
    table = tables[1]

    # Get all the table titles
    titles = []
    demo = table.find("tr").findAll("td")
    for l in list(demo):
        titles.append(l.text)

    ret = []

    # Iterate over all the rows in the body to get the actual data(enumerate is used to get the index of for lop)
    for idx, row in enumerate(table.findAll("tr")[1:]):
        fees = {}
        # Length 15 contains Fees type
        if len(row) == 15:
            # 7th,12th and 14th index of for loop contains the totals of respective fees types which we want to ignore
            if idx == 7 or idx == 12 or idx == 14:
                continue
            for element in range(len(row.findAll("td"))):
                fees[titles[element]] = row.findAll("td")[element].text.strip()
        # Length 13 means its the 2nd row for the Fees type, so need the previous Fees type name
        elif len(row) == 13:
            # 15th index contains the grand total of all fees which we also ignore
            if idx == 15:
                continue
            fees[titles[0]] = ret[-1][titles[0]]
            for element in range(len(row.findAll("td"))):
                fees[titles[element + 1]] = row.findAll("td")[element].text.strip()
        else:
            continue

        # The Advance column in erp fees table gives a blank string when there is no advance, so replacing it with '0'
        dct = {k: '0' if not v else v for k, v in fees.items()}
        ret.append(dct)

    return ret

def fees_json(username: str, password: str) -> str:
    """

    Parameters
    ----------
    username -> ERP ID
    password -> ERP Password

    Returns
    -------
    JSON body containing fees data
    """

    # Keep trying to get fees until we succeed or hit one of our error messages
    while True:
        fees_data = fees(username, password)
        if fees_data in ERRORS.keys():
            return dumps([{"response": ERRORS[fees_data]}])
        ret = get_fees(fees_data)
        if ret == ["Error"]:
            return dumps([{"response": "Error parsing attendance!"}])
        break

    # Convert the data BeautifulSoup gave us into a list of dicts
    data = list(ret)

    # Return the data after calling json.dumps() on it
    return dumps(data)