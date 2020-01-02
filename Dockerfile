FROM python:alpine

RUN apk add --no-cache bash gcc jpeg-dev musl-dev tesseract-ocr zlib-dev

COPY . /app

WORKDIR /app

RUN python -m venv /venv

RUN source /venv/bin/activate

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["./start.sh"]
