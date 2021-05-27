FROM ubuntu:focal
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install curl python3.9 python-is-python3 python3-pip tesseract-ocr tesseract-ocr-eng wget -y
RUN wget https://github.com/tesseract-ocr/tessdata/blob/master/eng.traineddata?raw=true -O /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata
RUN python3.9 -m pip install poetry
RUN poetry config virtualenvs.create false
WORKDIR /app
ADD . ./
RUN poetry install
ENTRYPOINT gunicorn api:app -b 0.0.0.0:5501 --workers=4
