#!/usr/bin/env bash
set -e

# Переменные окружения должны быть доступны из контейнера
# Если скрипт запускается локально, убедитесь что .env загружен

# Проверяем подключение
echo "⏳ Проверка подключения к PostgreSQL..."
until pg_isready -h "${DB_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "$POSTGRES_USER"; do
  sleep 1
done
echo "✅ PostgreSQL доступен"

# Подключаемся к БД и выполняем SQL
echo "🚀 Засеваем данные..."
psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}" <<'SQL'
DO $$
DECLARE
  owner_user_id UUID;
  manager_user_id UUID;
  courier_user_id UUID;
  shop_id UUID;
  owner_role_id INT;
  manager_role_id INT;
  courier_role_id INT;
BEGIN
  -- Создаём роли если их нет
  INSERT INTO roles (name)
  SELECT 'OWNER' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'OWNER');

  INSERT INTO roles (name)
  SELECT 'MANAGER' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'MANAGER');

  INSERT INTO roles (name)
  SELECT 'COURIER' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'COURIER');

  -- Получаем ID ролей
  SELECT id INTO owner_role_id FROM roles WHERE name = 'OWNER';
  SELECT id INTO manager_role_id FROM roles WHERE name = 'MANAGER';
  SELECT id INTO courier_role_id FROM roles WHERE name = 'COURIER';

  -- Создаем магазин если его нет
  INSERT INTO shops (id, name)
  SELECT gen_random_uuid(), 'Test Shop'
  WHERE NOT EXISTS (SELECT 1 FROM shops WHERE name = 'Test Shop')
  RETURNING id INTO shop_id;

  -- Если магазин уже существовал, получаем его ID
  IF shop_id IS NULL THEN
    SELECT id INTO shop_id FROM shops WHERE name = 'Test Shop';
  END IF;

  -- Создаём пользователя Owner если его нет
  IF NOT EXISTS (SELECT 1 FROM telegram_accounts WHERE telegram_id = 1000) THEN
    owner_user_id := gen_random_uuid();
    INSERT INTO users (id) VALUES (owner_user_id);
    INSERT INTO telegram_accounts (user_id, telegram_id, full_name)
    VALUES (owner_user_id, 1000, 'Owner User');
    INSERT INTO shop_memberships (user_id, shop_id, role_id, name)
    VALUES (owner_user_id, shop_id, owner_role_id, 'Owner User');
    RAISE NOTICE 'Создан Owner User (telegram_id: 1000)';
  ELSE
    RAISE NOTICE 'Owner User (telegram_id: 1000) уже существует';
  END IF;

  -- Создаём пользователя Manager если его нет
  IF NOT EXISTS (SELECT 1 FROM telegram_accounts WHERE telegram_id = 2000) THEN
    manager_user_id := gen_random_uuid();
    INSERT INTO users (id) VALUES (manager_user_id);
    INSERT INTO telegram_accounts (user_id, telegram_id, full_name)
    VALUES (manager_user_id, 2000, 'Manager User');
    INSERT INTO shop_memberships (user_id, shop_id, role_id, name)
    VALUES (manager_user_id, shop_id, manager_role_id, 'Manager User');
    RAISE NOTICE 'Создан Manager User (telegram_id: 2000)';
  ELSE
    RAISE NOTICE 'Manager User (telegram_id: 2000) уже существует';
  END IF;

  -- Создаём пользователя Courier если его нет
  IF NOT EXISTS (SELECT 1 FROM telegram_accounts WHERE telegram_id = 3000) THEN
    courier_user_id := gen_random_uuid();
    INSERT INTO users (id) VALUES (courier_user_id);
    INSERT INTO telegram_accounts (user_id, telegram_id, full_name)
    VALUES (courier_user_id, 3000, 'Courier User');
    INSERT INTO shop_memberships (user_id, shop_id, role_id, name)
    VALUES (courier_user_id, shop_id, courier_role_id, 'Courier User');
    RAISE NOTICE 'Создан Courier User (telegram_id: 3000)';
  ELSE
    RAISE NOTICE 'Courier User (telegram_id: 3000) уже существует';
  END IF;

END $$;

SQL

echo "✅ Данные успешно засеяны!"
