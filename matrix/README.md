# Matrix / Continuwuity

This directory deploys the Continuwuity homeserver for `darksair.org` on
`obrona.xeno`. Apache on `brighid.xeno` terminates TLS and proxies Matrix
traffic to `obrona.xeno:6167`.

## Current deployment

Continuwuity 26.6.2 runs from `/var/lib/continuwuity`. It was populated with a
cold, complete copy of the formerly-working Tuwunel 1.8.2 data directory. This
preserved the existing room data, user data, media, and Matrix server signing
key that were already present in the Tuwunel database.

`/var/lib/tuwunel` is retained, unchanged, as a rollback source. Never run both
homeservers at once, and never configure either server to use the other's live
data directory.

## Migration record

The following route was successful for this deployment:

```text
Conduit SQLite backup → Tuwunel 1.8.2 (previous working deployment)
                       → cold copy of /var/lib/tuwunel
                       → Continuwuity 26.6.2
```

The final arrow is a cold data copy, not a live binary swap. It has been
observed to retain the existing chats and room membership on this server, but
it is not advertised as a generally-supported cross-fork migration. Keep the
original and copied directories until normal client and federation use has been
verified over time.

Do **not** instead use this route:

```text
Conduit SQLite backup → conduit_toolbox RocksDB output → Continuwuity
```

It opened without a startup error but lost usable local room membership/state
in testing. The archive remains useful as a historical backup, not as the input
to the Continuwuity cutover.

If the successful cutover ever needs to be reproduced, stop both services,
make a new backup, then copy the *contents* of the stopped Tuwunel directory
into a new Continuwuity directory:

```sh
sudo systemctl stop continuwuity.service tuwunel.service
sudo install -d -m 0700 /var/lib/continuwuity
sudo rsync -aHAX --numeric-ids /var/lib/tuwunel/ /var/lib/continuwuity/
```

The destination must contain `CURRENT`, the RocksDB files, and `media/`
directly; do not create `/var/lib/continuwuity/tuwunel/`.

## Deploy

Run the playbook only after the new data directory is staged:

```sh
ansible-playbook -i hosts.ini -k -K matrix/setup.yaml
```

It stops and disables Tuwunel, installs Continuwuity 26.6.2, removes the
downloaded release after installation, changes ownership of
`/var/lib/continuwuity`, and starts Continuwuity. It does not remove Tuwunel,
Conduit, their data directories, or their configuration.

## Checks and normal federation noise

```sh
systemctl status continuwuity.service
curl -fsS https://matrix.xeno.darksair.org/_matrix/client/versions
curl -fsS https://matrix.xeno.darksair.org:8448/_matrix/federation/v1/version
```

Verify an existing encrypted conversation can send and receive, and verify an
old attachment. Retain the rollback data until this has been stable in normal
use.

Messages such as `Failed to parse .well-known` tagged with `fed{dest=...}`
refer to malformed discovery documents served by remote Matrix domains. A
`publicRooms` DNS `SERVFAIL` names the remote room directory that could not be
queried. Neither message indicates local database or migration corruption.
