# Git Server

This is a [Gitolite](https://gitolite.com) +
[cgit](https://git.zx2c4.com/cgit/about/) + Apache setup. This setup
is extremely tricky. A lot of care has to be taken to make everything
works. However I would not call this brittle.

## Admin

In reality, Gitolite does not do much in the admin aspect in this
setup. I only use it to “conveniently” create new repos. The Gitolite
user is `gitolite`. I followed the [official
doc](https://gitolite.com/gitolite/install.html) as well [Arch
wiki](https://wiki.archlinux.org/title/Gitolite/) to install and to do
the initial setup.

## Frontend and pull

The web frontend is served with cgit. This is relatively
straightforward, with the only caveat being the URLs in the Apache
config need to match those in the cgit config. And depending on the
URLs, the order of the statics rule and the `ScriptAlias` in the
Apache config might need some adjustments.

The read actions (pull, clone, etc.) are also handled by cgit.

## Push

This is the tricky part. Initially I wanted to use git-http-backend,
which I almost made work. But I found that it is
[incompatiple](https://gitolite.com/gitolite/emergencies.html#common-errors)
with Gitolite’s hook system. Gitolite would complain with something
like

> Empty compile time value given to use lib at hooks/update line 6\
> Can't locate Gitolite/Hooks/Update.pm in @INC

So I switched to using gitolite-shell. There are three parts to the
trick: cooperation with cgit, authentication, and permission.

### Coorperation with cgit

The usual setup of cgit will let it handle all HTTP requests. Cgit
cannot handle push, and therefore git push would fail. The trick here
is to arrange the Apache rules in such a way that only the
push-related requests are handled by Gitolite. The correct setup comes
from the [git-http-backend
doc](https://www.kernel.org/pub/software/scm/git/docs/git-http-backend.html):
```
ScriptAliasMatch \
        "(?x)^/git/(.*/(HEAD | \
                        info/refs | \
                        objects/(info/[^/]+ | \
                                 [0-9a-f]{2}/[0-9a-f]{38} | \
                                 pack/pack-[0-9a-f]{40}\.(pack|idx)) | \
                        git-(upload|receive)-pack))$" \
        /usr/libexec/git-core/git-http-backend/$1
```
Of course we need to replace the CGI executable with `gitolite-shell`.

### Authentication

The correct config here also comes from the git-http-backend doc. And
most importantly, we only need to protect `git-receive-pack`.
```
RewriteCond %{QUERY_STRING} service=git-receive-pack [OR]
RewriteCond %{REQUEST_URI} /git-receive-pack$
RewriteRule ^/ - [E=AUTHREQUIRED:yes]
<LocationMatch "^/">
  Order Deny,Allow
  Deny from env=AUTHREQUIRED
  AuthType Basic
  AuthName "Git Access"
  AuthBasicProvider file
  AuthUserFile /srv/http-git/htpasswd
  Require valid-user
  Satisfy Any
</LocationMatch>
```
However this has a problem. When git makes an HTTP request, it looks
for a 401 response to know that the server requests authentication.
The `LocationMatch` would return 404 when authentication fails. I have
not find a good solution to this. For now I set `http.proactiveAuth` to
`basic` in all the repos.

### Permission

In this setup the repo dir is owned by gitolite. However the CGI
scripts are executed by the http user. Therefore gitolite-shell would
not be able to modify anything in the repo dir. A solution is to use
the suexec Apache module, which requires the CGI scripts to be in
DocumentRoot. For this I created wrapper scripts in DocumentRoot. Note
that suexec does not apply to individual CGI script. It only applies
to global or virtual server. So I have to wrap both gitolite-shell and
cgit.

## Usage

* The `gitolite-admin` repo is only accessible via LAN ssh
* All repo should have `http.proactiveAuth = basic` locally.
* Removing and renaming of repos must be done manually after pushing
the change in `gitolite-admin`.
