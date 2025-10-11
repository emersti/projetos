#!/bin/bash

# Script de inicialização da instância EC2
# Este script é executado automaticamente quando a instância é criada

# Atualizar sistema
apt-get update
apt-get upgrade -y

# Instalar dependências do sistema
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql-client \
    git \
    htop \
    curl \
    wget \
    unzip

# Criar usuário para a aplicação
useradd -m -s /bin/bash django
usermod -aG sudo django

# Criar diretório da aplicação
mkdir -p /var/www/safetyscorebrasil
chown django:django /var/www/safetyscorebrasil

# Configurar Nginx
systemctl enable nginx
systemctl start nginx

# Configurar firewall básico
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Log da inicialização
echo "Instância inicializada em $(date)" >> /var/log/user-data.log




















