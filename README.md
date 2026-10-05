# User CRUD Monitoring

API REST de usuarios con **FastAPI** y **PostgreSQL**, monitoreada con **Prometheus** y **Grafana**. Todo corre en contenedores Docker orquestados con Docker Compose.

## Arquitectura

```
POST /users → FastAPI → PostgreSQL
                 ↓ /metrics
            Prometheus (scrape cada 5 s)
                 ↓
              Grafana (dashboards)
```

| Servicio | Imagen | Puerto | Redes |
|---|---|---|---|
| `postgres` | `postgres:13` | (interno) 5432 | `backend` |
| `fastapi` | build local (`Dockerfile`) | 8000 | `backend`, `analisis` |
| `prometheus` | `prom/prometheus` | 9090 | `analisis` |
| `grafana` | `grafana/grafana` | 3000 | `analisis` |

Se usan dos redes para aislar la base de datos: Prometheus y Grafana no pueden llegar a PostgreSQL. `fastapi` está en ambas y hace de puente.

## Estructura del proyecto

```
user-crud-monitoring/
├── docker-compose.yml
├── Dockerfile
├── seed.py
├── Practica_1_Docker_Guide.pdf
├── README.md
├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── database.py
│       └── models.py
├── grafana/
│   ├── Dashboard_Grafana.json
│   ├── Dashboard_2.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── datasource.yml
└── prometheus/
    └── prometheus.yml
```

## Requisitos

- Docker Desktop (con Docker Compose v2)

## Puesta en marcha

```bash
docker compose up -d --build
docker compose ps
```

Los cuatro servicios deben quedar en estado *running* y `postgres` en *healthy*.

Para detener todo:

```bash
docker compose down        # conserva los datos
docker compose down -v     # borra también los volúmenes (datos de Postgres y Grafana)
```

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/users` | Lista todos los usuarios |
| POST | `/users?name=...&age=...` | Crea un usuario |
| GET | `/metrics` | Métricas en formato Prometheus |
| GET | `/docs` | Documentación interactiva (Swagger) |

## Pruebas de la API

En PowerShell usa `curl.exe` (`curl` es un alias de otro comando):

```powershell
# Crear un usuario
curl.exe -X POST "http://localhost:8000/users?name=Alice&age=25"

# Listar usuarios
curl.exe -X GET "http://localhost:8000/users"

# Ver la métrica personalizada
curl.exe http://localhost:8000/metrics | findstr user_created
```

Crear varios usuarios automáticamente con el script incluido (requiere `pip install requests`):

```bash
python seed.py
```

Verificar en la base de datos:

```bash
docker exec -it postgres psql -U user -d mydb -c "SELECT * FROM users;"
```

## Monitoreo

### Prometheus

- Interfaz: <http://localhost:9090>
- Estado de los targets: <http://localhost:9090/targets> (`fastapi:8000` debe estar en **UP**)
- Configuración: `prometheus/prometheus.yml`

### Métricas disponibles

| Métrica | Descripción |
|---|---|
| `user_created_total` | Usuarios creados desde que arrancó la app (contador propio) |
| `process_resident_memory_bytes` | Memoria RAM usada por la app |
| `process_cpu_seconds_total` | CPU consumida (usar `rate(...[1m])`) |
| `process_open_fds` | Archivos y conexiones abiertas |
| `process_start_time_seconds` | Momento de arranque (para calcular el tiempo de funcionamiento) |
| `up` | 1 si Prometheus puede leer el target, 0 si no |

Nota: `user_created_total` vive en memoria. Si se reinicia el contenedor `fastapi`, vuelve a 0 aunque los usuarios sigan en la base de datos.

### Grafana

- Interfaz: <http://localhost:3000>
- Usuario: `admin` / Contraseña: `admin`
- Fuente de datos: Prometheus (`http://prometheus:9090`)

Dashboards exportados como JSON en la carpeta `grafana/`:

- `Dashboard_Grafana.json`
- `Dashboard_2.json`

Para importarlos: **Dashboards → New → Import → Upload dashboard JSON file**. Si se copian a `grafana/provisioning/dashboards/`, Grafana los carga solo al arrancar.

## Ejecución manual (sin Compose)

```bash
docker network create mired

docker run --name postgres --network mired \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mydb \
  -v pgdata:/var/lib/postgresql/data -d postgres:13

docker build -t mi_app .
docker run --name api --network mired -p 8000:8000 -d mi_app

docker run --name prometheus --network mired -p 9090:9090 \
  -v ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml -d prom/prometheus

docker run --name grafana --network mired -p 3000:3000 -d grafana/grafana
```

En este modo, el target de `prometheus.yml` debe ser `api:8000` (el nombre del contenedor). Con Compose es `fastapi:8000` (el nombre del servicio).

En PowerShell, escribe cada comando en una sola línea o usa el acento grave `` ` `` como continuación de línea (no `\`).

## Tecnologías

FastAPI · SQLAlchemy · PostgreSQL · Prometheus · Grafana · Docker · Docker Compose
