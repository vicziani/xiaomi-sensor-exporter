FROM python:3.11.4

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY xiaomi_sensor_exporter.py .

ENTRYPOINT ["python", "-u", "xiaomi_sensor_exporter.py", "-c", "/app/config/config.yaml"]