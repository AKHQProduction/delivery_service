# Context

## Order intake

Order intake is the domain path that turns a client, delivery slot, address,
phone, product list, payment method, and comment into a persisted Order.

It owns current Order creation policies: address and phone snapshots, product
name and price snapshots, optional recurring order link, balance payment,
missing-coordinate geocoding, and route insertion.
