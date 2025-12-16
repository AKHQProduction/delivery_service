import asyncio
import json
import random
import uuid
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

load_dotenv("/Users/plztrustme/dev/work/water_delivery/.env")

import os

DATABASE_URI = (
    f"postgresql+psycopg://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
)

SHOP_ID = uuid.UUID("7b402d92-39de-4d96-85fe-ec71ab703273")
DELIVERY_DATE = date(2025, 12, 20)

# Ukrainian names
FIRST_NAMES = [
    "Олександр", "Максим", "Артем", "Дмитро", "Андрій", "Богдан", "Владислав",
    "Микола", "Сергій", "Віталій", "Євген", "Ігор", "Тарас", "Роман", "Юрій",
    "Олена", "Наталія", "Ірина", "Марія", "Анна", "Катерина", "Світлана",
    "Тетяна", "Оксана", "Юлія", "Вікторія", "Людмила", "Галина", "Надія", "Лариса"
]

LAST_NAMES = [
    "Шевченко", "Коваленко", "Бондаренко", "Ткаченко", "Кравченко", "Олійник",
    "Мельник", "Савченко", "Поліщук", "Павленко", "Лисенко", "Мороз", "Левченко",
    "Гончаренко", "Марченко", "Петренко", "Іванченко", "Сидоренко", "Карпенко",
    "Романенко", "Приходько", "Литвиненко", "Степаненко", "Федоренко", "Кузьменко"
]

STREETS = [
    "вул. Хрещатик", "вул. Велика Васильківська", "вул. Саксаганського",
    "вул. Богдана Хмельницького", "вул. Володимирська", "вул. Шота Руставелі",
    "вул. Лесі Українки", "вул. Михайла Грушевського", "пр. Перемоги",
    "вул. Антоновича", "вул. Льва Толстого", "вул. Пушкінська",
    "вул. Січових Стрільців", "вул. Басейна", "вул. Велика Житомирська",
    "вул. Софіївська", "вул. Рейтарська", "вул. Прорізна", "вул. Костельна",
    "бул. Тараса Шевченка", "вул. Ярославів Вал", "вул. Золотоворітська"
]

PRODUCTS = [
    ("Вода Моршинська 19л", Decimal("120.00"), "WATER"),
    ("Вода Боржомі 19л", Decimal("150.00"), "WATER"),
    ("Вода Миргородська 19л", Decimal("110.00"), "WATER"),
    ("Вода Трускавецька 19л", Decimal("130.00"), "WATER"),
    ("Вода Поляна Квасова 19л", Decimal("140.00"), "WATER"),
    ("Вода BonAqua 19л", Decimal("100.00"), "WATER"),
    ("Вода Аква Няня 19л", Decimal("95.00"), "WATER"),
    ("Помпа механічна", Decimal("150.00"), "OTHER"),
    ("Помпа електрична", Decimal("450.00"), "OTHER"),
    ("Підставка для бутля", Decimal("200.00"), "OTHER"),
    ("Кулер настільний", Decimal("2500.00"), "OTHER"),
    ("Склянки одноразові (100 шт)", Decimal("80.00"), "OTHER"),
]


def generate_phone() -> str:
    prefixes = ["50", "66", "67", "68", "93", "95", "96", "97", "98", "99"]
    return f"+380{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def generate_address() -> dict:
    return {
        "street": random.choice(STREETS),
        "house": str(random.randint(1, 150)),
        "apartment": str(random.randint(1, 200)) if random.random() > 0.3 else None,
        "entrance": str(random.randint(1, 8)) if random.random() > 0.4 else None,
        "floor": str(random.randint(1, 25)) if random.random() > 0.5 else None,
        "intercom": str(random.randint(100, 9999)) if random.random() > 0.6 else None,
        "address_type": "APARTMENT" if random.random() > 0.2 else "PRIVATE_HOUSE",
    }


