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

# Копіюємо CSV файли на ОДИН РІВЕНЬ ВИЩЕ робочої директорії
COPY accelerometer.csv gps.csv data.csv /usr/agent/../

# Копіюємо код додатку
COPY . .

# Створюємо символічне посилання для lab1
RUN ln -s /usr/agent /usr/agent/lab1

# Додаємо поточну директорію до шляху Python
ENV PYTHONPATH=/usr/agent

# Запускаємо додаток з коректним шляхом
CMD ["python", "-m", "src.main"]