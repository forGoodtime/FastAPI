# FastAPI Project

## Описание

Это пример асинхронного API на FastAPI с поддержкой PostgreSQL, Redis и Celery. Проект развёрнут на Render.

## Стек

- FastAPI
- PostgreSQL (через SQLAlchemy)
- Redis (для кэша и брокера задач)
- Celery (фоновые задачи)
- Docker

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Настройка переменных окружения

Создайте файл `.env` и заполните его:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<dbname>
SECRET_KEY=your_secret_key
DEBUG=True
REDIS_URL=redis://<host>:6379
CELERY_BROKER_URL=redis://<host>:6379/0
CELERY_RESULT_BACKEND=redis://<host>:6379/0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Локальный запуск

```bash
docker-compose up --build
```

### 4. Деплой на Render

- Создайте сервисы: Web Service (FastAPI), Key Value (Redis), Database (PostgreSQL).
- Вставьте переменные окружения из `.env` в настройки Render.
- Перезапустите сервис.

## Основные команды

- Запуск приложения:  
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- Запуск Celery worker:  
  ```bash
  celery -A tasks worker --loglevel=info
  ```

## Документация API

После запуска перейдите на:

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Лицензия

MIT