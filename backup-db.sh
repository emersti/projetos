#!/bin/bash

# Script de Backup do Banco de Dados PostgreSQL
# SafeScore Brasil - safetyscorebrasil.com.br

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configurações
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"
RETENTION_DAYS=7

echo -e "${GREEN}💾 Iniciando backup do banco de dados...${NC}"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Verificar se o container do banco está rodando
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${RED}❌ Erro: Container do banco de dados não está rodando!${NC}"
    exit 1
fi

# Executar backup
echo -e "${GREEN}📦 Criando backup...${NC}"
docker-compose exec -T db pg_dump -U postgres safetyscore_db | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup criado com sucesso: $BACKUP_FILE ($BACKUP_SIZE)${NC}"
    
    # Remover backups antigos (manter últimos N dias)
    echo -e "${YELLOW}🧹 Removendo backups antigos (mantendo últimos $RETENTION_DAYS dias)...${NC}"
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Listar backups disponíveis
    echo ""
    echo -e "${GREEN}📋 Backups disponíveis:${NC}"
    ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | tail -5 || echo "Nenhum backup encontrado"
    
    exit 0
else
    echo -e "${RED}❌ Erro ao criar backup!${NC}"
    exit 1
fi

