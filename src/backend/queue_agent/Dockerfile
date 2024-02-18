FROM public.ecr.aws/docker/library/python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt
COPY main.py ./

CMD python3 -u main.py
