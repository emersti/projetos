#!/bin/bash

# Script de Deploy Automatizado para safetyscorebrasil.com.br
# Execute como root ou com sudo

set -e

# Configurações
PROJECT_NAME="safetyscorebrasil"
DOMAIN="safetyscorebrasil.com.br"
PROJECT_DIR="/var/www/$DOMAIN"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/seu-usuario/seu-repositorio.git"
BRANCH="main"
SERVICE_NAME="safetyscorebrasil"
USER_NAME="django"  # Usuário para rodar a aplicação

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando deploy do $PROJECT_NAME para $DOMAIN...${NC}"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERRO: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] AVISO: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute este script como root ou com sudo"
fi

# Verificar conectividade com a internet
log "Verificando conectividade..."
if ! ping -c 1 google.com &> /dev/null; then
    error "Sem conectividade com a internet"
fi

# Atualizar sistema
log "Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências do sistema
log "Instalando dependências do sistema..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    certbot \
    python3-certbot-nginx \
    ufw \
    htop \
    fail2ban \
    logrotate

# Configurar fail2ban
log "Configurando fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Criar usuário para o projeto (usar 'django' se não existir)
log "Criando usuário para o projeto..."
if ! id "$USER_NAME" &>/dev/null; then
    if ! id "$PROJECT_NAME" &>/dev/null; then
        useradd -m -s /bin/bash $USER_NAME
        usermod -aG sudo $USER_NAME
        info "Usuário $USER_NAME criado"
    else
        USER_NAME="$PROJECT_NAME"
        info "Usando usuário $USER_NAME existente"
    fi
else
    info "Usuário $USER_NAME já existe"
fi

# Criar diretório do projeto
log "Criando diretório do projeto..."
mkdir -p $PROJECT_DIR
chown $USER_NAME:$USER_NAME $PROJECT_DIR

# Clonar ou atualizar repositório
log "Clonando/atualizando repositório..."
if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR
    sudo -u $USER_NAME git fetch origin
    sudo -u $USER_NAME git reset --hard origin/$BRANCH
    info "Repositório atualizado"
else
    cd /var/www
    sudo -u $USER_NAME git clone $REPO_URL $DOMAIN
    cd $PROJECT_DIR
    sudo -u $USER_NAME git checkout $BRANCH
    info "Repositório clonado"
fi

# Criar ambiente virtual
log "Criando ambiente virtual..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $USER_NAME python3 -m venv $VENV_DIR
    info "Ambiente virtual criado"
else
    info "Ambiente virtual já existe"
fi

# Ativar ambiente virtual e instalar dependências
log "Instalando dependências Python..."
sudo -u $USER_NAME $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER_NAME $VENV_DIR/bin/pip install -r requirements-prod.txt

# Configurar banco de dados PostgreSQL
log "Configurando banco de dados PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE safetyscore_db;" || true
sudo -u postgres psql -c "CREATE USER safetyscore_user WITH PASSWORD 'sua_senha_segura_aqui';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE safetyscore_db TO safetyscore_user;" || true
sudo -u postgres psql -c "ALTER USER safetyscore_user CREATEDB;" || true

# Criar arquivo .env
log "Criando arquivo .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/env.production $PROJECT_DIR/.env
    warning "Configure o arquivo .env com suas credenciais!"
    warning "Arquivo localizado em: $PROJECT_DIR/.env"
fi

# Executar migrações
log "Executando migrações do banco de dados..."
sudo -u $USER_NAME $VENV_DIR/bin/python manage.py migrate --settings=projeto_teste.settings_prod

# Criar superusuário (opcional)
log "Criando superusuário..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@safetyscorebrasil.com.br', 'admin123')" | sudo -u $USER_NAME $VENV_DIR/bin/python manage.py shell --settings=projeto_teste.settings_prod || true

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
sudo -u $USER_NAME $VENV_DIR/bin/python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod

# Criar diretórios necessários
log "Criando diretórios necessários..."
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/media
mkdir -p $PROJECT_DIR/staticfiles
chown -R $USER_NAME:$USER_NAME $PROJECT_DIR

# Configurar Nginx
log "Configurando Nginx..."
cp $PROJECT_DIR/nginx_config.conf /etc/nginx/sites-available/$DOMAIN
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
nginx -t && systemctl reload nginx

# Configurar serviço Gunicorn
log "Configurando serviço Gunicorn..."
cp $PROJECT_DIR/projeto_teste.service /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Configurar Redis
log "Configurando Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configurar PostgreSQL
log "Configurando PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

