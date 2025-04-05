FROM python:3.12-slim

# Базові налаштування
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Створюємо правильну структуру каталогів
WORKDIR /usr/agent

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Копіюємо CSV файли у батьківську директорію
COPY accelerometer.csv gps.csv data.csv /usr/

# Копіюємо код додатку
COPY src ./lab1/src/

# Додаємо поточну директорію до шляху Python
ENV PYTHONPATH=/usr/agent

# Запускаємо додаток з коректним шляхом
CMD ["python", "-m", "src.main"]