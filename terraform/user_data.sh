#!/bin/bash

# Script de inicialização da instância EC2 para safetyscorebrasil.com.br
# Este script é executado automaticamente quando a instância é criada

# Configurar logging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Iniciando configuração da instância EC2 para safetyscorebrasil.com.br em $(date)"

# Atualizar sistema
echo "Atualizando sistema..."
apt-get update
apt-get upgrade -y

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    git \
    htop \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    logrotate \
    awscli \
    jq \
    bc \
    mailutils

# Configurar timezone
echo "Configurando timezone..."
timedatectl set-timezone America/Sao_Paulo

# Criar usuário para a aplicação
echo "Criando usuário para a aplicação..."
if ! id "django" &>/dev/null; then
    useradd -m -s /bin/bash django
    usermod -aG sudo django
    echo "Usuário django criado"
else
    echo "Usuário django já existe"
fi

# Criar diretório da aplicação
echo "Criando diretório da aplicação..."
mkdir -p /var/www/safetyscorebrasil.com.br
chown django:django /var/www/safetyscorebrasil.com.br

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

# Configurar Redis
echo "Configurando Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configurar Nginx
echo "Configurando Nginx..."
systemctl enable nginx
systemctl start nginx

# Configurar firewall básico
echo "Configurando firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Criar diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p /var/www/safetyscorebrasil.com.br/logs
mkdir -p /var/www/safetyscorebrasil.com.br/staticfiles
mkdir -p /var/www/safetyscorebrasil.com.br/media
mkdir -p /var/backups/safetyscorebrasil
chown -R django:django /var/www/safetyscorebrasil.com.br
chown -R django:django /var/backups/safetyscorebrasil

# Configurar fail2ban
echo "Configurando fail2ban..."
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
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Configurar logrotate
echo "Configurando logrotate..."
cat > /etc/logrotate.d/safetyscorebrasil << EOF
/var/www/safetyscorebrasil.com.br/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 django django
}
EOF

# Configurar CloudWatch Agent (opcional)
echo "Configurando CloudWatch Agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb || true
rm amazon-cloudwatch-agent.deb

# Configurar backup automático
echo "Configurando backup automático..."
cat > /etc/cron.daily/safetyscorebrasil-backup << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/safetyscorebrasil"
mkdir -p \$BACKUP_DIR

# Backup do banco de dados
sudo -u postgres pg_dump safetyscore_db > \$BACKUP_DIR/db_\$DATE.sql 2>/dev/null || true

# Backup dos arquivos de mídia
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz /var/www/safetyscorebrasil.com.br/media/ 2>/dev/null || true

# Backup dos logs
tar -czf \$BACKUP_DIR/logs_\$DATE.tar.gz /var/www/safetyscorebrasil.com.br/logs/ 2>/dev/null || true

# Manter apenas os últimos 7 backups
find \$BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
find \$BACKUP_DIR -name "logs_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/safetyscorebrasil-backup

# Configurar monitoramento de saúde
echo "Configurando monitoramento de saúde..."
cat > /etc/cron.daily/safetyscorebrasil-health << EOF
#!/bin/bash
# Verificar se os serviços estão rodando
if ! systemctl is-active --quiet safetyscorebrasil; then
    echo "Serviço safetyscorebrasil não está rodando!" | mail -s "Alerta: SafeScore Brasil Down" admin@safetyscorebrasil.com.br || true
    systemctl restart safetyscorebrasil || true
fi

# Verificar espaço em disco
DISK_USAGE=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "Uso de disco: \$DISK_USAGE%" | mail -s "Alerta: Espaço em disco baixo" admin@safetyscorebrasil.com.br || true
fi

# Verificar uso de memória
MEM_USAGE=\$(free | awk 'NR==2{printf "%.2f", \$3*100/\$2}')
if (( \$(echo "\$MEM_USAGE > 90" | bc -l) )); then
    echo "Uso de memória: \$MEM_USAGE%" | mail -s "Alerta: Uso de memória alto" admin@safetyscorebrasil.com.br || true
fi
EOF

chmod +x /etc/cron.daily/safetyscorebrasil-health

# Configurar renovação automática do SSL
echo "Configurando renovação automática do SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Criar arquivo de status
echo "Criando arquivo de status..."
cat > /var/www/safetyscorebrasil.com.br/status.txt << EOF
SafeScore Brasil - Status da Instância
=====================================
Domínio: safetyscorebrasil.com.br
Usuário: django
Diretório: /var/www/safetyscorebrasil.com.br
Inicializado em: $(date)
Timezone: America/Sao_Paulo
Versão do Python: $(python3 --version)
Versão do PostgreSQL: $(sudo -u postgres psql -c "SELECT version();" | head -1)
Versão do Redis: $(redis-server --version | head -1)
Versão do Nginx: $(nginx -v 2>&1)
EOF

# Log da inicialização
echo "Instância inicializada com sucesso em $(date)" >> /var/log/user-data.log
echo "Domínio: safetyscorebrasil.com.br" >> /var/log/user-data.log
echo "Usuário: django" >> /var/log/user-data.log
echo "Diretório: /var/www/safetyscorebrasil.com.br" >> /var/log/user-data.log
echo "Timezone: America/Sao_Paulo" >> /var/log/user-data.log

# Sinalizar que a inicialização foi concluída
touch /var/www/safetyscorebrasil.com.br/initialization-complete

echo "✅ Inicialização da instância EC2 concluída com sucesso!"
echo "🌐 Pronto para receber o deploy do SafeScore Brasil"
echo "📝 Próximos passos:"
echo "   1. Execute o script de deploy"
echo "   2. Configure o arquivo .env"
echo "   3. Configure o DNS"
echo "   4. Teste o site"




















