FROM python:3.9-slim
WORKDIR /app
COPY lab2/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
COPY lab2/src/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
