FROM public.ecr.aws/docker/library/python:3.10.12-slim
WORKDIR /app
COPY requirements.txt . 
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY *.py ./

CMD ["python", "main.py"]
