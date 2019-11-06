For linux only rn (always update your linux distro to latest version) \
for MITWPU students only \
prerequisites : python3, selenium, geckodriver, firefox, pytesseract, pillow, tesserect-ocr\
 \
It gives Attendence as an output in terminal (no need of manual captcha solving) \
 \
Download geckodriver from https://github.com/mozilla/geckodriver/releases \
copy geckodriver to /usr/bin directory using
```sh
sudo mv geckodriver /usr/bin/geckodriver
```
```sh
pip3 install pytesseract --user
```
```sh
pip3 install pillow --user
```
```sh
pip3 install tesseract-ocr --user
```
```sh
pip3 install pandas --user
```
```sh
cd /usr/share/tessdata/
sudo wget https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata
```
```sh
git clone https://github.com/prkprime/erp_attendence_scraper.git
cd erp_attendence_scraper
python3 start.py
```
