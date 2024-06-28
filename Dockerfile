FROM python:3.12.4-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000 5432

