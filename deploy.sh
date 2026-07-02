#!/bin/bash

APP_DIR="/mnt/sh_pool/appdata/sh-web-app"
BRANCH="main"

cd "$APP_DIR" || exit 1

git fetch origin "$BRANCH"

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH")

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "$(date): No changes. Skip deploy."
  exit 0
fi

echo "$(date): Changes detected. Deploying..."

git pull origin "$BRANCH"

docker compose up -d --build

echo "$(date): Deploy complete."
