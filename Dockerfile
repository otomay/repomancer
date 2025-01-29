FROM python:3.9-slim

RUN apt-get update && apt-get install -y libssl-dev nodejs npm

COPY backend /app/backend
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

WORKDIR /app

EXPOSE 3000

CMD ["sh", "-c", "cd /app/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers ${UVICORN_WORKERS:-1}"]
