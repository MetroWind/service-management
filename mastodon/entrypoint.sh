#!/bin/sh

redis-server /etc/redis/redis.conf &
bundle exec sidekiq -c 25 &
PORT=4000 node ./streaming &
exec bundle exec puma -C config/puma.rb
