#!/bin/bash
set -e

COMMANDS="debug help logtail show stop adduser fg kill quit run wait console foreground logreopen reload shell status"
START="start restart zeoserver"
CMD="bin/instance"

# Fixing permissions for external /data volumes
mkdir -p /data/blobstorage /data/cache /data/filestorage /data/instance /data/log /data/zeoserver
mkdir -p /plone/instance/src
find /data  -not -user plone -exec chown plone:plone {} \+
find /plone -not -user plone -exec chown plone:plone {} \+

# Initializing from environment variables
su-exec plone python /docker-initialize.py

if [ -e "custom.cfg" ]; then
  if [ ! -e "bin/develop" ]; then
    buildout -c custom.cfg
    find /data  -not -user plone -exec chown plone:plone {} \+
    find /plone -not -user plone -exec chown plone:plone {} \+
    su-exec plone python /docker-initialize.py
  fi
fi

if [[ "$1" == "zeo"* ]]; then
  CMD="bin/$1"
fi

if [ -z "$HEALTH_CHECK_TIMEOUT" ]; then
  HEALTH_CHECK_TIMEOUT=1
fi

if [ -z "$HEALTH_CHECK_INTERVAL" ]; then
  HEALTH_CHECK_INTERVAL=1
fi

if [[ $START == *"$1"* ]]; then
  _stop() {
    su-exec plone $CMD stop
    kill -TERM $child 2>/dev/null
  }

  trap _stop SIGTERM SIGINT
  su-exec plone $CMD start
  su-exec plone $CMD logtail &
  child=$!

  pid=`$CMD status | sed 's/[^0-9]*//g'`
  if [ ! -z "$pid" ]; then
    echo "Application running on pid=$pid"
    sleep "$HEALTH_CHECK_TIMEOUT"
    while kill -0 "$pid" 2> /dev/null; do
      sleep "$HEALTH_CHECK_INTERVAL"
    done
  else
    echo "Application didn't start normally. Shutting down!"
    _stop
  fi
else
  if [[ $COMMANDS == *"$1"* ]]; then
    exec su-exec plone bin/instance "$@"
  fi
  exec "$@"
fi