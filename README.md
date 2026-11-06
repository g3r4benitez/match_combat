# Match Combat - Gerardo Benitez

Un proyecto que pretende resolver la problemática de buscar oponentes para
eventos de deportes de contacto, dada una lista de competidores y basándose en
criterios como el sexo, el peso y la experiencia, para seleccionar las mejores
opciones para cada competidor, crear los matches y sacar de las opciones a los
competidores que ya tienen pelea armada.

**Stack:** FastAPI · SQLModel (SQLAlchemy) · PostgreSQL / SQLite · Docker ·
PM2 · nginx

---

## Quick path: producción en Debian 13

En el servidor Debian 13, como usuario de despliegue:

```bash
# 1. Obtener el código
sudo apt update && sudo apt install -y git
sudo mkdir -p /opt/match_combat && sudo chown "$USER":"$USER" /opt/match_combat
git clone <repo-url> /opt/match_combat
cd /opt/match_combat

# 2. Instalar todo (nginx, PM2, Python 3.11, certificados, sitio nginx)
sudo env SERVER_IP=192.168.1.46 ./scripts/setup-production.sh

# 3. Editar variables de producción (DB, JWT, admin)
nano .env

# 4. Arrancar la API con PM2
pm2 start ecosystem.config.js --env production
pm2 save

# 5. Verificar
curl -k https://192.168.1.46/api/ping
```

Resultado esperado:

| URL | Resultado |
|---|---|
| `https://192.168.1.46/api/ping` | `"pong"` |
| `https://192.168.1.46/docs` | Swagger UI |
| `http://192.168.1.46:9009` | `308` → `https://192.168.1.46/api` |
| `http://192.168.1.46:9009/api/ping` | `308` → `https://192.168.1.46/api/ping` |
| `http://192.168.1.46/api/ping` | `308` → `https://192.168.1.46/api/ping` |

El resto de este documento explica cada paso, los certificados, la operación
diaria y la resolución de problemas.

---

## Requirements

- Python 3.11+ (la instalación de producción provisiona 3.11 automáticamente)
- PostgreSQL 14+ (o SQLite para desarrollo)
- Node.js + PM2 (solo producción)
- nginx (solo producción)

---

## Desarrollo local

### Setup del entorno

1. Copiar `.env.example` a `.env`.
2. Completar las variables de entorno.

### Opción 1: Docker

```bash
docker-compose up
```

### Opción 2: manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a
source .env
set +a
uvicorn app.main:app --host 0.0.0.0 --port 9009 --reload

# Opcional: varios workers
gunicorn -w "$(nproc)" -k uvicorn.workers.UvicornWorker app.main:app
```

### Opción 3: PM2 en desarrollo

```bash
pm2 start ./.venv/bin/uvicorn --name "match-combat" -- app.main:app --host 0.0.0.0 --port 9009
```

> En producción **no** uses `--host 0.0.0.0`: el `ecosystem.config.js` ya fija
> `127.0.0.1:9009` para que solo nginx exponga la API.

---

## Producción en Debian 13

### Arquitectura

```text
LAN / Internet
      │
      │  http://192.168.1.46:9009/...      nginx :9009
      │        └── 308 ──> https://192.168.1.46/...
      │
      │  http://192.168.1.46/...           nginx :80
      │        └── 308 ──> https://192.168.1.46/...
      │
      ▼
nginx :443 (TLS)
      ├── /api/  ──────────────> 127.0.0.1:9009  (uvicorn + PM2)
      ├── /docs  ──────────────> 127.0.0.1:9009
      ├── /redoc ──────────────> 127.0.0.1:9009
      └── /openapi.json ───────> 127.0.0.1:9009
```

La aplicación ya monta todas sus rutas bajo `/api`
(`app/api/routes/router.py`), por lo que nginx **no reescribe** el prefijo:
`proxy_pass http://127.0.0.1:9009` conserva el URI original.

### Puertos y URLs

| Puerto | Proceso | Exposición | Función |
|---|---|---|---|
| `80` | nginx | LAN | Redirige a HTTPS |
| `443` | nginx | LAN | TLS + reverse proxy a `/api` |
| `9009` | nginx | LAN | Redirige a `https://IP/api` |
| `9009` | uvicorn | Solo loopback | Aplicación FastAPI |

