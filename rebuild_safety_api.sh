#!/bin/bash
set -e

CONTAINER_NAME="safety-api-container"
IMAGE_NAME="safety-api"
BACKUP_FILE="backup-db-$(date +%F).sqlite3"

echo "===== Localizando container atual ====="
CONTAINER_ID=$(docker ps -q --filter name=$CONTAINER_NAME || true)

if [ -z "$CONTAINER_ID" ]; then
    echo "⚠️ Nenhum container $CONTAINER_NAME rodando — pulando backup."
else
    echo "===== Fazendo dump do SQLite ====="
    docker cp $CONTAINER_ID:/app/db.sqlite3 "./$BACKUP_FILE"
    echo "✅ Backup criado: $BACKUP_FILE"
fi

echo "===== Parando e removendo container ====="
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "===== Removendo imagem antiga ====="
docker rmi $IMAGE_NAME 2>/dev/null || true

echo "===== Build da nova imagem ====="
docker buildx build --load -t $IMAGE_NAME .

echo "===== Subindo novo container ====="
docker run -d -p 8000:8000 \
  -e DEBUG=True \
  -e DJANGO_ALLOWED_HOSTS="54.244.42.1,54.244.42.1:8000,localhost,127.0.0.1,*" \
  -e DJANGO_CSRF_TRUSTED="http://54.244.42.1,http://54.244.42.1:8000,https://54.244.42.1,http://localhost,http://127.0.0.1" \
  -e SESSION_COOKIE_SECURE=False \
  -e CSRF_COOKIE_SECURE=False \
  -e SESSION_COOKIE_HTTPONLY=False \
  -e CSRF_COOKIE_HTTPONLY=False \
  -e SECURE_SSL_REDIRECT=False \
  -e SECURE_PROXY_SSL_HEADER="" \
  --name $CONTAINER_NAME \
  $IMAGE_NAME

echo "===== Restaurando banco no container novo ====="
NEW_ID=$(docker ps -q --filter name=$CONTAINER_NAME)

if [ -f "$BACKUP_FILE" ]; then
    docker cp "$BACKUP_FILE" $NEW_ID:/app/db.sqlite3
    echo "✅ Banco restaurado!"
else
    echo "⚠️ Nenhum backup .sqlite3 — seguindo com banco limpo."
fi

echo "===== Rodando migrações ====="
docker exec -it $NEW_ID python manage.py migrate --noinput

echo "✅ Ambiente rebuildado com sucesso!"
docker ps | grep $CONTAINER_NAME
