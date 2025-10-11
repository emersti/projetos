#!/bin/bash

# Script de Deploy para safetyscorebrasil.com.br
# Execute como root ou com sudo

set -e

# Configurações
PROJECT_NAME="safetyscorebrasil"
DOMAIN="safetyscorebrasil.com.br"
PROJECT_DIR="/var/www/$DOMAIN"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/seu-usuario/seu-repositorio.git"
BRANCH="main"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando deploy do $PROJECT_NAME...${NC}"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERRO: $1${NC}"
    exit 1
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute este script como root ou com sudo"
fi

# Atualizar sistema
log "Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências do sistema
log "Instalando dependências do sistema..."
apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    nginx apache2-utils \
    redis-server \
    git curl wget \
    build-essential libpq-dev \
    certbot python3-certbot-nginx

# Criar usuário para o projeto
log "Criando usuário para o projeto..."
if ! id "$PROJECT_NAME" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_NAME
fi

# Criar diretório do projeto
log "Criando diretório do projeto..."
mkdir -p $PROJECT_DIR
chown $PROJECT_NAME:$PROJECT_NAME $PROJECT_DIR

# Clonar ou atualizar repositório
log "Clonando/atualizando repositório..."
if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR
    sudo -u $PROJECT_NAME git pull origin $BRANCH
else
    cd /var/www
    sudo -u $PROJECT_NAME git clone $REPO_URL $DOMAIN
    cd $PROJECT_DIR
    sudo -u $PROJECT_NAME git checkout $BRANCH
fi

# Criar ambiente virtual
log "Criando ambiente virtual..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $PROJECT_NAME python3 -m venv $VENV_DIR
fi

# Ativar ambiente virtual e instalar dependências
log "Instalando dependências Python..."
sudo -u $PROJECT_NAME $VENV_DIR/bin/pip install --upgrade pip
sudo -u $PROJECT_NAME $VENV_DIR/bin/pip install -r requirements.txt

# Configurar banco de dados
log "Configurando banco de dados..."
sudo -u postgres psql -c "CREATE DATABASE safetyscore_db;" || true
sudo -u postgres psql -c "CREATE USER safetyscore_user WITH PASSWORD 'sua_senha_aqui';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE safetyscore_db TO safetyscore_user;" || true

# Criar arquivo .env
log "Criando arquivo .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/env.example $PROJECT_DIR/.env
    echo -e "${YELLOW}⚠️  Configure o arquivo .env com suas credenciais!${NC}"
fi

# Executar migrações
log "Executando migrações..."
sudo -u $PROJECT_NAME $VENV_DIR/bin/python manage.py migrate --settings=projeto_teste.settings_production

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
sudo -u $PROJECT_NAME $VENV_DIR/bin/python manage.py collectstatic --noinput --settings=projeto_teste.settings_production

# Criar diretório de logs
log "Criando diretório de logs..."
mkdir -p $PROJECT_DIR/logs
chown $PROJECT_NAME:$PROJECT_NAME $PROJECT_DIR/logs

# Configurar Nginx
log "Configurando Nginx..."
cp $PROJECT_DIR/nginx_config.conf /etc/nginx/sites-available/$DOMAIN
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Configurar Gunicorn
log "Configurando Gunicorn..."
cat > /etc/systemd/system/$PROJECT_NAME.service << EOF
[Unit]
Description=Gunicorn instance to serve $PROJECT_NAME
After=network.target

[Service]
User=$PROJECT_NAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 projeto_teste.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Iniciar serviços
log "Iniciando serviços..."
systemctl daemon-reload
systemctl enable $PROJECT_NAME
systemctl start $PROJECT_NAME
systemctl enable nginx
systemctl start nginx
systemctl enable redis-server
systemctl start redis-server

# Configurar SSL com Let's Encrypt
log "Configurando SSL..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Configurar firewall
log "Configurando firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Configurar backup automático
log "Configurando backup automático..."
cat > /etc/cron.daily/$PROJECT_NAME-backup << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/$PROJECT_NAME"
mkdir -p \$BACKUP_DIR

# Backup do banco de dados
sudo -u postgres pg_dump safetyscore_db > \$BACKUP_DIR/db_\$DATE.sql

# Backup dos arquivos de mídia
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz $PROJECT_DIR/media/

# Manter apenas os últimos 7 backups
find \$BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/$PROJECT_NAME-backup

# Configurar monitoramento
log "Configurando monitoramento..."
cat > /etc/cron.daily/$PROJECT_NAME-health << EOF
#!/bin/bash
# Verificar se o serviço está rodando
if ! systemctl is-active --quiet $PROJECT_NAME; then
    echo "Serviço $PROJECT_NAME não está rodando!" | mail -s "Alerta: $PROJECT_NAME Down" admin@$DOMAIN
    systemctl restart $PROJECT_NAME
fi

# Verificar espaço em disco
DISK_USAGE=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "Uso de disco: \$DISK_USAGE%" | mail -s "Alerta: Espaço em disco baixo" admin@$DOMAIN
fi
EOF

chmod +x /etc/cron.daily/$PROJECT_NAME-health

log "✅ Deploy concluído com sucesso!"
echo -e "${GREEN}🌐 Site disponível em: https://$DOMAIN${NC}"
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo -e "${YELLOW}   1. Configure o arquivo .env com suas credenciais${NC}"
echo -e "${YELLOW}   2. Reinicie o serviço: systemctl restart $PROJECT_NAME${NC}"
echo -e "${YELLOW}   3. Configure o DNS para apontar para este servidor${NC}"
echo -e "${YELLOW}   4. Teste o site e configure monitoramento${NC}"