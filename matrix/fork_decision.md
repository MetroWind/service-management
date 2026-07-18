# Matrix homeserver fork decision record

**Status:** Continuwuity selected as the intended long-term homeserver.

**Recorded:** 2026-07-17

**Scope:** This is a decision record for `darksair.org`, not a general
ranking of Matrix homeservers. It covers the Conduit family relevant to this
deployment: Conduit, Conduwuit, Tuwunel, Continuwuity, and Grapevine. It does
not attempt to enumerate every Matrix homeserver or every historical fork.

## Executive summary

The server currently runs **Continuwuity 26.6.2** successfully. It runs on
`obrona.xeno`, while Apache on `brighid.xeno` terminates TLS and proxies
requests to port 6167. Its database is a cold copy of the former working
Tuwunel 1.8.2 data directory.

Tuwunel is not the chosen long-term implementation. **Continuwuity** is now the
active server. The decision is primarily about governance, maintainership, and
fit for a self-hosted community server; it is not a claim that Tuwunel is
technically broken or unsafe.

The immediate operational rule is:

> Do not run Continuwuity and Tuwunel concurrently, and do not point either
> running process at the other's live data directory.

The Tuwunel project itself warns that switching between forks sharing its linear
database-version lineage can permanently corrupt data unless the migration is
explicitly supported.[^tuwunel-migration] The untouched Conduit backup and the
preserved stopped Tuwunel data directory are the rollback sources.

## Current deployment state

| Item | State |
| --- | --- |
| Matrix server name | `darksair.org` |
| Public Matrix endpoint | `matrix.xeno.darksair.org` |
| Current homeserver | Continuwuity 26.6.2 |
| Current database | RocksDB at `/var/lib/continuwuity` |
| Current media tree | `/var/lib/continuwuity/media` |
| Backend listener | `0.0.0.0:6167` on `obrona.xeno` |
| TLS/reverse proxy | Apache on `brighid.xeno` |
| Registration | Disabled |
| Federation | Enabled |
| Source archive | `matrix/matrix-conduit.tar.zstd` (untracked local file) |
| Rollback deployment | Tuwunel 1.8.2, stopped/disabled; data retained |
| Earlier deployment | Conduit 0.11.0-alpha, stopped/disabled |

The Ansible files in this directory now describe the Continuwuity cutover. They
deliberately leave the working Tuwunel installation and data in place as a
rollback source until post-cutover checks have succeeded.

## Lineage and terminology

```text
Conduit (Rust Matrix homeserver)
├── Conduwuit (fork; later archived)
│   ├── Continuwuity (community continuation of Conduwuit)
│   └── Tuwunel (declares itself the official successor to Conduwuit)
└── Grapevine (earlier fork from Conduit 0.7.0)
```

This is a useful historical map, not a database-compatibility map. Forks can
retain common ancestry while making incompatible database/schema decisions.

## Projects considered

### Conduit: the original deployment and migration source

Conduit is the original lightweight Rust homeserver from which the projects in
this record derive. This server ran `conduit 0.11.0-alpha (ea02329)`.

Conduit is not a current candidate for this deployment. The practical reason is
maintenance: the installation was already on an old alpha release, and the
project no longer provided the update path wanted for this server. Conduit is
still important because its complete backup is the authoritative source for a
future migration.

The migration that produced the current Tuwunel installation was not a simple
upstream-supported binary replacement:

1. Back up `/var/lib/matrix-conduit` completely, including SQLite side files
   and media.
2. Use the pinned `danjujan/conduit_toolbox` fork to convert the SQLite data to
   RocksDB.
3. Copy the *contents* of the converted RocksDB directory into
   `/var/lib/tuwunel`.
4. Copy the *contents* of Conduit's `media/` directory into
   `/var/lib/tuwunel/media`.
5. Start an appropriate Tuwunel version and verify client access, media, and
   federation.

That succeeded here, but it must not be read as a generic cross-fork migration
guarantee. In particular, Tuwunel's current migration table still lists Conduit
as unsupported and says that any supported source must be explicitly listed.[^tuwunel-migration]

### Conduwuit: the former active Conduit fork

Conduwuit was the major featureful Conduit fork that became the common ancestor
of the two realistic successors considered here. It existed to continue and
extend the Rust homeserver after divergence from Conduit. The original project
was later archived; Continuwuity's own project description gives that archival
as the reason a continuation was needed.[^continuwuity-repository]

It is not a deployment candidate because it is archived. Its importance is
historical and operational: both current candidates inherited code, release
practices, and parts of the database lineage from it.

### Continuwuity: community continuation of Conduwuit

Continuwuity was created after Conduwuit was archived. Its stated purpose is to
continue maintenance, fix outstanding bugs, improve compatibility, and build a
sustainable community-driven project.[^continuwuity-repository]