# Configurar firewall
log "Configurando firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configurar SSL com Let's Encrypt
log "Configurando SSL com Let's Encrypt..."
if ! certbot certificates | grep -q "$DOMAIN"; then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect
    info "Certificado SSL configurado"
else
    info "Certificado SSL já existe"
fi

# Configurar renovação automática do SSL
log "Configurando renovação automática do SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Configurar backup automático
log "Configurando backup automático..."
mkdir -p /var/backups/$PROJECT_NAME
cat > /etc/cron.daily/$PROJECT_NAME-backup << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/$PROJECT_NAME"
mkdir -p \$BACKUP_DIR

# Backup do banco de dados
sudo -u postgres pg_dump safetyscore_db > \$BACKUP_DIR/db_\$DATE.sql

# Backup dos arquivos de mídia
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz $PROJECT_DIR/media/

# Backup dos logs
tar -czf \$BACKUP_DIR/logs_\$DATE.tar.gz $PROJECT_DIR/logs/

# Manter apenas os últimos 7 backups
find \$BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
find \$BACKUP_DIR -name "logs_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/$PROJECT_NAME-backup

# Configurar monitoramento
log "Configurando monitoramento..."
cat > /etc/cron.daily/$PROJECT_NAME-health << EOF
#!/bin/bash
# Verificar se o serviço está rodando
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "Serviço $SERVICE_NAME não está rodando!" | mail -s "Alerta: $SERVICE_NAME Down" admin@$DOMAIN || true
    systemctl restart $SERVICE_NAME
fi

# Verificar espaço em disco
DISK_USAGE=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "Uso de disco: \$DISK_USAGE%" | mail -s "Alerta: Espaço em disco baixo" admin@$DOMAIN || true
fi

# Verificar uso de memória
MEM_USAGE=\$(free | awk 'NR==2{printf "%.2f", \$3*100/\$2}')
if (( \$(echo "\$MEM_USAGE > 90" | bc -l) )); then
    echo "Uso de memória: \$MEM_USAGE%" | mail -s "Alerta: Uso de memória alto" admin@$DOMAIN || true
fi
EOF

chmod +x /etc/cron.daily/$PROJECT_NAME-health

# Configurar logrotate
log "Configurando logrotate..."
cat > /etc/logrotate.d/$PROJECT_NAME << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $PROJECT_NAME $PROJECT_NAME
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

# Iniciar serviços
log "Iniciando serviços..."
systemctl start $SERVICE_NAME
systemctl start nginx

# Verificar status dos serviços
log "Verificando status dos serviços..."
systemctl is-active --quiet $SERVICE_NAME && info "Serviço $SERVICE_NAME: ✅ Ativo" || error "Serviço $SERVICE_NAME: ❌ Inativo"
systemctl is-active --quiet nginx && info "Nginx: ✅ Ativo" || error "Nginx: ❌ Inativo"
systemctl is-active --quiet redis-server && info "Redis: ✅ Ativo" || error "Redis: ❌ Inativo"
systemctl is-active --quiet postgresql && info "PostgreSQL: ✅ Ativo" || error "PostgreSQL: ❌ Inativo"

# Teste de conectividade
log "Testando conectividade..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
    info "Teste de conectividade: ✅ OK"
else
    warning "Teste de conectividade: ⚠️ Verificar configuração"
fi

log "✅ Deploy concluído com sucesso!"
echo -e "${GREEN}🌐 Site disponível em: https://$DOMAIN${NC}"
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo -e "${YELLOW}   1. Configure o arquivo .env com suas credenciais${NC}"
echo -e "${YELLOW}   2. Reinicie o serviço: systemctl restart $SERVICE_NAME${NC}"
echo -e "${YELLOW}   3. Configure o DNS para apontar para este servidor${NC}"
echo -e "${YELLOW}   4. Teste o site e configure monitoramento${NC}"
echo -e "${YELLOW}   5. Acesse o admin: https://$DOMAIN/admin${NC}"
echo -e "${BLUE}📊 Comandos úteis:${NC}"
echo -e "${BLUE}   Status: systemctl status $SERVICE_NAME${NC}"
echo -e "${BLUE}   Logs: journalctl -u $SERVICE_NAME -f${NC}"
echo -e "${BLUE}   Restart: systemctl restart $SERVICE_NAME${NC}"
echo -e "${BLUE}   Backup: /etc/cron.daily/$PROJECT_NAME-backup${NC}"