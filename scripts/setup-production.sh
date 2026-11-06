#!/usr/bin/env bash
#
# Bootstrap the Match Combat production stack on Debian 13 (trixie):
#   - system packages (nginx, openssl, Python build tooling)
#   - Node.js + PM2
#   - Python 3.11 virtualenv (required by the pinned dependencies)
#   - TLS certificates (local CA)
#   - nginx site configuration
#   - PM2 systemd startup entry
#
# Usage:
#   sudo SERVER_IP=192.168.1.46 ./scripts/setup-production.sh
#   sudo SERVER_IP=192.168.1.46 START_APP=1 ./scripts/setup-production.sh
#
# Environment variables:
#   SERVER_IP      LAN IP of the server (default 192.168.1.46)
#   SERVER_NAME    nginx server_name values (default $SERVER_IP)
#   APP_USER       User that runs PM2 (default: SUDO_USER)
#   CERT_DIR       TLS certificate directory (default /etc/nginx/ssl/match-combat)
#   PYTHON_VERSION Python version for the virtualenv (default 3.11)
#   START_APP      1 = start the app with PM2 after setup (default 0)
#   SKIP_APT       1 = skip apt package installation
#   SKIP_NODE      1 = skip Node.js/PM2 installation

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_IP="${SERVER_IP:-192.168.1.46}"
SERVER_NAME="${SERVER_NAME:-$SERVER_IP}"
CERT_DIR="${CERT_DIR:-/etc/nginx/ssl/match-combat}"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
START_APP="${START_APP:-0}"
SKIP_APT="${SKIP_APT:-0}"
SKIP_NODE="${SKIP_NODE:-0}"
APP_USER="${APP_USER:-${SUDO_USER:-}}"

log() { printf '\n==> %s\n' "$*"; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Run as root: sudo $0"
[ -n "$APP_USER" ] || die "Set APP_USER or run with sudo as the deploy user"
id "$APP_USER" >/dev/null 2>&1 || die "User does not exist: $APP_USER"
APP_HOME="$(getent passwd "$APP_USER" | cut -d: -f6)"
[ -n "$APP_HOME" ] || die "Cannot resolve home directory for $APP_USER"

if ! printf '%s' "$SERVER_IP" | grep -Eq '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'; then
    die "SERVER_IP must be an IPv4 address, got: $SERVER_IP"
fi

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
if [ "$SKIP_APT" != "1" ]; then
    log "Installing system packages"
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        openssl \
        nginx \
        python3 \
        python3-venv \
        python3-pip \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev \
        liblzma-dev \
        git
fi

# ---------------------------------------------------------------------------
# 2. Node.js + PM2
# ---------------------------------------------------------------------------
if [ "$SKIP_NODE" != "1" ]; then
    if ! command -v node >/dev/null 2>&1; then
        log "Installing Node.js 20 from NodeSource"
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
    fi

    command -v node >/dev/null 2>&1 || die "Node.js installation failed"
    command -v npm >/dev/null 2>&1 || die "npm is not available"

    if ! command -v pm2 >/dev/null 2>&1; then
        log "Installing PM2"
        npm install -g pm2
    fi
fi

command -v pm2 >/dev/null 2>&1 || die "PM2 is not available (set SKIP_NODE=0)"

# ---------------------------------------------------------------------------
# 3. Python virtualenv
#
# Debian 13 ships Python 3.13, but the pinned dependencies (greenlet 3.0.3,
# pandas 2.2.2) have no cp313 wheels. Use uv to provision Python 3.11 unless
# the system interpreter is already 3.11/3.12.
# ---------------------------------------------------------------------------
system_python_is_supported() {
    command -v python3 >/dev/null 2>&1 || return 1
    python3 - <<'PY'
import sys
raise SystemExit(0 if sys.version_info[:2] <= (3, 12) else 1)
PY
}

log "Preparing Python ${PYTHON_VERSION} virtualenv"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

UV_BIN="$(command -v uv 2>/dev/null || true)"
if [ ! -x "$APP_DIR/.venv/bin/python" ]; then
    if system_python_is_supported && [ "$PYTHON_VERSION" = "3.11" ] && python3 -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)'; then
        sudo -u "$APP_USER" -H python3 -m venv "$APP_DIR/.venv"
    else
        if [ -z "$UV_BIN" ]; then
            log "Installing uv (Python version manager)"
            curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh
            UV_BIN="$(command -v uv 2>/dev/null || echo /usr/local/bin/uv)"
        fi
        [ -x "$UV_BIN" ] || die "uv installation failed"
        sudo -u "$APP_USER" -H "$UV_BIN" python install "$PYTHON_VERSION"
        sudo -u "$APP_USER" -H "$UV_BIN" venv --python "$PYTHON_VERSION" "$APP_DIR/.venv"
    fi
