#!/bin/bash
# nginx site + Let's Encrypt certificate for Revert on the shared Odoo 20 server. Run as root:
#   vhost.sh <host> [email for Let's Encrypt]
# <host> is also the database name (dbfilter ^%h$). Its DNS A record must already point to this
# server. Same layout as the Albatross site: :80 answers the ACME challenge and redirects, :443
# includes the shared snippets (erp-tls, erp-odoo). Stage 1 serves :80 only so certbot can prove the
# domain; stage 2 installs the HTTPS server once the certificate exists. Re-runnable.
set -euo pipefail
HOST=${1:?host}
EMAIL=${2:-}
SITE=/etc/nginx/sites-available/erp-revert.conf

http_block() {
cat <<EOF
# Revert on the shared Odoo 20 ERP: $HOST serves database "$HOST" (dbfilter ^%h\$).
server {
    listen 80;
    listen [::]:80;
    server_name $HOST;
    include snippets/acme-challenge.conf;
    location / { return 301 https://$HOST\$request_uri; }
}
EOF
}

https_block() {
cat <<EOF
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name $HOST;
    ssl_certificate /etc/letsencrypt/live/$HOST/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$HOST/privkey.pem;
    include snippets/erp-tls.conf;
    add_header Strict-Transport-Security "max-age=31536000" always;
    access_log /var/log/nginx/$HOST.access.log;
    error_log /var/log/nginx/$HOST.error.log;
    include snippets/erp-odoo.conf;
}
EOF
}

resolved=$(getent ahostsv4 "$HOST" | awk '{print $1}' | sort -u | tr '\n' ' ')
mine=$(curl -4 -s --max-time 10 https://api.ipify.org || true)
echo "$HOST resolves to: ${resolved:-nothing}; this server: ${mine:-unknown}"
case " $resolved " in *" $mine "*) ;; *) echo "DNS for $HOST does not point here yet: stop" >&2; exit 1 ;; esac

if [ ! -s "/etc/letsencrypt/live/$HOST/fullchain.pem" ]; then
    http_block > "$SITE"
    ln -sfn "$SITE" /etc/nginx/sites-enabled/erp-revert.conf
    nginx -t && systemctl reload nginx
    if [ -n "$EMAIL" ]; then reg=(-m "$EMAIL"); else reg=(--register-unsafely-without-email); fi
    certbot certonly --webroot -w /var/www/letsencrypt -d "$HOST" --agree-tos -n "${reg[@]}"
fi
{ http_block; https_block; } > "$SITE"
ln -sfn "$SITE" /etc/nginx/sites-enabled/erp-revert.conf
nginx -t && systemctl reload nginx
certbot certificates -d "$HOST" 2>/dev/null | grep -E "Certificate Name|Expiry Date" || true
