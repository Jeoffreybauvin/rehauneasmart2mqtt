FROM python:3.15-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/usr/src/app/main.py" ]