`http://192.168.1.46:9009` y `127.0.0.1:9009` son sockets distintos (IP LAN vs
loopback), por eso nginx y uvicorn pueden usar el mismo número de puerto sin
colisionar. Desde el propio servidor, `http://127.0.0.1:9009` llega directo a
uvicorn (útil para depurar); desde la LAN, `http://192.168.1.46:9009` pasa por
nginx y redirige a `https://192.168.1.46/api`.

> **Nota sobre `https://192.168.1.46:9009`:** nginx no puede servir TLS y HTTP
> plano en el mismo puerto. TLS se termina en `443`; el puerto `9009` es
> únicamente el redirect HTTP→HTTPS. Usa siempre
> `https://192.168.1.46/api`.

### 1. Preparar el servidor

```bash
sudo apt update && sudo apt install -y git
sudo mkdir -p /opt/match_combat && sudo chown "$USER":"$USER" /opt/match_combat
git clone <repo-url> /opt/match_combat
cd /opt/match_combat

sudo env SERVER_IP=192.168.1.46 ./scripts/setup-production.sh
```

El script realiza, de forma idempotente:

1. Instala `nginx`, `openssl`, `python3`, `python3-venv`, `build-essential`,
   `git` y utilidades de compilación.
2. Instala Node.js 20 (NodeSource) y PM2 si no existen.
3. Crea `.venv` con **Python 3.11**. Debian 13 trae Python 3.13, pero las
   dependencias fijadas (`greenlet==3.0.3`, `pandas==2.2.2`) no tienen wheels
   para 3.13; el script instala `uv` y provisiona 3.11 automáticamente.
4. Instala `requirements.txt` en el virtualenv.
5. Crea `.env` desde `deploy/env.production.example` (si no existe) con permisos
   `600`.
6. Genera la CA local y el certificado del servidor.
7. Renderiza e instala la configuración de nginx y valida con `nginx -t`.
8. Registra PM2 en systemd para que arranque al reiniciar.

Variables disponibles:

| Variable | Default | Descripción |
|---|---|---|
| `SERVER_IP` | `192.168.1.46` | IP LAN del servidor |
| `SERVER_NAME` | `$SERVER_IP` | `server_name` de nginx |
| `APP_USER` | `$SUDO_USER` | Usuario que ejecuta PM2 |
| `CERT_DIR` | `/etc/nginx/ssl/match-combat` | Directorio de certificados |
| `PYTHON_VERSION` | `3.11` | Versión del virtualenv |
| `START_APP` | `0` | `1` arranca la API al finalizar (se ignora si `.env` acaba de crearse o contiene `CHANGE_ME_`) |
| `SKIP_APT` | `0` | `1` omite `apt` |
| `SKIP_NODE` | `0` | `1` omite Node.js/PM2 |

> El bootstrap descarga el repositorio de NodeSource y el instalador de `uv`.
> Si tu política no permite ejecutar instaladores remotos, instala Node.js,
> PM2 y Python 3.11 por tu cuenta y vuelve a ejecutar con `SKIP_NODE=1`.

Para arrancar la API en el mismo paso:

```bash
sudo env SERVER_IP=192.168.1.46 START_APP=1 ./scripts/setup-production.sh
```

> Si `.env` se acaba de crear o todavía contiene valores `CHANGE_ME_`, el
> script ignora `START_APP=1` a propósito para no arrancar la API con
> credenciales de ejemplo. Edita `.env` y arranca PM2 manualmente.

### 2. Variables de entorno

```bash
cp deploy/env.production.example .env   # solo si setup no lo creó
chmod 600 .env
nano .env
```

Variables mínimas a cambiar:

| Variable | Ejemplo | Nota |
|---|---|---|
| `DB_USER` | `match_user` | Usuario PostgreSQL |
| `DB_PASSWORD` | contraseña larga | **Cambiar** |
| `DB_NAME` | `match_combat` | Base de datos |
| `DB_HOST` | `127.0.0.1` | Host de PostgreSQL |
| `DB_PORT` | `5432` | Puerto |
| `JWT_SECRET_KEY` | cadena aleatoria larga | **Cambiar** |
| `ADMIN_PASSWORD` | contraseña segura | **Cambiar** |
| `ADMIN_EMAIL` | `admin@dominio` | Correo del admin inicial |
| `IS_DEBUG` | `False` | En producción siempre `False` |

