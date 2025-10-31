#!/bin/bash

# Script de Deploy Automatizado para Docker na EC2
# SafeScore Brasil - safetyscorebrasil.com.br

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando deploy da aplicação...${NC}"

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erro: docker-compose.yml não encontrado!${NC}"
    echo "Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo "Criando arquivo .env a partir do exemplo..."
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        echo -e "${YELLOW}⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!${NC}"
    else
        echo -e "${RED}❌ Erro: Arquivo env.production.example não encontrado!${NC}"
        exit 1
    fi
fi

# Criar diretórios necessários
echo -e "${GREEN}📁 Criando diretórios necessários...${NC}"
mkdir -p staticfiles media logs backups

# Parar containers existentes (se houver)
echo -e "${GREEN}🛑 Parando containers existentes...${NC}"
docker-compose down 2>/dev/null || true

# Atualizar código (se usando Git)
if [ -d ".git" ]; then
    echo -e "${GREEN}📥 Atualizando código do repositório...${NC}"
    git pull origin main || git pull origin master || echo "Nenhuma atualização disponível"
fi

# Construir imagens Docker
echo -e "${GREEN}🔨 Construindo imagens Docker...${NC}"
docker-compose build --no-cache

# Subir apenas banco de dados primeiro
echo -e "${GREEN}🗄️  Iniciando banco de dados...${NC}"
docker-compose up -d db

# Aguardar banco de dados estar pronto
echo -e "${YELLOW}⏳ Aguardando banco de dados ficar pronto...${NC}"
sleep 10

# Executar migrações
echo -e "${GREEN}🔄 Executando migrações do banco de dados...${NC}"
docker-compose run --rm web python manage.py migrate --noinput || echo "Aviso: Migrações podem ter falhado"

# Coletar arquivos estáticos
echo -e "${GREEN}📦 Coletando arquivos estáticos...${NC}"
docker-compose run --rm web python manage.py collectstatic --noinput --clear || echo "Aviso: collectstatic pode ter falhado"

# Subir todos os serviços
echo -e "${GREEN}🚀 Iniciando todos os serviços...${NC}"
docker-compose up -d

# Aguardar serviços iniciarem
echo -e "${YELLOW}⏳ Aguardando serviços iniciarem...${NC}"
sleep 15

# Verificar status
echo -e "${GREEN}📊 Status dos containers:${NC}"
docker-compose ps

# Verificar health checks
echo -e "${GREEN}🏥 Verificando saúde dos serviços...${NC}"
sleep 5

# Verificar se web está respondendo
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Serviço web está respondendo!${NC}"
else
    echo -e "${YELLOW}⚠️  Serviço web ainda não está respondendo. Verifique os logs.${NC}"
fi

# Limpar imagens antigas não utilizadas
echo -e "${GREEN}🧹 Limpando imagens antigas...${NC}"
docker image prune -f

# Mostrar informações úteis
echo ""
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo -e "${YELLOW}📝 Comandos úteis:${NC}"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Ver logs web: docker-compose logs -f web"
echo "  - Parar serviços: docker-compose stop"
echo "  - Reiniciar serviços: docker-compose restart"
echo "  - Entrar no container: docker-compose exec web bash"
echo ""
echo -e "${YELLOW}🔍 Verificando últimos logs:${NC}"
docker-compose logs --tail=20 web

