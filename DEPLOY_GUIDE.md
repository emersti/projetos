# Guia de Deploy - safetyscorebrasil.com.br

## 📋 Pré-requisitos

### Servidor AWS EC2:
- Ubuntu 22.04 LTS
- Mínimo 2GB RAM
- Mínimo 20GB de armazenamento
- Portas 22, 80, 443 abertas

### Domínio:
- safetyscorebrasil.com.br configurado
- DNS apontando para o servidor

### Banco de Dados:
- PostgreSQL 13+ (RDS ou local)
- Usuário e senha configurados

## 🚀 Deploy Automático

### 1. Conectar ao servidor:
```bash
ssh -i sua-chave.pem ubuntu@seu-servidor-ip
```

### 2. Executar script de deploy:
```bash
sudo ./deploy.sh
```

### 3. Configurar variáveis de ambiente:
```bash
sudo nano /var/www/safetyscorebrasil.com.br/.env
```

## 🔧 Deploy Manual

### 1. Atualizar sistema:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar dependências:
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib nginx redis-server git \
    build-essential libpq-dev certbot python3-certbot-nginx
```

### 3. Configurar banco de dados:
```bash
sudo -u postgres psql
CREATE DATABASE safetyscore_db;
CREATE USER safetyscore_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE safetyscore_db TO safetyscore_user;
\q
```

### 4. Clonar repositório:
```bash
cd /var/www
sudo git clone https://github.com/seu-usuario/seu-repositorio.git safetyscorebrasil.com.br
sudo chown -R ubuntu:ubuntu safetyscorebrasil.com.br
```

### 5. Configurar ambiente virtual:
```bash
cd /var/www/safetyscorebrasil.com.br
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Configurar arquivo .env:
```bash
cp env.example .env
nano .env
```

### 7. Executar migrações:
```bash
python manage.py migrate --settings=projeto_teste.settings_production
```

### 8. Coletar arquivos estáticos:
```bash
python manage.py collectstatic --noinput --settings=projeto_teste.settings_production
```

### 9. Configurar Nginx:
```bash
sudo cp nginx_config.conf /etc/nginx/sites-available/safetyscorebrasil.com.br
sudo ln -s /etc/nginx/sites-available/safetyscorebrasil.com.br /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 10. Configurar Gunicorn:
```bash
sudo cp gunicorn_config.py /var/www/safetyscorebrasil.com.br/
```

### 11. Criar serviço systemd:
```bash
sudo nano /etc/systemd/system/safetyscorebrasil.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=Gunicorn instance to serve safetyscorebrasil
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/safetyscorebrasil.com.br
Environment="PATH=/var/www/safetyscorebrasil.com.br/venv/bin"
ExecStart=/var/www/safetyscorebrasil.com.br/venv/bin/gunicorn --config gunicorn_config.py projeto_teste.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### 12. Iniciar serviços:
```bash
sudo systemctl daemon-reload
sudo systemctl enable safetyscorebrasil
sudo systemctl start safetyscorebrasil
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 13. Configurar SSL:
```bash
sudo certbot --nginx -d safetyscorebrasil.com.br -d www.safetyscorebrasil.com.br
```

## 🔍 Verificação

### 1. Verificar status dos serviços:
```bash
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx
sudo systemctl status redis-server
```

### 2. Verificar logs:
```bash
sudo journalctl -u safetyscorebrasil -f
sudo tail -f /var/log/nginx/safetyscorebrasil_error.log
```

### 3. Testar site:
```bash
curl -I https://safetyscorebrasil.com.br
```

## 🔄 Atualizações

### 1. Atualizar código:
```bash
cd /var/www/safetyscorebrasil.com.br
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=projeto_teste.settings_production
python manage.py collectstatic --noinput --settings=projeto_teste.settings_production
sudo systemctl restart safetyscorebrasil
```

### 2. Backup:
```bash
sudo -u postgres pg_dump safetyscore_db > backup_$(date +%Y%m%d).sql
```

## 🐛 Troubleshooting

### Problemas comuns:

#### 1. Erro 502 Bad Gateway:
```bash
# Verificar se Gunicorn está rodando
sudo systemctl status safetyscorebrasil
sudo journalctl -u safetyscorebrasil -f
```

#### 2. Erro de permissão:
```bash
# Corrigir permissões
sudo chown -R ubuntu:www-data /var/www/safetyscorebrasil.com.br
sudo chmod -R 755 /var/www/safetyscorebrasil.com.br
```

#### 3. Erro de banco de dados:
```bash
# Verificar conexão
sudo -u postgres psql -c "SELECT 1;"
```

#### 4. Erro de SSL:
```bash
# Renovar certificado
sudo certbot renew --dry-run
```

## 📊 Monitoramento

### 1. Logs em tempo real:
```bash
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/django.log
sudo tail -f /var/log/nginx/safetyscorebrasil_access.log
```

### 2. Status dos serviços:
```bash
sudo systemctl status safetyscorebrasil nginx redis-server
```

### 3. Uso de recursos:
```bash
htop
df -h
free -h
```

## 🔒 Segurança

### 1. Firewall:
```bash
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

### 2. Atualizações de segurança:
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Backup regular:
```bash
# Configurar cron job para backup diário
sudo crontab -e
```

## 📞 Suporte

Em caso de problemas:
1. Verificar logs
2. Verificar status dos serviços
3. Verificar configurações
4. Contatar administrador do sistema

## 🔗 Links Úteis

- [Documentação Django](https://docs.djangoproject.com/)
- [Documentação Nginx](https://nginx.org/en/docs/)
- [Documentação Gunicorn](https://docs.gunicorn.org/)
- [Documentação PostgreSQL](https://www.postgresql.org/docs/)
- [Documentação AWS](https://docs.aws.amazon.com/)