Its published goals fit this server well:

- a stable, lightweight Rust homeserver for modest self-hosted hardware;
- Matrix specification compatibility and operational features;
- documentation and deployment options for administrators; and
- a contributor/review process rather than dependence on one upstream author.

#### Current project health and engineering process

At the time of this record, Continuwuity is active: its Forgejo repository has
regular releases, active pull requests, and a sizeable issue tracker. The
project describes a review-and-test flow in which changes are reviewed, trialed
on tester servers, and merged after reviewers/testers agree.[^continuwuity-repository]

The public contribution guide requires formatting, linting, tests, documentation
where applicable, and PR review.[^continuwuity-contributing] The project allows
LLM-assisted contributions, but its PR template expressly rejects large,
low-quality machine-generated changes that have not received careful human
work. A recent merged PR shows that template and human maintainer approvals in
practice.[^continuwuity-pr-2014]

This does not prove that every change is correct. It is meaningful evidence
against the narrower concern that the project blindly accepts AI-generated code.

The public security policy names Jade, Nex, and Ginger as contacts and describes
private reporting, triage, coordinated disclosure, and release of fixes.[^continuwuity-security]

#### Maintainers and community behaviour

The core public team is small. Jade Ellis leads the project and represents
Continuwuity on the Matrix Governing Board.[^matrix-board] Nex and Ginger are
the other named security contacts and are also major current contributors. A
review of approximately 1,500 recent public commits on 2026-07-17 found Ginger
and Nex to be the two most prolific human authors in that sample; direct commit
counts are not a measure of leadership, but they are useful evidence of active
maintenance.

No well-sourced public record was found of threats, harassment, or comparable
misconduct by Jade, Nex, or Ginger. This is necessarily a limited conclusion:
private Matrix-room moderation is not fully observable, and absence of a public
record is not proof that no disagreement has occurred.

One relevant governance preference is visible in public. Nex runs some Matrix
communities with strict moderation, including external policy lists and a
low-tolerance approach to perceived malicious conduct.[^niobot-coc] During a
Continuwuity incident, a server hosted under FreeDNS was automatically blocked
because its server name matched an anti-spam list.[^continuwuity-postmortem]
That is not evidence of misconduct. It is a transparent indication that this
team prefers proactive, sometimes broad, anti-abuse controls. For this server,
that is understandable and acceptable; server-side moderation policy remains
under the local administrator's control.

#### Migration implications

Continuwuity does not advertise direct Tuwunel-database compatibility, and
Tuwunel warns against unlisted cross-fork migrations.[^tuwunel-migration] The
first attempted path was therefore based on the retained Conduit archive: the
SQLite data was converted with `danjujan/conduit_toolbox` revision
`7c9eaa176d1150e0a0e164bed3f615d002f03009`, then opened by Continuwuity 26.6.2.
The server completed startup and its schema migrations, but clients lost usable
room membership/state. A clean startup was not a sufficient migration test.

That direct Conduit-to-Continuwuity route is rejected for this deployment. The
working route was instead a complete, stopped copy of the known-good Tuwunel
1.8.2 directory into a separate Continuwuity data directory. Continuwuity 26.6.2
opened that copy with the existing chats, room state, media, and server identity
present. This is an observed compatibility result for these exact versions and
data, not a generic upstream guarantee.

Therefore the cutover must be planned as a migration, not an in-place upgrade:

1. Preserve the complete Conduit archive and stopped Tuwunel directory until
   the new deployment has been verified in normal use.
2. Stop both homeservers before making the cold data copy.
3. Copy the *contents* of `/var/lib/tuwunel` into a distinct
   `/var/lib/continuwuity` directory, including `media/`.
4. Start only Continuwuity and verify history, encrypted messaging, media, and
   federation before considering the migration complete.

The user has accepted that a migration is feasible and is not a reason to stay
on Tuwunel. That does not remove the requirement to verify the exact path before
touching production data.

### Tuwunel: the former working deployment

Tuwunel declares itself the official successor to Conduwuit. It is an active
Rust homeserver project with binaries/packages and an enterprise-oriented
positioning. Its repository says it is sponsored primarily by the Swiss
government and used by companies/government deployments.[^tuwunel-repository]

#### Why it was selected temporarily

Tuwunel was the practical immediate target because it had a current release
that could open the converted Conduit-derived data after the proper migration
handling. Version 1.8.2 worked on this server: clients connected, existing data
was visible, and the existing Apache proxy path remained usable.

Tuwunel also has operational strengths:

- active upstream development and released static binaries;
- good performance characteristics for a modest server;
- RocksDB support compatible with the conversion workflow used here;
- a documented security/release presence; and
- useful administrative functions, including manual media deletion.

