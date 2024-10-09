FROM --platform=linux/amd64 python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "latency.py"]