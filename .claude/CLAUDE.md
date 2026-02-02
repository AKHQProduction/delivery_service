# Architecture

## Layers

```
src/backend/
├── bootstrap/          # Entrypoints, DI-контейнеры, конфиг
├── presentation/       # FastAPI routes, aiogram handlers, schemas
├── application/        # Commands, Queries, Policies, Validators, Interfaces
├── domain/             # Stateless сервисы с бизнес-логикой
└── infrastructure/     # SQLAlchemy gateways, Redis, PDF, Telegram
```

## Architecture Decisions

### ORM-модели как доменные модели
ORM-модели SQLAlchemy используются напрямую как доменные объекты (анемичная модель).
Domain-сервисы создают и мутируют ORM-объекты. Отдельных domain entities нет — это осознанное решение.

### Gateway-паттерн
Доступ к данным через Gateway-классы в infrastructure. Для read-операций используются read models (DTO).
Интерфейсы создаются только при наличии 2+ реализаций.

### Command/Query разделение
- **Commands** (`application/commands/`) — write-операции: авторизация → domain service → gateway → commit
- **Queries** (`application/queries/`) — read-операции: авторизация → gateway.read_all() → read models

### DI через Dishka
- `APP` scope — синглтоны (engine, config)
- `REQUEST` scope — per-request (session, gateways, handlers)

## Stack
- **API**: FastAPI + ORJSONResponse
- **Bot**: aiogram + dishka
- **ORM**: SQLAlchemy async
- **DI**: Dishka
- **IDs**: UUID v7
- **Transactions**: явный TransactionManager.commit()
