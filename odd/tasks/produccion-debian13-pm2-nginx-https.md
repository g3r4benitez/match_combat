# Producción Debian 13 — PM2 + nginx + HTTPS

Objetivo: dejar el proyecto listo para desplegarse en Debian 13 con PM2, nginx, HTTPS y el redirect del puerto 9009 hacia `/api`.
Rama: `feat/produccion-debian13` | Estrategia de entrega: `single-pr` (sin PR remoto) | Runner: no aplica (configuración/infra); verificación con `bash -n`, `openssl`, `node --check` y `nginx -t`.

## Specs

- S1: El proyecto FastAPI se despliega en un servidor Debian 13.
- S2: La API se ejecuta con PM2.
- S3: nginx actúa como reverse proxy.
- S4: La API corre en el puerto 9009 (uvicorn, solo loopback).
- S5: Las llamadas a `http(s)://192.168.1.46:9009` se redirigen a `http(s)://192.168.1.46/api`.
- S6: El servidor queda configurado para HTTPS.
- S7: Se incluyen scripts para crear los certificados necesarios.
- S8: El `README.md` documenta todo el proceso de preparación de producción y los pasos para ejecutar la API con PM2.

## Tasks

- T1 — `deploy/nginx/`: template de nginx con TLS 443, redirect 9009 y proxy `/api` a `127.0.0.1:9009`. [S3,S4,S5,S6]
- T2 — `scripts/generate-certs.sh`: CA local + certificado de servidor con SAN IP. [S6,S7]
- T3 — `scripts/install-nginx-config.sh` + `scripts/setup-production.sh`: render, validación y bootstrap Debian 13. [S1,S3,S6]
- T4 — `ecosystem.config.js` + `deploy/env.production.example`: PM2 seguro en loopback y variables de producción. [S2,S4]
- T5 — `README.md`: guía completa de producción. [S8]
- T6 — Verificación estructural y funcional (certificados, sintaxis nginx, redirect/proxy). [S1..S8]

## Log

### L1 — Pedido original (verbatim)

```
este proyecto FastAPI tiene que ser desplegado en un servidor con debian 13, crear la configuracion para ejecutar la api con pm2, nginx, la api debe correr en el puerto 9009, pero las llamadas a la api deben manejarse con este redireccionamiento http(s)://192.168.1.46:9009 a http(s)://192.168.1.46/api

crear lo necesario para que servidor este configurado para llamadas https, crear los scripts para crear los certificados necesarios. 

Documentar en el archivo README.md todo el proceso de preparación del entorno de producción, asi como los pasos para ejecutar la api con pm2
```

### L2 — Análisis y decisiones

- La app ya expone todas sus rutas bajo `/api` (`app/api/routes/router.py`), por lo que nginx no debe reescribir el prefijo: `proxy_pass http://127.0.0.1:9009` conserva el URI.
- Para cumplir S4 y S5 a la vez: uvicorn escucha en `127.0.0.1:9009` y nginx escucha en `192.168.1.46:9009` para el redirect. Son sockets distintos (loopback vs IP LAN), por lo que no colisionan.
- `https://192.168.1.46:9009` no se puede servir junto con HTTP plano en el mismo puerto: nginx no multiplexa TLS y texto plano. TLS se termina en 443 y el 9009 es HTTP→HTTPS (documentado en README).
- Certificado: Let's Encrypt no emite para IP privada. Se usa una CA local + certificado de servidor con `subjectAltName` IP; el cliente debe confiar en `ca.crt`.
- `app/core/config.py` construye `DB_URL` desde `DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME`; la variable `DB_URL` del `.env` es ignorada por el código actual. Se documenta.
- `app/core/config.py` lee `.env` desde `os.getcwd()`, por eso `ecosystem.config.js` fija `cwd: __dirname`.
- `ecosystem.config.js` tenía secretos hardcodeados; se eliminan y se dejan en `.env` (permisos 600).
- Mirror en Engram: pendiente (herramientas de memoria no disponibles en este runtime).

### L3 — Evidencia de verificación

- `bash -n` y `shellcheck` sobre los tres scripts: sin errores.
- `openssl`: CA + servidor generados; `openssl verify` devuelve `OK`; SAN confirmado con `IP:192.168.1.46, IP:127.0.0.1, DNS:match-combat.local, DNS:localhost`.
- `node --check ecosystem.config.js`: OK.
- `nginx -t` con la plantilla renderizada y el snippet instalado (contenedor `nginx:bookworm`): OK.
- Prueba funcional con nginx `--network host` y un backend dummy en `127.0.0.1:9009`:
  - `http://127.0.0.2:80/api/ping` → `308 https://127.0.0.2/api/ping`.
  - `http://127.0.0.2:9009/` → `308 https://127.0.0.2/api`.
  - `http://127.0.0.2:9009/api/ping` → `308 https://127.0.0.2/api/ping` (también con `POST`, método preservado).
  - `https://127.0.0.2/api/ping` → `"pong"` vía proxy.
  - `https://127.0.0.2/docs` → respuesta del backend vía proxy.
- Decisión de runtime: Debian 13 usa Python 3.13; se comprobó que `greenlet==3.0.3` y `pandas==2.2.2` no tienen wheels `cp313`, por lo que el bootstrap provisiona Python 3.11 con `uv`.
- `psycopg2-binary` agregado a `requirements.txt`: sin él un virtualenv nuevo no puede abrir PostgreSQL.
