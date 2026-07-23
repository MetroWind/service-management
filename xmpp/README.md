# XMPP service

This directory deploys the XMPP service for `xmpp.xeno.darksair.org`.

The homeserver is ejabberd on `obrona.xeno`. It uses SQLite for its local
database and serves client XMPP, federation, and its HTTPS endpoints directly.
Caddy on the same host obtains the public TLS certificate. Apache on
`brighid.xeno` forwards the public HTTP-01 ACME challenge to Caddy.

The most important part of this setup is the certificate hand-off from Caddy to
ejabberd. Caddy is the ACME client; ejabberd must not attempt ACME itself.

## Components and traffic flow

```
Internet
    |
    | TCP 80, HTTP-01 challenge
    v
brighid.xeno: Apache
    |
    | proxy to 10.10.10.29:80
    v
obrona.xeno: Caddy
    |
    | obtains and stores the certificate
    v
/var/lib/caddy/certificates/...
    |
    | copy-cert-xmpp.service
    v
/var/lib/ejabberd/certs/
    |
    | ejabberdctl reload_config
    v
ejabberd
```

ejabberd listens on these ports:

| Port | Purpose |
| --- | --- |
| 5222/TCP | Client-to-server XMPP with STARTTLS |
| 5223/TCP | Direct TLS client-to-server XMPP |
| 5269/TCP | Server-to-server federation |
| 5443/TCP | HTTPS: HTTP Upload, WebSocket, BOSH, API, and Web Admin |

The router must forward the public ports that are intended to be reachable.
In particular, HTTP Upload uses the URL
`https://xmpp.xeno.darksair.org:5443/upload`; a NAT rule for 5443 must forward
to obrona. LAN clients also need NAT reflection for that port, or split DNS.

## TLS and ACME

### HTTP-01 routing

`httpd.conf` is installed on brighid. Its sole job is to forward:

```
http://xmpp.xeno.darksair.org/.well-known/acme-challenge/
```

to Caddy on obrona. Caddy's `caddyfile` defines the hostname and a harmless
response, which is enough for Caddy to manage the certificate and respond to
ACME challenges.

The public DNS record for `xmpp.xeno.darksair.org` must point to brighid's
public address. Port 80 must reach Apache on brighid.

### Why ejabberd ACME is disabled

ejabberd's built-in ACME client is disabled with `acme.auto: false`. This
deployment previously encountered a timeout while ejabberd requested a
certificate, despite working DNS and HTTP-01 routing. The relevant upstream
report is [ejabberd issue #4407](https://github.com/processone/ejabberd/issues/4407).

Caddy is already responsible for certificate issuance elsewhere in this setup,
has a reliable renewal loop, and can use the HTTP-01 proxy above. The hand-off
service keeps that division of responsibility while still giving ejabberd a
normal local certificate and key.

### Why the copy-and-reload service exists

ejabberd is configured with:

```yaml
acme:
  auto: false

certfiles:
  - /var/lib/ejabberd/certs/xmpp.xeno.darksair.org.crt
  - /var/lib/ejabberd/certs/xmpp.xeno.darksair.org.key
```

Caddy stores its current certificate and private key under its own state
directory. ejabberd intentionally does not use that location directly: Caddy
owns those files and may replace them at renewal. More importantly, replacing
files on disk does not by itself make ejabberd reread the certificate.

`copy-cert-xmpp.service` therefore runs as root and does three things in order:

1. Copies Caddy's `.crt` and `.key` files to `/var/lib/ejabberd/certs/`.
2. Changes their ownership to `jabber:jabber`.
3. Runs `ejabberdctl reload_config`, which makes ejabberd reopen the configured
   certificate files without a server restart.

`copy-cert-xmpp.timer` invokes that service once a day, with up to one hour of
random delay. `Persistent=true` runs a missed invocation after boot. Daily
copying is intentionally simple: Caddy can renew at any time in its renewal
window, and copying unchanged files is harmless.

The service currently assumes Caddy's default local storage and Let's Encrypt's
production directory:

```
/var/lib/caddy/certificates/acme-v02.api.letsencrypt.org-directory/
  xmpp.xeno.darksair.org/
```

If Caddy's storage root, issuer, or certificate name changes, update the two
source paths in `copy-cert.service` as well.

### Service account caveat

`ejabberdctl` switches to the `ejabberd` service account. If that account is
expired, commands such as `ejabberdctl reload_config` fail with an account
expiry error even when invoked by root. Ensure that the system account has no
expiry date:

```sh
chage -l ejabberd
chage -E -1 ejabberd
```

The second command is only needed if the first command reports an expiry date.

### Verification and manual recovery

After deployment, check that the timer exists and the one-shot service works:

```sh
systemctl list-timers copy-cert-xmpp.timer
systemctl start copy-cert-xmpp.service
systemctl status copy-cert-xmpp.service
journalctl -u copy-cert-xmpp.service --no-pager
```

To inspect the certificate offered by ejabberd from another machine:

```sh
openssl s_client -connect xmpp.xeno.darksair.org:5223 \
  -servername xmpp.xeno.darksair.org </dev/null
```

Check the subject, issuer, and expiry date in the output. For a STARTTLS check,
use an XMPP-aware client or a TLS testing tool that supports STARTTLS.

## HTTP Upload and attachments

`mod_http_upload` serves files through the HTTPS listener on port 5443. The
default upload service JID is `upload.xmpp.xeno.darksair.org`, while local user
accounts are on `xmpp.xeno.darksair.org`. ejabberd's default `local` access rule
would evaluate against the upload service host and deny those users.

The `xmpp_users` ACL and `http_upload` access rule explicitly permit accounts
from `xmpp.xeno.darksair.org`, without granting upload access to arbitrary
federated users. This is required for normal file uploads and for Monocles Chat
stickers, including encrypted stickers that are converted to uploads.

`mod_http_upload_quota.max_days: 365` removes files and directories older than
one year from ejabberd's HTTP Upload storage. It applies to local HTTP Upload
files only; it does not delete MAM messages or remote media.

### Sticker retention

Monocles Chat currently sends stickers through HTTP Upload as ordinary image
files. It does not mark the upload as a sticker in a way ejabberd can use for
retention policy. Consequently, the one-year upload cleanup applies to
stickers as well, including stickers sent in encrypted conversations.

After cleanup, the MAM message remains, but its upload URL no longer serves the
image. A client that already cached the sticker may still display it; a new
device or an uncached client will not be able to retrieve it. ejabberd's upload
quota module has no per-file, path, or MIME-type exception for this policy.

If stickers must remain available indefinitely, either keep HTTP Upload files
indefinitely by removing the age limit, or use a separate static hosting and
sticker-pack design. The latter is not provided by the current Monocles upload
flow.

## Messaging features

The service enables MAM by default, persistent MUC creation for local users,
PubSub/PEP, roster versioning, and standard HTTP/WebSocket endpoints. OMEMO is
client-side and is not required by this server configuration.

## Deployment

Deploy the complete service configuration with:

```sh
ansible-playbook -i hosts.ini -k -K xmpp/setup.yaml
```

The playbook updates Apache on brighid, Caddy and ejabberd configuration on
obrona, installs the certificate-copy unit and timer, then restarts ejabberd.

For temporary ejabberd diagnostics:

```sh
ejabberdctl set_loglevel debug
journalctl -fu ejabberd
```

Always restore normal logging afterward:

```sh
ejabberdctl set_loglevel info
```
