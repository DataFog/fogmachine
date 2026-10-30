#!/usr/bin/env bash
set -euo pipefail
profile="$1"
checkout="$2"
container="fogmachine-${profile}"
mkdir -p "evidence/$profile"
cleanup() {
  docker cp "$container:/workspace/.fogmachine-runs/." "evidence/$profile/" || true
  docker rm -f "$container" >/dev/null
}
docker create --name "$container" -e FOGMACHINE_IMAGE="$FOGMACHINE_IMAGE" "$FOGMACHINE_IMAGE" >/dev/null
trap cleanup EXIT
docker cp "$checkout/." "$container:/workspace"
docker start "$container" >/dev/null
docker exec --user root "$container" chown -R ubuntu:ubuntu /workspace
for operation in setup doctor check; do
  docker exec "$container" /opt/fogmachine/dev "$operation" --profile "$profile"
done