For example, media retention can be approximated with an administrator command
such as `!admin media delete-range 365d --older-than`, with an additional
explicit flag required to remove local uploads. It is not a built-in automatic
one-year retention setting, so any scheduled deletion policy must be designed
and accepted locally.

#### Why Tuwunel is not the long-term choice

The decision against Tuwunel is a risk and fit judgment, not a technical
condemnation.

1. **Governance clarity and project fit.** Tuwunel's own public positioning is
   explicitly shaped by corporate and government sponsor needs. That can fund
   serious engineering, but this deployment is a small independently-operated
   server whose priority is community stewardship, maintainability, and a
   transparent contributor process. Continuwuity is the closer cultural fit.

2. **Public interpersonal conflict is an operational risk.** A Continuwuity
   issue alleges that Jason Volk made threats against several people. The issue
   does not publish the alleged messages or independently verifiable details,
   so it must not be treated as established fact.[^continuwuity-849] A separate
   critical HedgeDoc was written by the founder of the competing Grapevine fork
   and explicitly discloses that conflict of interest.[^fork-dispute-doc] It is
   useful for locating claims and primary artifacts, but is not neutral
   reporting. Even with those limitations, the recurring public dispute makes
   Tuwunel's governance harder to assess and less attractive for a long-lived
   personal community service.

3. **Current project policy does not eliminate lock-in risk.** Tuwunel warns
   against unlisted cross-fork migrations. The server already required a
   bespoke SQLite-to-RocksDB conversion to get here. Staying only because the
   current instance works would compound the cost of a later move.

4. **Continuwuity has enough positive, directly checkable evidence.** Its
   active review process, stated quality controls, security contacts, and
   community continuation model address the concerns that matter most here.
   This is a relative choice, not an assertion of perfection.

This decision should be revisited if any of the following materially change:

- Continuwuity stops releasing/security-maintaining the project;
- its contributor/review process becomes ineffective or opaque;
- a direct, safe, well-documented Tuwunel-to-Continuwuity migration route does
  not exist and restoring the Conduit source proves impractical; or
- independently verifiable information materially changes the governance
  assessment of either project.

### Grapevine: conservative but not ready

Grapevine forked from Conduit 0.7.0. Its stated aim is a robust, reliable
homeserver with an emphasis on maintainability, automated testing, and
instrumentation.[^grapevine-intro] It intentionally accepts configuration and
database incompatibility with Conduit where its maintainers believe divergence
is needed for secure, ergonomic operation.

It is not a candidate now. Its own site says there are no releases and that it
is not ready for general use. The Computer Surgery community site further says
development has largely halted because of maintainer burnout.[^computer-surgery]

Grapevine matters to the governance research because the author of a critical
document about the Conduit-family dispute also started Grapevine. That conflict
is openly disclosed in the document itself; it is the reason to treat its
interpretation cautiously while still checking any linked primary evidence.

## Decision

Choose **Continuwuity** as the intended long-term homeserver for `darksair.org`.

Keep the stopped Tuwunel installation and its data in place until Continuwuity
has completed post-cutover client, media, and federation checks over normal use.
The successful migration used a separate cold copy of the Tuwunel data, not a
shared live data directory or the failed direct Conduit conversion route.

## References

[^tuwunel-repository]: [Tuwunel repository and project statement](https://github.com/matrix-construct/tuwunel)
[^tuwunel-migration]: [Tuwunel migration and cross-fork database warning](https://github.com/matrix-construct/tuwunel#-migrating-to-tuwunel)
[^continuwuity-repository]: [Continuwuity repository README](https://forgejo.ellis.link/continuwuation/continuwuity)
[^continuwuity-contributing]: [Continuwuity contribution guide](https://continuwuity.org/development/contributing)
[^continuwuity-pr-2014]: [Continuwuity PR #2014, including its contribution checklist/template](https://forgejo.ellis.link/continuwuation/continuwuity/pulls/2014)
[^continuwuity-security]: [Continuwuity security policy](https://continuwuity.org/security)
[^matrix-board]: [Matrix Foundation governing-board election information](https://matrix.org/foundation/governing-board-elections/2026/)
[^niobot-coc]: [Nio-Bot room code of conduct and moderation policy](https://docs.nio-bot.dev/master/meta/code-of-conduct/)
[^continuwuity-postmortem]: [Continuwuity security-incident postmortem](https://nexy.blog/2025/12/22/continuwuity-postmortem/)
[^continuwuity-849]: [Continuwuity issue #849](https://forgejo.ellis.link/continuwuation/continuwuity/issues/849)
[^fork-dispute-doc]: [“Problems with Matrix homeserver implementations”](https://hedgedoc.computer.surgery/s/qMd17DXxP)
[^grapevine-intro]: [Grapevine project introduction](https://grapevine.computer.surgery/)
[^computer-surgery]: [Computer Surgery project status](https://computer.surgery/)
