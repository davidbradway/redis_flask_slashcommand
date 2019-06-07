FROM python:3.6-alpine

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /app

EXPOSE $BIND_PORT

WORKDIR /app

RUN chmod 644 app.py

CMD ["flask", "run", "-h", "0.0.0.0"]
