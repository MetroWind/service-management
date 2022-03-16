#!/bin/sh

exec curl "https://admin:{{ dns_http_password }}@darksair.org/dns/update-dns01-txt?domain=${CERTBOT_DOMAIN}&value=${CERTBOT_VALIDATION}"
