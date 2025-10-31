#!/bin/bash

# Script de Restauração do Banco de Dados PostgreSQL
# SafeScore Brasil - safetyscorebrasil.com.br

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_DIR="./backups"

echo -e "${GREEN}🔄 Script de Restauração de Banco de Dados${NC}"
echo ""

# Verificar se há backups disponíveis
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR/*.sql.gz 2>/dev/null)" ]; then
    echo -e "${RED}❌ Nenhum backup encontrado em $BACKUP_DIR${NC}"
    exit 1
fi

# Listar backups disponíveis
echo -e "${GREEN}📋 Backups disponíveis:${NC}"
ls -lh "$BACKUP_DIR"/backup_*.sql.gz | nl

echo ""
read -p "Digite o número do backup para restaurar (ou 'cancelar' para sair): " choice

if [ "$choice" = "cancelar" ] || [ -z "$choice" ]; then
    echo "Operação cancelada."
    exit 0
fi

# Obter nome do arquivo selecionado
BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*.sql.gz | sed -n "${choice}p")

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup inválido!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⚠️  ATENÇÃO: Esta operação vai substituir TODOS os dados atuais do banco!${NC}"
read -p "Tem certeza que deseja continuar? (digite 'SIM' para confirmar): " confirm

if [ "$confirm" != "SIM" ]; then
    echo "Operação cancelada."
    exit 0
fi

# Verificar se o container do banco está rodando
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Iniciando container do banco de dados...${NC}"
    docker-compose up -d db
    sleep 5
fi

# Restaurar backup
echo -e "${GREEN}📥 Restaurando backup: $BACKUP_FILE${NC}"

# Dropar banco existente e criar novo
docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS safetyscore_db;"
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE safetyscore_db;"

# Restaurar dados
gunzip < "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres safetyscore_db

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup restaurado com sucesso!${NC}"
    echo -e "${YELLOW}⚠️  Lembre-se de executar: docker-compose restart web${NC}"
else
    echo -e "${RED}❌ Erro ao restaurar backup!${NC}"
    exit 1
fi

