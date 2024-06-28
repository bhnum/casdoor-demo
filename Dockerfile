FROM python:3.12-slim

EXPOSE 8080

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /app

CMD ["fastapi", "dev", "--host", "0.0.0.0"]
