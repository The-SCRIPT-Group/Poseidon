For linux only rn \
prerequisites : python3, selenium, geckodriver, pytesseract, pillow

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
cd /usr/share/tessdata/
sudo wget https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata
```
```sh
python3 start.py
```
