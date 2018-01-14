#!/bin/bash -e

host=$(echo "${KODI_HOST}" | cut -d: -f2 | tr -d /)
port=$(echo "${KODI_HOST}" | cut -d: -f3)

for i in $(seq 1 60); do
  if timeout 1 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" 2> /dev/null; then
    exit 0
  fi
  sleep 1
done

exit 1
