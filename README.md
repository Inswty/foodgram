[![Main Foodgram workflow](https://github.com/Inswty/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Inswty/foodgram/actions/workflows/main.yml)

**Foodgram** — проектом «Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Функциональность:

- Регистрация и авторизация (TokenAuthentication аутентификация)
- Лента рецептов (сортировка «от новых к старым»)
- Публикация рецептов (фото, описание, ингредиенты, шаги приготовления)
- Профиль пользователя (личные рецепты, избранное, подписки)
- Возможность экспорта списка покупок в файл txt
- Админ-панель Django
- Поддержка деплоя на сервер с использованием GitHub Actions + Docker + nginx
- REST API

---

Установка и запуск проекта локально:

1. Клонируйте репозиторий:

bash
git clone git@github.com:Inswty/foodgram.git
cd foodgram

2. Создайте и заполните .env файл:
Пример содержимого:

DEBUG=True
USE_SQLITE=False
ALLOWED_HOSTS=127.0.0.1,localhost,foodgram-25.duckdns.org
DJANGO_SECRET_KEY={SECRET_KEY}
POSTGRES_DB=recipes
POSTGRES_USER=recipes_user
POSTGRES_PASSWORD=recipes_password
DB_HOST=db
DB_PORT=5432

3. Запустите проект через Docker Compose:
docker-compose up

Проект будет доступен по адресу http://localhost:9080/

Как запустить в проде:
    -Настроить переменные окружения в .env, скопировать на сервер в директорию проекта
    -Создать SICRETS в GitHub Actions:
        DOCKER_PASSWORD
        DOCKER_USERNAME
        HOST
        SSH_KEY
        SSH_PASSPHRASE
        TELEGRAM_TO
        TELEGRAM_TOKEN
        USER
    -Выполнить пуш в GitHub (bash): git push

Наполнение базы данных:
Для загрузки списка ингредиентов в БД из CSV-файла,
после развертывания приложения на сервере, перейти в контейнер и выполнить:
(bash)
```
python manage.py load_csv_data
```

Технологический стек:
- Python 3.12 / Django (бэкенд)
- React (фронтенд)
- PostgreSQL
- Docker / Docker Compose
- Gunicorn
- Nginx (gateway)
- GitHub Actions (CI/CD)
- Certbot (HTTPS)


Автор:
Проект разработан [Павел Куличенко]
GitHub: https://github.com/Inswty/foodgram.git