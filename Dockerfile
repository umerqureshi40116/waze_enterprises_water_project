FROM python:3.13-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

EXPOSE 8000

# Start the application - hardcoded port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