> **Importante:** `app/core/config.py` construye la URL de conexión desde
> `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_NAME`. La variable
> `DB_URL` del `.env` **no se usa** en el código actual; se mantiene solo por
> compatibilidad con otras herramientas.

El archivo `.env` se lee desde el directorio de trabajo del proceso. PM2 fija
`cwd: __dirname` en `ecosystem.config.js`, por eso debe vivir en la raíz del
proyecto.

### 3. Base de datos

El script **no instala PostgreSQL**. Puedes usar un servidor existente
(incluido Supabase) o instalarlo localmente:

```bash
sudo apt install -y postgresql
sudo -u postgres psql -c "CREATE USER match_user WITH PASSWORD 'CAMBIA_ESTO';"
sudo -u postgres psql -c "CREATE DATABASE match_combat OWNER match_user;"
```

Luego ajusta `DB_*` en `.env`. Las migraciones de Alembic se ejecutan
automáticamente al arrancar la aplicación (`app/core/database.py:init_db()`).

### 4. Certificados TLS

Let's Encrypt y las CA públicas **no emiten certificados para IPs privadas**
como `192.168.1.46`. Por eso el proyecto usa una CA local y un certificado de
servidor con `subjectAltName` para la IP.

```bash
sudo env SERVER_IP=192.168.1.46 ./scripts/generate-certs.sh
```

Genera en `/etc/nginx/ssl/match-combat`:

| Archivo | Uso |
|---|---|
| `ca.crt` | CA local; se importa en los clientes |
| `ca.key` | Clave privada de la CA (`600`, no distribuir) |
| `server.crt` | Certificado del servidor |
| `server.key` | Clave privada del servidor (`600`) |

El SAN incluye `IP:192.168.1.46`, `IP:127.0.0.1`, `DNS:<primer valor de SERVER_NAME>`
y `DNS:localhost`. Si `SERVER_NAME` tiene varios nombres separados por espacios,
el certificado usa el primero como CN/SAN DNS y nginx los usa todos. El script
verifica la cadena con `openssl verify`.

**Confiar en la CA en los clientes** (evita el aviso del navegador):

```bash
# Debian/Ubuntu
sudo cp /etc/nginx/ssl/match-combat/ca.crt /usr/local/share/ca-certificates/match-combat.crt
sudo update-ca-certificates

# Windows: importar ca.crt en "Entidades de certificación raíz de confianza"
# macOS:  Llavero -> Sistema -> importar ca.crt -> Confiar siempre
```

Regenerar (los clientes deben volver a confiar en la nueva CA):

```bash
sudo env SERVER_IP=192.168.1.46 FORCE=1 ./scripts/generate-certs.sh
sudo systemctl reload nginx
```

El `reload` es obligatorio: nginx mantiene en memoria el certificado anterior
hasta que se recarga, aunque los archivos en disco ya sean los nuevos.

> Si en el futuro usas un **dominio DNS** que apunte a esta IP, puedes usar
> Let's Encrypt con `certbot` en lugar de la CA local.

### 5. nginx

El script de setup ya instala y recarga nginx. Para reinstalar solo el sitio:

```bash
sudo env SERVER_IP=192.168.1.46 ./scripts/install-nginx-config.sh
```

Archivos:

| Archivo | Destino | Función |
|---|---|---|
| `deploy/nginx/match-combat.conf.template` | `/etc/nginx/sites-available/match-combat.conf` | Sitios 80/443/9009 |
| `deploy/nginx/proxy-headers.conf` | `/etc/nginx/snippets/match-combat-proxy-headers.conf` | Headers `X-Forwarded-*` |

