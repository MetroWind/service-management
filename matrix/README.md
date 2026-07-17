# Matrix / Tuwunel

This directory deploys the Tuwunel homeserver for `darksair.org` on
`obrona.xeno`. It replaces the retired Conduit deployment.

## One-time data migration

1. Stop Conduit and make a complete backup of `/var/lib/matrix-conduit`.
2. Convert Conduit's SQLite database to RocksDB with the pinned
   `danjujan/conduit_toolbox` fork.
3. Copy the *contents* of the converted RocksDB directory into
   `/var/lib/tuwunel/`. Do not create `/var/lib/tuwunel/rocksdb/`.
4. Copy the *contents* of `/var/lib/matrix-conduit/media/` into
   `/var/lib/tuwunel/media/`.
5. Run this playbook. It changes ownership of `/var/lib/tuwunel`, installs
   Tuwunel, disables Conduit, and starts Tuwunel. It never removes the old
   Conduit data directory or its configuration.

```sh
ansible-playbook matrix/setup.yaml
```

The configuration keeps the existing backend listener on `0.0.0.0:6167`,
which is proxied by `brighid.xeno`.

## Post-deployment checks

```sh
systemctl status tuwunel.service
curl -fsS https://matrix.xeno.darksair.org/_matrix/client/versions
curl -fsS https://matrix.xeno.darksair.org:8448/_matrix/federation/v1/version
```

Do not delete `/var/lib/matrix-conduit` until client login, media access, and
incoming federation have all been verified.
