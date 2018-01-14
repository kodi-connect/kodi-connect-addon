#!/bin/bash -xe

host=$(echo "${KODI_HOST}" | cut -d: -f2 | tr -d /)
# host="keks"
port=$(echo "${KODI_HOST}" | cut -d: -f3)

for i in $(seq 1 10); do
  # if timeout 1 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}"; then
  #   exit 0
  # fi
  # ping "${host}"
  if nc -z "${host}" "${port}"; then
    exit 0
  fi
  sleep 1
done

exit 1
