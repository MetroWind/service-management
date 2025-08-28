#!/bin/sh

export GIT_PROJECT_ROOT=/var/lib/gitolite/repositories
export GITOLITE_HTTP_HOME=/var/lib/gitolite

exec /usr/lib/cgit/cgit.cgi
