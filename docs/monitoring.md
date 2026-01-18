# Мониторинг

## Обзор

Система мониторинга построена на стеке:
- **VictoriaMetrics** - хранение метрик (совместим с Prometheus)
- **Grafana Loki** - хранение и поиск логов
- **Grafana** - визуализация
- **OpenTelemetry** - сбор метрик и логов из приложения
- **Exporters** - сбор метрик из инфраструктуры

## Дашборды

### API Monitoring (`api-monitoring.json`)

Мониторинг HTTP API на основе метрик OpenTelemetry FastAPI.

| Секция | Описание |
|--------|----------|
| **Overview** | Общая статистика: RPS, Error Rate, Avg Latency, Active Requests, Apdex |
| **RED Method** | Rate (запросы/сек), Errors (ошибки/сек), Duration (latency P50/P95/P99) |
| **4 Golden Signals** | Latency, Traffic, Errors, Saturation |
| **Apdex** | Application Performance Index (0-1), где 1 = идеально |
| **Endpoints** | Детализация по эндпоинтам: Top Slowest, Top By Requests, Top By Errors |

**Ключевые метрики:**
- `http_server_duration_milliseconds` - latency запросов
- `http_server_active_requests` - активные запросы

**Пороги:**
- Apdex < 0.9 - жёлтый (есть проблемы)
- Apdex < 0.7 - красный (критично)
- Error Rate > 1% - требует внимания
- P99 Latency > 1s - медленные запросы

---

### PostgreSQL (`postgresql.json`)

Мониторинг базы данных через `postgres_exporter`.

| Секция | Описание |
|--------|----------|
| **Overview** | Connections, Cache Hit Ratio, TPS, Deadlocks, DB Size |
| **Connections** | Активные/Idle соединения, использование пула |
| **Transactions** | Commits/Rollbacks, TPS |
| **Cache & I/O** | Buffer cache hit ratio, блоки чтения |
| **Rows** | Операции с строками (inserted, updated, deleted, fetched) |
| **Database Size** | Размер баз данных |

**Ключевые метрики:**
- `pg_stat_activity_count` - количество соединений
- `pg_stat_database_blks_hit` / `pg_stat_database_blks_read` - cache hit ratio
- `pg_stat_database_xact_commit` / `pg_stat_database_xact_rollback` - транзакции
- `pg_stat_database_deadlocks` - дедлоки

**Пороги:**
- Cache Hit Ratio < 95% - жёлтый
- Cache Hit Ratio < 90% - красный (нужно больше RAM для PostgreSQL)
- Deadlocks > 0 - требует расследования
- Connections > 80% от max - жёлтый

---

### Logs (`logs.json`)

Централизованные логи приложения через Grafana Loki.

| Секция | Описание |
|--------|----------|
| **Overview** | Total Logs, Error/Warning/Info/Debug counts, Logs/min |
| **Log Volume** | График объёма логов по уровням (stacked bars) |
| **Error Analysis** | Error Rate Over Time, Top Error Messages |
| **Live Logs** | Панель логов с поиском в реальном времени |
| **Error Logs** | Отфильтрованные только ошибки (collapsed) |

**Переменные:**
- `service` - фильтр по сервису (service_name)
- `search` - текстовый поиск по логам

**Примеры LogQL запросов:**
```logql
# Все логи сервиса
{service_name="water-delivery"}

# Только ошибки
{service_name="water-delivery"} |~ "(?i)error|exception"

# Поиск по тексту
{service_name="water-delivery"} |= "user_id=123"

# Логи за последние 5 минут с уровнем ERROR
{service_name="water-delivery"} | json | level="ERROR"
```

**Retention:** 24 часа (настраивается в `configs/loki/loki-config.yaml`)

---

### Redis (`redis.json`)

Мониторинг Redis через `redis_exporter`.

| Секция | Описание |
|--------|----------|
| **Overview** | Uptime, Clients, Hit Rate, Used Memory, Total Keys, Commands/sec |
| **Memory** | Used/RSS/Peak Memory, Fragmentation Ratio |
| **Clients & Connections** | Connected/Blocked Clients, Connections Rate |
| **Commands & Performance** | Commands/sec, Cache Hit Ratio, Hits & Misses |
| **Keys** | Keys by Database, Expired & Evicted Keys |
| **Network** | Network I/O |

**Ключевые метрики:**
- `redis_memory_used_bytes` - используемая память
- `redis_connected_clients` - подключённые клиенты
- `redis_keyspace_hits_total` / `redis_keyspace_misses_total` - cache hit ratio
- `redis_evicted_keys_total` - вытесненные ключи (память закончилась)

