# Используем образ Python 3.9.
FROM python:3.9

# Копируем файлы проекта
RUN mkdir /app
WORKDIR /app
COPY . /app


# Ставим необходимые зависимости
RUN pip install pipenv
RUN pipenv install --deploy --system

# Команда для запуска
CMD python ./calculator/main.py
