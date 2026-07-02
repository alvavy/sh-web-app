#!/bin/bash

# 환경 변수 추가 (Cron이 git과 docker 명령어를 찾을 수 있게 함)
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

APP_DIR="/mnt/sh_pool/appdata/sh-web-app"
BRANCH="main"

cd "$APP_DIR" || exit 1

# 절대 경로를 사용해 git fetch 실행
/usr/bin/git fetch origin "$BRANCH"

LOCAL=$(/usr/bin/git rev-parse HEAD)
REMOTE=$(/usr/bin/git rev-parse "origin/$BRANCH")

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "$(date): No changes. Skip deploy."
  exit 0
fi

echo "$(date): Changes detected. Deploying..."

/usr/bin/git pull origin "$BRANCH"

# docker compose 절대 경로로 실행 (버전에 따라 docker-compose 일 수 있음)
/usr/bin/docker compose up -d --build

