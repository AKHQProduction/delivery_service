# Water Delivery

## Запуск проекта

### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```env
# PostgreSQL
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=water_delivery
POSTGRES_PORT=5432
POSTGRES_INTERNAL_PORT=5432
DB_HOST=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Telegram Bot
BOT_TOKEN=your_bot_token
```

### 2. Запуск контейнеров

```bash
docker compose up -d
```

### 3. Создание тестовых данных

Для инициализации базы данных тестовыми данными выполните:

```bash
docker compose exec postgres bash -c "bash < /scripts/seed_db.sh"
```

Этот скрипт создаст:
- **Роли**: OWNER, MANAGER, COURIER
- **Магазин**: "Test Shop"
- **Тестовых пользователей**:
  - Owner User (telegram_id: 1000) - владелец
  - Manager User (telegram_id: 2000) - менеджер
  - Courier User (telegram_id: 3000) - курьер

## Остановка проекта

```bash
docker compose down
```

Для полной очистки с удалением volume:

```bash
docker compose down -v
```