else
    log "Reusing existing virtualenv at $APP_DIR/.venv"
fi

if [ -n "$UV_BIN" ] && [ -x "$APP_DIR/.venv/bin/python" ] && ! "$APP_DIR/.venv/bin/python" -m pip --version >/dev/null 2>&1; then
    log "Installing Python dependencies with uv"
    sudo -u "$APP_USER" -H "$UV_BIN" pip install --python "$APP_DIR/.venv/bin/python" -r "$APP_DIR/requirements.txt"
else
    log "Installing Python dependencies with pip"
    sudo -u "$APP_USER" -H "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
    sudo -u "$APP_USER" -H "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

install -d -o "$APP_USER" -g "$APP_USER" "$APP_DIR/logs"

# ---------------------------------------------------------------------------
# 4. Environment file
# ---------------------------------------------------------------------------
ENV_CREATED=0
if [ ! -f "$APP_DIR/.env" ]; then
    log "Creating .env from deploy/env.production.example"
    cp "$APP_DIR/deploy/env.production.example" "$APP_DIR/.env"
    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    ENV_CREATED=1
else
    log "Keeping existing .env"
    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
fi

# ---------------------------------------------------------------------------
# 5. TLS certificates + nginx
# ---------------------------------------------------------------------------
log "Generating TLS certificates"
SERVER_IP="$SERVER_IP" SERVER_NAME="$SERVER_NAME" CERT_DIR="$CERT_DIR" \
    bash "$APP_DIR/scripts/generate-certs.sh"

log "Installing nginx site configuration"
SERVER_IP="$SERVER_IP" SERVER_NAME="$SERVER_NAME" CERT_DIR="$CERT_DIR" \
    bash "$APP_DIR/scripts/install-nginx-config.sh"

# ---------------------------------------------------------------------------
# 6. PM2 startup
# ---------------------------------------------------------------------------
log "Registering PM2 with systemd"
if ! pm2 startup systemd -u "$APP_USER" --hp "$APP_HOME"; then
    warn "pm2 startup failed; configure it manually with: pm2 startup systemd -u $APP_USER --hp $APP_HOME"
fi

if [ "$START_APP" = "1" ]; then
    log "Starting the application with PM2"
    sudo -u "$APP_USER" -H bash -lc "cd '$APP_DIR' && pm2 start ecosystem.config.js --env production && pm2 save"
else
    log "Application left stopped (START_APP=0)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
log "Setup complete"
printf '  App directory: %s\n' "$APP_DIR"
printf '  App user:      %s\n' "$APP_USER"
printf '  Server IP:     %s\n' "$SERVER_IP"
printf '  Certificates:  %s\n' "$CERT_DIR"
printf '  API:           https://%s/api\n' "$SERVER_IP"
printf '  Redirect:      http://%s:9009 -> https://%s/api\n' "$SERVER_IP" "$SERVER_IP"

if [ "$ENV_CREATED" = "1" ]; then
    printf '\nNEXT: edit %s/.env (database, JWT secret, admin password).\n' "$APP_DIR"
fi

if [ "$START_APP" != "1" ]; then
    printf 'NEXT: start the API with PM2:\n'
    printf '  sudo -u %s -H bash -lc "cd %s && pm2 start ecosystem.config.js --env production && pm2 save"\n' "$APP_USER" "$APP_DIR"
fi
