## Foodgram
[![Main Foodgram workflow](https://github.com/Inswty/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Inswty/foodgram/actions/workflows/main.yml)
[![Website](https://img.shields.io/badge/Visit-Live%20Site-brightgreen)](https://foodgram-25.duckdns.org/)

**Проект «Фудграм»** —  это сервис, где пользователи могут публиковать собственные рецепты, добавлять рецепты других участников в избранное и подписываться на публикации любимых авторов. Зарегистрированным пользователям доступен сервис «Список покупок», который позволяет формировать и выгружать в файл перечень продуктов, необходимых для приготовления выбранных блюд.

### Технологический стек:
- Python 3.12
- Django
- Django REST Framework
- React
- PostgreSQL
- Docker, Docker Compose
- Gunicorn
- Nginx (gateway)
- GitHub Actions (CI/CD)
- Certbot (HTTPS)
- ReDoc (документация API)

### Функциональность:
- Регистрация и авторизация (Token Authentication)
- Лента рецептов с сортировкой от новых к старым
- Публикация рецептов (фото, описание, ингредиенты, шаги приготовления)
- Профиль пользователя (личные рецепты, избранное, подписки)
- Экспорт списка покупок в txt-файл
- Админ-панель Django
- Поддержка деплоя на сервер с GitHub Actions + Docker + Nginx
- REST API

### Установка и запуск проекта локально:
1. Клонируйте репозиторий:
```bash
git clone git@github.com:Inswty/foodgram.git
```
2. Создайте и заполните .env файл:  
Пример содержимого:
```
DEBUG=True
USE_SQLITE=False
ALLOWED_HOSTS=127.0.0.1,localhost,foodgram-25.duckdns.org
DJANGO_SECRET_KEY={SECRET_KEY}
POSTGRES_DB=recipes
POSTGRES_USER=recipes_user
POSTGRES_PASSWORD=recipes_password
DB_HOST=db
DB_PORT=5432
```
3. Запустите проект через Docker Compose:
```bash
docker compose up --build
```
4. Выполните миграции:
```
docker compose exec backend python manage.py migrate
```
Проект будет доступен по адресу: [http://localhost:8000](http://localhost:8000)

Документация API доступна по адресу: [http://localhost:8000/docs/](http://localhost:8000/docs/)

### Продакшен / Деплой:  
- Настроить переменные окружения в .env, скопировать на сервер в директорию проекта
- Создать SICRETS в GitHub Actions:
```
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
SSH_KEY
SSH_PASSPHRASE
TELEGRAM_TO
TELEGRAM_TOKEN
USER
```
- Выполнить пуш GitHub в ветку main:
```bash
git push origin main
```

## Наполнение базы данных:
Для загрузки списка ингредиентов в БД из CSV-файла,  
после развертывания приложения на сервере, выполнить:
```bash
docker compose exec backend python manage.py load_csv_data
```

## Автор:
Проект разработан 
[Павел Куличенко](https://github.com/Inswty)