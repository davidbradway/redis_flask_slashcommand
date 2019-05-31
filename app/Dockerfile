FROM python:3.6-alpine

ENV BIND_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./app.py /app.py

EXPOSE $BIND_PORT

WORKDIR /

RUN chmod 644 app.py

CMD ["flask", "run", "-h", "0.0.0.0"]