Validación manual:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx
```

Comportamiento del redirect:

```text
http://192.168.1.46:9009            -> 308 https://192.168.1.46/api
http://192.168.1.46:9009/api/ping   -> 308 https://192.168.1.46/api/ping
http://192.168.1.46/api/ping        -> 308 https://192.168.1.46/api/ping
https://192.168.1.46/               -> 302 https://192.168.1.46/api
```

> nginx escucha en `SERVER_IP:9009`. Si cambia la IP del servidor, vuelve a
> ejecutar `install-nginx-config.sh` con el nuevo `SERVER_IP`; de lo contrario
> nginx fallará al recargar porque la IP ya no existe.

### 6. Ejecutar la API con PM2

```bash
cd /opt/match_combat

pm2 start ecosystem.config.js --env production
pm2 status
pm2 logs match-combat
```

Comandos de operación:

| Acción | Comando |
|---|---|
| Ver estado | `pm2 status` |
| Ver logs en vivo | `pm2 logs match-combat` |
| Reiniciar | `pm2 restart match-combat --update-env` |
| Recargar (con 1 instancia fork equivale a reiniciar el worker) | `pm2 reload match-combat --update-env` |
| Detener | `pm2 stop match-combat` |
| Eliminar | `pm2 delete match-combat` |
| Guardar proceso actual | `pm2 save` |
| Configurar arranque al boot | `sudo pm2 startup systemd -u "$USER" --hp "$HOME"` |
| Monitoreo | `pm2 monit` |

`ecosystem.config.js` define:

- `script: ./.venv/bin/python` con `-m uvicorn app.main:app`
- `--host 127.0.0.1 --port 9009` (solo loopback)
- `--proxy-headers --forwarded-allow-ips=127.0.0.1` para que FastAPI respete
  `X-Forwarded-Proto` de nginx
- `cwd: __dirname` para leer `.env`
- Logs en `logs/pm2-out.log` y `logs/pm2-error.log`
- Reinicio automático y límite de memoria de 512 MB

Después de arrancar por primera vez:

```bash
pm2 save
pm2 startup systemd -u "$USER" --hp "$HOME"
```

> `pm2 save` es obligatorio: sin él, el servicio de systemd arranca sin
> procesos después de un reinicio.

### 7. Verificación

```bash
# API a través de nginx
curl -k https://192.168.1.46/api/ping
# "pong"

# Redirect del puerto 9009
curl -I http://192.168.1.46:9009
# HTTP/1.1 308 Permanent Redirect
# Location: https://192.168.1.46/api

curl -I http://192.168.1.46:9009/api/ping
# Location: https://192.168.1.46/api/ping

# Redirect de HTTP a HTTPS
curl -I http://192.168.1.46/api/ping
# Location: https://192.168.1.46/api/ping

# Documentación
curl -k https://192.168.1.46/docs

# Login
curl -k -X POST https://192.168.1.46/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=TU_PASSWORD"
```

Una vez que importaste `ca.crt` en el cliente, los `curl` funcionan sin `-k` y
el navegador no muestra advertencias.

### 8. Firewall

```bash
sudo apt install -y ufw
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 9009/tcp   # necesario solo si usas el redirect desde la LAN
sudo ufw enable
sudo ufw status
```

Si no necesitas el redirect del puerto 9009, no abras `9009` y usa únicamente
`https://192.168.1.46/api`.

### 9. Operación y actualizaciones

```bash
cd /opt/match_combat
git pull

# Si cambió requirements.txt
.venv/bin/pip install -r requirements.txt
# o, si se instaló con uv:
# uv pip install --python .venv/bin/python -r requirements.txt

pm2 restart match-combat --update-env
pm2 save
```

> Con `instances: 1` y `exec_mode: "fork"`, PM2 no puede hacer un reload
> rolling: `pm2 reload` y `pm2 restart` reinician el único worker y hay una
> ventana breve de downtime (nginx responde `502`). Para cero downtime real
> necesitarías balanceo con varios procesos o un segundo servidor.

Las migraciones de base de datos se aplican solas al arrancar la aplicación.

Logs:

| Origen | Ubicación |
|---|---|
| Aplicación (rotativo) | `/tmp/logs/app.log` |
| PM2 stdout | `logs/pm2-out.log` |
| PM2 stderr | `logs/pm2-error.log` |
| PM2 en vivo | `pm2 logs match-combat` |
| systemd (arranque PM2) | `journalctl -u "pm2-$USER"` |

