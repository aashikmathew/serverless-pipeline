FROM python:3.11-slim

WORKDIR /app

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY main.py .

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD exec functions-framework --target=data_validator --port=${PORT} 