**Пороги:**
- Cache Hit Ratio < 95% - жёлтый
- Cache Hit Ratio < 90% - красный
- Memory Fragmentation Ratio > 1.5 - проблема с фрагментацией
- Evicted Keys > 0 - Redis не хватает памяти

---

### Containers (`containers.json`)

Мониторинг Docker контейнеров через `cAdvisor`.

| Секция | Описание |
|--------|----------|
| **Overview** | Running Containers, Total CPU, Total Memory, Network RX/TX |
| **CPU** | CPU Usage по контейнерам |
| **Memory** | Memory Usage, Working Set по контейнерам |
| **Network** | Network Receive/Transmit по контейнерам |
| **Disk I/O** | Disk Read/Write по контейнерам |

**Ключевые метрики:**
- `container_cpu_usage_seconds_total` - CPU usage
- `container_memory_usage_bytes` - Memory usage
- `container_network_receive_bytes_total` - Network RX
- `container_fs_reads_bytes_total` / `container_fs_writes_bytes_total` - Disk I/O

**Пороги:**
- CPU > 80% - контейнер перегружен
- Memory близко к лимиту - риск OOM Kill

---

### Server (`node.json`)

Мониторинг сервера/хоста через `node_exporter`.

| Секция | Описание |
|--------|----------|
| **Overview** | Uptime, CPU Usage, Memory Usage, Disk Usage /, Load 1m, Total RAM |
| **CPU** | CPU Usage (User/System/IOWait/Idle), System Load |
| **Memory** | Memory Usage (Used/Available/Cached/Buffers), Swap |
| **Disk** | Disk Usage by Mountpoint, Disk I/O, Disk IOPS |
| **Network** | Network Traffic, Network Errors & Drops |

**Ключевые метрики:**
- `node_cpu_seconds_total` - CPU usage по режимам
- `node_memory_MemAvailable_bytes` - доступная память
- `node_filesystem_avail_bytes` - свободное место на диске
- `node_load1` / `node_load5` / `node_load15` - system load

**Пороги:**
- CPU > 70% - жёлтый, > 90% - красный
- Memory > 70% - жёлтый, > 90% - красный
- Disk > 70% - жёлтый, > 90% - красный (критично!)
- Load > количества CPU - система перегружена

---

## Запуск на сервере

### Стандартный запуск

```bash
docker compose up -d
```

### С node_exporter (только Linux)

```bash
docker compose --profile linux up -d
```

---

## Установка node_exporter на Linux сервере

### Вариант 1: Через Docker (уже настроено)

```bash
docker compose --profile linux up -d
```

### Вариант 2: Нативная установка (рекомендуется для прода)

Нативная установка даёт более точные метрики и меньший overhead.

#### Ubuntu/Debian

```bash
# Установка
sudo apt update
sudo apt install prometheus-node-exporter

# Запуск и автозапуск
sudo systemctl enable --now prometheus-node-exporter

# Проверка
curl http://localhost:9100/metrics | head
```

#### CentOS/RHEL/Fedora

```bash
# Установка
sudo dnf install golang-github-prometheus-node-exporter

# Запуск и автозапуск
sudo systemctl enable --now node_exporter

# Проверка
curl http://localhost:9100/metrics | head
```

#### Ручная установка (любой Linux)

```bash
# Скачать последнюю версию
VERSION="1.8.2"
wget https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/node_exporter-${VERSION}.linux-amd64.tar.gz

# Распаковать
tar xvfz node_exporter-${VERSION}.linux-amd64.tar.gz
sudo mv node_exporter-${VERSION}.linux-amd64/node_exporter /usr/local/bin/

# Создать systemd сервис
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Запустить
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

# Проверить
sudo systemctl status node_exporter
curl http://localhost:9100/metrics | head
```

### Настройка scrape в VictoriaMetrics

После установки node_exporter, убедитесь что в `configs/vm/scrape.yml` есть:

```yaml
- job_name: "node"
  static_configs:
    - targets: ["host.docker.internal:9100"]
```

Если node_exporter установлен нативно (не в Docker), и VictoriaMetrics в Docker, то `host.docker.internal` резолвится в IP хоста благодаря настройке `extra_hosts` в docker-compose.

### Проверка что метрики собираются

1. Проверить что node_exporter отвечает:
```bash
curl http://localhost:9100/metrics | grep node_cpu
```

2. Проверить что VictoriaMetrics скрейпит:
```bash
curl "http://localhost:8428/api/v1/targets" | jq '.data.activeTargets[] | select(.labels.job=="node")'
```

3. Открыть Grafana → Server dashboard