> `/tmp/logs/app.log` es efímero: se pierde al reiniciar el servidor. Usa
> `pm2 logs` o configura un colector de logs si necesitas retención.
>
> Los archivos `logs/pm2-*.log` no rotan por defecto. Instala el módulo de
> rotación una vez: `pm2 install pm2-logrotate`.

### 10. Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `502 Bad Gateway` | La API no está corriendo | `pm2 status`, `pm2 logs match-combat` |
| `502` y el log dice `connection refused` | uvicorn no escucha en `127.0.0.1:9009` | Revisa `ecosystem.config.js` y reinicia PM2 |
| `pm2 start` falla por módulo `psycopg2` | Dependencia no instalada | `.venv/bin/pip install -r requirements.txt` |
| nginx no recarga: `cannot assign requested address` | `SERVER_IP` ya no existe en el servidor | Reejecuta `install-nginx-config.sh` con la IP correcta |
| nginx no arranca: `address already in use` en 9009 | uvicorn está en `0.0.0.0:9009` | Usa `ecosystem.config.js` (loopback) y `pm2 delete` el proceso viejo |
| Advertencia de certificado en el navegador | La CA local no está instalada en el cliente | Importa `ca.crt` (ver sección 4) |
| `pip install` falla compilando `greenlet`/`pandas` | Se usó Python 3.13 | Reejecuta `setup-production.sh`; debe crear `.venv` con 3.11 |
| `could not connect to server` (PostgreSQL) | DB mal configurada o apagada | Revisa `DB_*` en `.env` y `systemctl status postgresql` |
| PM2 no arranca tras reiniciar | Falta `pm2 save` o `pm2 startup` | `pm2 save` y `pm2 startup systemd -u "$USER" --hp "$HOME"` |
| `.env` no se lee | PM2 arrancó desde otro `cwd` | Usa `ecosystem.config.js` (fija `cwd`) |

### 11. Checklist de seguridad

- [ ] `JWT_SECRET_KEY` cambiado por una cadena aleatoria larga.
- [ ] `ADMIN_PASSWORD` cambiado.
- [ ] `IS_DEBUG=False`.
- [ ] `.env` con permisos `600` y dueño del usuario de la app.
- [ ] `ca.key` y `server.key` con permisos `600`.
- [ ] La API escucha solo en `127.0.0.1:9009`.
- [ ] Firewall limita los puertos expuestos (80, 443 y 9009 si aplica).
- [ ] La CA local se distribuye solo a clientes de confianza.
- [ ] `pm2 startup` + `pm2 save` verificados con un reinicio de prueba.

---

## Backup y restore de la base de datos

Backup:

```bash
pg_dump -h 127.0.0.1 -p 5432 -U match_user match_combat > backup_match_combat_$(date +%F).sql
```

Restore:

```bash
psql -h 127.0.0.1 -p 5432 -U match_user -d match_combat -f backup_match_combat_2026-11-06.sql
```

---

## API

### Probar con curl

```bash
curl -k --location --request POST 'https://192.168.1.46/api/notification' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "category": "films",
    "message": "Dec 24, world premiere of the movie Avatar 3"
  }'
```

### Documentación

- Swagger UI: `https://192.168.1.46/docs`
- ReDoc: `https://192.168.1.46/redoc`
- OpenAPI: `https://192.168.1.46/openapi.json`

---

## Archivos de despliegue

```text
deploy/
├── env.production.example          # Plantilla de variables de producción
└── nginx/
    ├── match-combat.conf.template  # Sitio nginx (80/443/9009)
    └── proxy-headers.conf          # Headers X-Forwarded-*

scripts/
├── setup-production.sh             # Bootstrap completo Debian 13
├── generate-certs.sh               # CA local + certificado del servidor
└── install-nginx-config.sh         # Render, validación y recarga de nginx

ecosystem.config.js                 # Configuración PM2
```

---

## Notas históricas

- `DEPLOYMENT.md` describe un despliegue alternativo en AWS (App Runner + RDS +
  S3 + Terraform). No es necesario para el despliegue en Debian 13 de este
  documento.
- `scripts/deploy.sh` corresponde a ese flujo AWS (ECR + App Runner) y no se usa
  en el despliegue con PM2/nginx.
