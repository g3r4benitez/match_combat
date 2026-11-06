#!/usr/bin/env bash
#
# Render and install the Match Combat nginx site on Debian 13.
#
# The installed configuration is validated with `nginx -t` before the running
# server is reloaded. If validation or reload fails, the previous site file is
# restored, so a bad render cannot leave nginx unable to start on reboot.
#
# Usage:
#   sudo SERVER_IP=192.168.1.46 ./scripts/install-nginx-config.sh
#
# Environment variables:
#   SERVER_IP     LAN IP where port 9009 redirects to HTTPS (default 192.168.1.46)
#   SERVER_NAME   nginx server_name values (default $SERVER_IP)
#   CERT_DIR      TLS certificate directory (default /etc/nginx/ssl/match-combat)
#   SKIP_RELOAD   1 = install and validate, but do not reload nginx

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$APP_DIR/deploy/nginx/match-combat.conf.template"
SNIPPET="$APP_DIR/deploy/nginx/proxy-headers.conf"
SERVER_IP="${SERVER_IP:-192.168.1.46}"
SERVER_NAME="${SERVER_NAME:-$SERVER_IP}"
CERT_DIR="${CERT_DIR:-/etc/nginx/ssl/match-combat}"
SKIP_RELOAD="${SKIP_RELOAD:-0}"

SITE_AVAILABLE="/etc/nginx/sites-available/match-combat.conf"
SITE_ENABLED="/etc/nginx/sites-enabled/match-combat.conf"
SNIPPET_TARGET="/etc/nginx/snippets/match-combat-proxy-headers.conf"

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Run as root: sudo $0"
command -v nginx >/dev/null 2>&1 || die "nginx is not installed"
[ -f "$TEMPLATE" ] || die "Template not found: $TEMPLATE"
[ -f "$SNIPPET" ] || die "Snippet not found: $SNIPPET"

if ! printf '%s' "$SERVER_IP" | grep -Eq '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'; then
    die "SERVER_IP must be an IPv4 address, got: $SERVER_IP"
fi

# All three values are substituted through pipe-delimited sed expressions.
for value in "$SERVER_IP" "$SERVER_NAME" "$CERT_DIR"; do
    case "$value" in
        *"|"*) die "SERVER_IP, SERVER_NAME and CERT_DIR must not contain the '|' character" ;;
        *"&"*) die "SERVER_IP, SERVER_NAME and CERT_DIR must not contain the '&' character" ;;
    esac
done

[ -f "$CERT_DIR/server.crt" ] || die "Missing $CERT_DIR/server.crt (run scripts/generate-certs.sh first)"
[ -f "$CERT_DIR/server.key" ] || die "Missing $CERT_DIR/server.key (run scripts/generate-certs.sh first)"

install -d /etc/nginx/snippets /etc/nginx/sites-available /etc/nginx/sites-enabled

log "Installing proxy header snippet"
install -m 644 "$SNIPPET" "$SNIPPET_TARGET"

# Keep the previous site file so a failed validation or reload can roll back.
BACKUP="$(mktemp)"
HAD_PREVIOUS=0
if [ -f "$SITE_AVAILABLE" ]; then
    cp -a "$SITE_AVAILABLE" "$BACKUP"
    HAD_PREVIOUS=1
fi

restore_previous() {
    if [ "$HAD_PREVIOUS" = "1" ]; then
        cp -a "$BACKUP" "$SITE_AVAILABLE"
        log "Previous nginx site configuration restored"
    else
        rm -f "$SITE_AVAILABLE" "$SITE_ENABLED"
        log "No previous nginx site configuration existed; new file removed"
    fi
}

cleanup() {
    rm -f "$BACKUP"
}
trap cleanup EXIT

log "Rendering site configuration"
sed \
    -e "s|__SERVER_IP__|${SERVER_IP}|g" \
    -e "s|__SERVER_NAME__|${SERVER_NAME}|g" \
    -e "s|__CERT_DIR__|${CERT_DIR}|g" \
    "$TEMPLATE" > "$SITE_AVAILABLE"
chmod 644 "$SITE_AVAILABLE"

ln -sfn "$SITE_AVAILABLE" "$SITE_ENABLED"

log "Validating nginx configuration"
if ! nginx -t; then
    restore_previous
    die "nginx -t failed; the previous configuration was restored"
fi

if [ "$SKIP_RELOAD" = "1" ]; then
    log "SKIP_RELOAD=1: configuration installed and validated, but nginx was not reloaded"
    exit 0
fi

log "Reloading nginx"
if ! systemctl reload nginx; then
    restore_previous
    die "nginx reload failed; the previous configuration was restored"
fi

log "nginx configuration installed"
printf '  Site:    %s\n' "$SITE_AVAILABLE"
printf '  Enabled: %s\n' "$SITE_ENABLED"
printf '  Cert:    %s\n' "$CERT_DIR"
