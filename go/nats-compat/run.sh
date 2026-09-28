#!/usr/bin/env bash
#
# Does the unchanged capture connect and publish to a given NATS server image?
# See PLAN-nats-compat.md at the repo root.
#
# Usage: go/nats-compat/run.sh <nats-server-image> [platform]
#   go/nats-compat/run.sh nats:2.15.0
#   go/nats-compat/run.sh synadia/nats-server:nightly-20220224 linux/amd64
#
# Local Docker only: no MySQL, no /dev, no production hosts.
# The capture connects to nats.ts.imetrical.com (hardcoded), publishes "Start",
# fails to open MySQL, sleeps 5s and exits. --add-host points that hostname at
# the local server, inside the capture container only.

set -euo pipefail

IMAGE=${1:?usage: $0 <nats-server-image> [platform]}
PLATFORM=${2:-}

GO_DIR=$(cd "$(dirname "$0")/.." && pwd)
NET=ted1k-nats-compat
SERVER=ted1k-nc-server
SUB=ted1k-nc-sub
CAPTURE_IMAGE=ted1k-capture:nats-compat
SUBJECT=im.qcic.heartbeat

cleanup() {
  docker rm -f "$SERVER" "$SUB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

echo "## Build capture from go/Dockerfile (golang:1.20, unchanged)"
docker build -q -t "$CAPTURE_IMAGE" "$GO_DIR" >/dev/null

docker network create "$NET" >/dev/null

echo "## Server: $IMAGE ${PLATFORM:+($PLATFORM)}"
# keep the image's own config args, add -DV to log client CONNECT/PUB
read -r -a SERVER_ARGS <<<"$(docker image inspect "$IMAGE" --format '{{range .Config.Cmd}}{{.}} {{end}}')"
docker run -d --name "$SERVER" --network "$NET" ${PLATFORM:+--platform "$PLATFORM"} \
  "$IMAGE" "${SERVER_ARGS[@]}" -DV >/dev/null
sleep 2
SERVER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$SERVER")
echo "server IP: $SERVER_IP"

echo "## Subscriber (nats-box) on $SUBJECT"
docker run -d --name "$SUB" --network "$NET" natsio/nats-box:latest \
  nats sub -s "nats://$SERVER:4222" "$SUBJECT" >/dev/null
sleep 2

echo "## Capture (exit expected after ~5s: no MySQL)"
set +e
docker run --rm --network "$NET" \
  --add-host "nats.ts.imetrical.com:$SERVER_IP" \
  "$CAPTURE_IMAGE"
echo "capture exit status: $?"
set -e
sleep 1

echo "## Server version"
docker logs "$SERVER" 2>&1 | grep -m1 -i 'version' || true
echo "## Server log: capture client (CONNECT/PUB, warnings, errors)"
docker logs "$SERVER" 2>&1 | grep -E 'capture\.ted1k|PUB im\.qcic|\[WRN\]|\[ERR\]' || true
echo "## Subscriber output"
docker logs "$SUB" 2>&1

if docker logs "$SUB" 2>&1 | grep -q '"text":"Start"'; then
  echo "## RESULT $IMAGE: PASS (\"Start\" received)"
else
  echo "## RESULT $IMAGE: FAIL (\"Start\" not received)"
  exit 1
fi
