[![Main Foodgram workflow](https://github.com/Inswty/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Inswty/foodgram/actions/workflows/main.yml)
[![Website](https://img.shields.io/badge/Visit-Live%20Site-brightgreen)](https://foodgram-25.duckdns.org/)
## Foodgram
Проект «Фудграм» — это сервис, на котором пользователи могут публиковать свои рецепты, читать\добавлять рецепты других участников себе в избранное, подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок», который позволяет создавать и выгружать в файл перечень продуктов, которые нужно купить для приготовления выбранных блюд.

### Функциональность:
- Регистрация и авторизация (TokenAuthentication аутентификация)
- Лента рецептов (сортировка «от новых к старым»)
- Публикация рецептов (фото, описание, ингредиенты, шаги приготовления)
- Профиль пользователя (личные рецепты, избранное, подписки)
- Возможность экспорта списка покупок в файл txt
- Админ-панель Django
- Поддержка деплоя на сервер с использованием GitHub Actions + Docker + nginx
- REST API

### Установка и запуск проекта локально:
1. Клонируйте репозиторий, установите зависимости:
```bash
git clone git@github.com:Inswty/foodgram.git
cd foodgram
pip install -r requirements.txt
```
2. Создайте и примени миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```
3. Создайте и заполните .env файл:  
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
4. Запустите проект через Docker Compose:
```bash
docker-compose up
```
Проект будет доступен по адресу [http://localhost:8000](http://localhost:8000)

**Как запустить в проде:**  
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
после развертывания приложения на сервере, перейти в контейнер и выполнить:
```bash
python manage.py load_csv_data
```

## Hosted Version:
[https://foodgram-25.duckdns.org/](https://foodgram-25.duckdns.org/)

## Технологический стек:
- Python 3.12 / Django (бэкенд)
- React (фронтенд)
- PostgreSQL
- Docker / Docker Compose
- Gunicorn
- Nginx (gateway)
- GitHub Actions (CI/CD)
- Certbot (HTTPS)

## Автор:
Проект разработан 
[Павел Куличенко](https://github.com/Inswty)