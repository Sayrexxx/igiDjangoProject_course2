# Используем официальный базовый образ Python
FROM python:3.9-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы требований
COPY requirements.txt /app/

# Устанавливаем зависимости проекта
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . /app/

# Устанавливаем переменную окружения для настройки Django
ENV DJANGO_SETTINGS_MODULE=myapp.settings

# Открываем порт для сервера
EXPOSE 8000

# Выполняем миграции и собираем статические файлы


RUN python manage.py test
# Запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]