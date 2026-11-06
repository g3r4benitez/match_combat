#!/usr/bin/env bash
#
# Render and install the Match Combat nginx site on Debian 13.
#
# Usage:
#   sudo SERVER_IP=192.168.1.46 ./scripts/install-nginx-config.sh
#
# Environment variables:
#   SERVER_IP     LAN IP where port 9009 redirects to HTTPS (default 192.168.1.46)
#   SERVER_NAME   nginx server_name values (default $SERVER_IP)
#   CERT_DIR      TLS certificate directory (default /etc/nginx/ssl/match-combat)
#   SKIP_RELOAD   1 = validate only, do not reload nginx

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

case "$SERVER_NAME" in
    *"|"*) die "SERVER_NAME must not contain the '|' character" ;;
esac

[ -f "$CERT_DIR/server.crt" ] || die "Missing $CERT_DIR/server.crt (run scripts/generate-certs.sh first)"
[ -f "$CERT_DIR/server.key" ] || die "Missing $CERT_DIR/server.key (run scripts/generate-certs.sh first)"

install -d /etc/nginx/snippets /etc/nginx/sites-available /etc/nginx/sites-enabled

log "Installing proxy header snippet"
install -m 644 "$SNIPPET" "$SNIPPET_TARGET"

log "Rendering site configuration"
sed \
    -e "s|__SERVER_IP__|${SERVER_IP}|g" \
    -e "s|__SERVER_NAME__|${SERVER_NAME}|g" \
    -e "s|__CERT_DIR__|${CERT_DIR}|g" \
    "$TEMPLATE" > "$SITE_AVAILABLE"
chmod 644 "$SITE_AVAILABLE"

ln -sfn "$SITE_AVAILABLE" "$SITE_ENABLED"

log "Validating nginx configuration"
nginx -t

if [ "$SKIP_RELOAD" = "1" ]; then
    log "SKIP_RELOAD=1: configuration installed but nginx was not reloaded"
    exit 0
fi

log "Reloading nginx"
systemctl reload nginx

log "nginx configuration installed"
printf '  Site:    %s\n' "$SITE_AVAILABLE"
printf '  Enabled: %s\n' "$SITE_ENABLED"
printf '  Cert:    %s\n' "$CERT_DIR"
