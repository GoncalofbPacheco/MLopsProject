FROM python:3.11.9-slim

# non-root
RUN useradd -ms /bin/bash kedro
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R kedro:kedro /app
USER kedro

# simple logging setup
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_PATH=/app/logs/info.log
CMD ["kedro", "run"]
