FROM archlinux:base-devel
# RUN sed -i '1s/^/# /' /etc/pacman.d/mirrorlist
RUN pacman --noconfirm -Syu
RUN pacman --noconfirm -S wget ruby ffmpeg imagemagick libidn libpqxx libxml2 libxslt libyaml nodejs redis ruby-bundler protobuf yarn zlib git

ENV version="4.0.2"
ENV LOCAL_DOMAIN="darksair.org"
ENV WEB_DOMAIN="mastodon.xeno.darksair.org"
ENV DB_NAME="mastodon_production"

ENV RAILS_ENV="production"
ENV PORT="3000"
ENV LD_PRELOAD="libjemalloc.so"
ENV DB_POOL="25"
ENV MALLOC_ARENA_MAX="2"
ENV STREAMING_CLUSTER_NUM="1"
ENV BIND="0.0.0.0"

WORKDIR /tmp/build

RUN wget https://github.com/mastodon/mastodon/archive/v${version}.tar.gz
RUN tar -xf v${version}.tar.gz
WORKDIR /tmp/build/mastodon-${version}
# Allow use of any bundler
RUN sed -i -e '/BUNDLED/,+1d' Gemfile.lock
RUN bundle config set silence_root_warning true
RUN bundle config set --local path 'vendor/bundle'
RUN bundle config unset deployment
RUN bundle config set without 'development test'
RUN bundle install -j$(getconf _NPROCESSORS_ONLN)
RUN yarn install --pure-lockfile

WORKDIR /tmp/build
RUN mv mastodon-${version} /var/lib/mastodon
WORKDIR /var/lib/mastodon

# Put the config file in /etc and link to it
RUN touch /etc/mastodon.conf
RUN ln -s /etc/mastodon.conf /var/lib/mastodon/.env.production
RUN ln -s /usr/bin/node /var/lib/mastodon/node

COPY entrypoint.sh .
COPY env.production .env.production

ENTRYPOINT ["sh", "entrypoint.sh"]
