FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

# state.json lives in /app/data -- mount this as a volume in production
# so delta detection works across container restarts (see README.md).
VOLUME ["/app/data"]

CMD ["python", "-m", "app.main"]