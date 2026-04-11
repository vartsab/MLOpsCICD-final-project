#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <image-tag>"
  exit 1
fi

NEW_TAG="$1"
VALUES_FILE="helm/values.yaml"

if [ ! -f "$VALUES_FILE" ]; then
  echo "Error: $VALUES_FILE not found"
  exit 1
fi

sed -i -E "s/^(  tag: ).*$/\1\"${NEW_TAG}\"/" "$VALUES_FILE"

echo "Updated image tag in ${VALUES_FILE} to ${NEW_TAG}"
grep -A3 '^image:' "$VALUES_FILE"
