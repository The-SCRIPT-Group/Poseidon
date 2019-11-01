For linux only rn \
prerequisites : python3, selenium, geckodriver, pytesseract, pillow \
1. \
Download geckodriver from https://github.com/mozilla/geckodriver/releases \
copy geckodriver to /usr/bin directory using \
sudo mv geckodriver /usr/bin/geckodriver \
2. \
pip3 install pytesseract --user \
3. \
pip3 install pillow --user \
4. \
pip3 install tesseract-ocr --user \
5. \
cd /usr/share/tessdata/ \
sudo wget https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata \
6. \
python3 start.py \
