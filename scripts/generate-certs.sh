#!/usr/bin/env bash
#
# Generate a local CA and a TLS server certificate for Match Combat.
#
# Public CAs (Let's Encrypt included) do not issue certificates for private
# IP addresses such as 192.168.1.46. This script creates a local CA and a
# server certificate with subjectAltName entries for the LAN IP, so clients
# can trust ca.crt instead of ignoring browser warnings.
#
# Usage:
#   sudo ./scripts/generate-certs.sh
#   sudo FORCE=1 ./scripts/generate-certs.sh          # regenerate everything
#   CERT_DIR=./deploy/certs ./scripts/generate-certs.sh
#
# Environment variables:
#   SERVER_IP     LAN IP to include in the SAN (default 192.168.1.46)
#   SERVER_NAME   DNS name to include in the SAN (default $SERVER_IP)
#   CERT_DIR      Output directory (default /etc/nginx/ssl/match-combat)
#   DAYS          Server certificate validity in days (default 825)
#   CA_DAYS       CA validity in days (default 3650)
#   FORCE         1 = overwrite existing certificates
#   COUNTRY       Subject country (default SV)
#   ORG           Subject organization (default Match Combat)

set -euo pipefail

SERVER_IP="${SERVER_IP:-192.168.1.46}"
SERVER_NAME="${SERVER_NAME:-$SERVER_IP}"
# nginx accepts a space-separated server_name list; the certificate uses the
# first name as CN/DNS SAN, while the IP SANs cover both LAN and loopback.
PRIMARY_SERVER_NAME="${SERVER_NAME%% *}"
CERT_DIR="${CERT_DIR:-/etc/nginx/ssl/match-combat}"
DAYS="${DAYS:-825}"
CA_DAYS="${CA_DAYS:-3650}"
FORCE="${FORCE:-0}"
COUNTRY="${COUNTRY:-SV}"
ORG="${ORG:-Match Combat}"

CA_SUBJECT="/C=${COUNTRY}/O=${ORG}/CN=Match Combat Local CA"
SERVER_SUBJECT="/C=${COUNTRY}/O=${ORG}/CN=${PRIMARY_SERVER_NAME}"

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

command -v openssl >/dev/null 2>&1 || die "openssl is required (apt-get install openssl)"

if ! printf '%s' "$SERVER_IP" | grep -Eq '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'; then
    die "SERVER_IP must be an IPv4 address, got: $SERVER_IP"
fi

if [ -d "$CERT_DIR" ] && [ -f "$CERT_DIR/server.crt" ] && [ "$FORCE" != "1" ]; then
    log "Certificates already exist in $CERT_DIR"
    openssl x509 -in "$CERT_DIR/server.crt" -noout -subject -dates -ext subjectAltName 2>/dev/null \
        || openssl x509 -in "$CERT_DIR/server.crt" -noout -subject -dates

    if ! openssl x509 -in "$CERT_DIR/server.crt" -noout -text 2>/dev/null | grep -q "IP Address:${SERVER_IP}"; then
        printf '\nWARNING: the existing certificate does not cover IP %s.\n' "$SERVER_IP" >&2
        printf 'Regenerate with FORCE=1 and reload nginx.\n' >&2
    fi

    printf '\nUse FORCE=1 to regenerate (clients must trust the new CA again).\n'
    printf 'If nginx is already running, reload it: sudo systemctl reload nginx\n'
    exit 0
fi

umask 077
mkdir -p "$CERT_DIR"
chmod 700 "$CERT_DIR"

log "Generating local CA in $CERT_DIR"
if [ ! -f "$CERT_DIR/ca.key" ] || [ "$FORCE" = "1" ]; then
    openssl genrsa -out "$CERT_DIR/ca.key" 4096
    openssl req -x509 -new -nodes \
        -key "$CERT_DIR/ca.key" \
        -sha256 \
        -days "$CA_DAYS" \
        -out "$CERT_DIR/ca.crt" \
        -subj "$CA_SUBJECT" \
        -addext "basicConstraints=critical,CA:TRUE" \
        -addext "keyUsage=critical,keyCertSign,cRLSign"
else
    log "Reusing existing CA ($CERT_DIR/ca.crt)"
fi

log "Generating server certificate for ${PRIMARY_SERVER_NAME} (${SERVER_IP})"

SAN_FILE="$(mktemp)"
trap 'rm -f "$SAN_FILE"' EXIT

cat > "$SAN_FILE" <<EOF
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = ${SERVER_IP}
IP.2 = 127.0.0.1
DNS.1 = ${PRIMARY_SERVER_NAME}
DNS.2 = localhost
EOF

openssl genrsa -out "$CERT_DIR/server.key" 2048
openssl req -new \
    -key "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.csr" \
    -subj "$SERVER_SUBJECT"

openssl x509 -req \
    -in "$CERT_DIR/server.csr" \
    -CA "$CERT_DIR/ca.crt" \
    -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/server.crt" \
    -days "$DAYS" \
    -sha256 \
    -extfile "$SAN_FILE"

rm -f "$CERT_DIR/server.csr"

chmod 600 "$CERT_DIR/ca.key" "$CERT_DIR/server.key"
chmod 644 "$CERT_DIR/ca.crt" "$CERT_DIR/server.crt"

log "Verifying certificate chain"
openssl verify -CAfile "$CERT_DIR/ca.crt" "$CERT_DIR/server.crt"

printf '\nCertificates ready:\n'
printf '  CA:     %s\n' "$CERT_DIR/ca.crt"
printf '  Cert:   %s\n' "$CERT_DIR/server.crt"
printf '  Key:    %s\n' "$CERT_DIR/server.key"
printf '\nIf nginx is already running, reload it so it picks up the new certificate:\n'
printf '  sudo systemctl reload nginx\n'
printf '\nImport ca.crt into every client that must trust this server:\n'
printf '  Debian/Ubuntu: sudo cp ca.crt /usr/local/share/ca-certificates/match-combat.crt && sudo update-ca-certificates\n'
printf '  Windows:       import ca.crt into "Trusted Root Certification Authorities"\n'
printf '  macOS:         Keychain Access -> System -> import ca.crt -> Always Trust\n'