async def main():
    engine = create_async_engine(DATABASE_URI)

    async with engine.begin() as conn:
        # Create products
        print("Creating products...")
        product_ids = []
        for name, price, category in PRODUCTS:
            product_id = uuid.uuid4()
            product_ids.append((product_id, name, price))
            await conn.execute(
                text("""
                    INSERT INTO products (id, name, price, category, shop_id, created_at, updated_at)
                    VALUES (:id, :name, :price, :category, :shop_id, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": product_id,
                    "name": name,
                    "price": price,
                    "category": category,
                    "shop_id": SHOP_ID,
                },
            )
        print(f"Created {len(PRODUCTS)} products")

        # Create clients
        print("Creating clients...")
        client_ids = []
        for i in range(30):
            client_id = uuid.uuid4()
            full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            phone = generate_phone()

            await conn.execute(
                text("""
                    INSERT INTO clients (id, full_name, shop_id, created_at, updated_at)
                    VALUES (:id, :full_name, :shop_id, NOW(), NOW())
                """),
                {"id": client_id, "full_name": full_name, "shop_id": SHOP_ID},
            )

            await conn.execute(
                text("""
                    INSERT INTO client_phones (number, is_primary, client_id, shop_id, created_at, updated_at)
                    VALUES (:number, TRUE, :client_id, :shop_id, NOW(), NOW())
                """),
                {"number": phone, "client_id": client_id, "shop_id": SHOP_ID},
            )

            addr = generate_address()
            await conn.execute(
                text("""
                    INSERT INTO client_addresses
                    (street, house, apartment, entrance, floor, intercom, address_type, is_primary, client_id, created_at, updated_at)
                    VALUES (:street, :house, :apartment, :entrance, :floor, :intercom, :address_type, TRUE, :client_id, NOW(), NOW())
                """),
                {**addr, "client_id": client_id},
            )

            client_ids.append((client_id, full_name, phone, addr))

        print(f"Created {len(client_ids)} clients")

        # Create orders
        print("Creating orders...")
        order_count = 0
        for i in range(100):
            client_id, client_name, phone, addr = random.choice(client_ids)
            order_id = uuid.uuid4()
            time_pref = random.choice(["FIRST_HALF", "SECOND_HALF"])

            # Sometimes use a different address
            delivery_addr = addr if random.random() > 0.3 else generate_address()
            delivery_phone = phone if random.random() > 0.2 else generate_phone()

            comment = None
            if random.random() > 0.7:
                comments = [
                    "Зателефонувати за 30 хв",
                    "Код від домофону 1234",
                    "Залишити біля дверей",
                    "Передзвонити перед доставкою",
                    "Не дзвонити, постукати",
                    "Собака у дворі - обережно",
                    "Вхід з торця будинку",
                ]
                comment = random.choice(comments)

            await conn.execute(
                text("""
                    INSERT INTO orders
                    (id, date, delivery_address, delivery_phone, time_preference, comment, shop_id, client_id, created_at, updated_at)
                    VALUES (:id, :date, :delivery_address, :delivery_phone, :time_preference, :comment, :shop_id, :client_id, NOW(), NOW())
                """),
                {
                    "id": order_id,
                    "date": DELIVERY_DATE,
                    "delivery_address": json.dumps(delivery_addr),
                    "delivery_phone": delivery_phone,
                    "time_preference": time_pref,
                    "comment": comment,
                    "shop_id": SHOP_ID,
                    "client_id": client_id,
                },
            )

            # Add 1-4 items per order
            num_items = random.randint(1, 4)
            selected_products = random.sample(product_ids, min(num_items, len(product_ids)))

            for product_id, product_name, product_price in selected_products:
                quantity = random.randint(1, 5) if "19л" in product_name else 1

                await conn.execute(
                    text("""
                        INSERT INTO order_items (name, quantity, price_per_item, order_id, created_at, updated_at)
                        VALUES (:name, :quantity, :price_per_item, :order_id, NOW(), NOW())
                    """),
                    {
                        "name": product_name,
                        "quantity": quantity,
                        "price_per_item": product_price,
                        "order_id": order_id,
                    },
                )

            order_count += 1

        print(f"Created {order_count} orders for {DELIVERY_DATE}")
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())