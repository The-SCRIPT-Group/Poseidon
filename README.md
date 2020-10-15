# Poseidon - ERP Attendance Scraper

##### To download the source
```bash
git clone https://github.com/The-SCRIPT-Group/Poseidon.git
```

##### To get your environment setup with the required libraries

```bash
pip install -r requirements.txt
```

##### To update dependencies

```bash
pip install -U -r requirements.txt
```

##### You can install the dependencies in a virtualenv if you so desire

##### To run the application with the flask development server

```bash
python3 api.py
```

or with gunicorn

```bash
gunicorn api:app
```

##### On Windows follow these additional steps


override tesseract_cmd in erp.py as

```bash
import pytesseract as loki

loki.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'
```
change captcha_text for tesseract-ocr in erp.py to

```bash
captcha_text = loki.image_to_string(
                    image,
                    config='--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789abcdef --tessdata-dir "C:\\Users\\USER\\AppData\\Local\\Tesseract-OCR\\tessdata"',
                )
```

download eng.traineddata from https://github.com/tesseract-ocr/tessdata/blob/master/eng.traineddata
