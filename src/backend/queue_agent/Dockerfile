FROM public.ecr.aws/docker/library/python:3.10-slim

RUN apt-get update; apt-get install libmagic1 -y; rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' app && \
    mkdir /app || true; \
    chown -R app /app
WORKDIR /app
USER app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY src/* ./

CMD python3 -u /app/main.py
