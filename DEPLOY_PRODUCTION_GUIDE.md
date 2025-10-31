# 🚀 Guia de Deploy em Produção - SafeScore Brasil

## 📋 Visão Geral

Este projeto está configurado para deploy em produção na AWS com o domínio **safetyscorebrasil.com.br**.

## 🏗️ Arquitetura de Produção

- **Frontend**: Django Templates + CSS/JavaScript
- **Backend**: Django 4.2.7 + Python 3.11
- **Banco de Dados**: PostgreSQL (RDS AWS)
- **Servidor Web**: Nginx + Gunicorn
- **Cache**: Redis
- **SSL**: Let's Encrypt
- **Deploy**: AWS EC2 + Terraform
- **Domínio**: safetyscorebrasil.com.br

## 🚀 Deploy Rápido na AWS

### Opção 1: Deploy Manual (Recomendado)

#### 1. Criar Instância EC2
```bash
# Ubuntu 22.04 LTS
# Tipo: t3.micro (tier gratuito)
# Security Group: SSH (22), HTTP (80), HTTPS (443)
# Storage: 20GB GP3
```

#### 2. Conectar à Instância
```bash
ssh -i sua-chave.pem ubuntu@seu-ip-ec2
```

#### 3. Executar Deploy
```bash
# Upload dos arquivos
scp -r -i sua-chave.pem . ubuntu@seu-ip-ec2:/home/ubuntu/

# Na EC2, executar:
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

#### 4. Configurar Variáveis de Ambiente
```bash
sudo nano /var/www/safetyscorebrasil.com.br/.env
```

Configure com suas credenciais:
```bash
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=safetyscorebrasil.com.br,www.safetyscorebrasil.com.br
DATABASE_URL=postgresql://admin:senha@seu-rds-endpoint:5432/projetoteste
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

#### 5. Configurar Banco de Dados RDS
```bash
# Criar instância RDS PostgreSQL
# Tipo: db.t3.micro (tier gratuito)
# Engine: PostgreSQL 15.4
# Usuário: admin
# Senha: [senha segura]
# Database: projetoteste
```

### Opção 2: Deploy com Terraform (Avançado)

#### 1. Configurar Terraform
```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

Edite `terraform.tfvars`:
```hcl
aws_region = "us-east-1"
project_name = "safetyscorebrasil"
domain_name = "safetyscorebrasil.com.br"
db_password = "sua-senha-segura"
```

#### 2. Executar Terraform
```bash
terraform init
terraform plan
terraform apply
```

#### 3. Configurar DNS
```bash
# Use os nameservers do Route 53 retornados pelo Terraform
# Configure no seu provedor de domínio
```

## ⚙️ Configurações Importantes

### Variáveis de Ambiente (.env)
```bash
# Django
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=safetyscorebrasil.com.br,www.safetyscorebrasil.com.br

# Banco de Dados
DATABASE_URL=postgresql://admin:senha@seu-rds-endpoint:5432/projetoteste

# Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@safetyscorebrasil.com.br

# Cache
REDIS_URL=redis://127.0.0.1:6379/1
```

### Domínio e DNS
- **Domínio**: safetyscorebrasil.com.br
- **WWW**: www.safetyscorebrasil.com.br
- **DNS**: Apontar para IP do servidor AWS
- **SSL**: Let's Encrypt (automático)

## 🔧 Serviços Configurados

### 1. Gunicorn (Aplicação Django)
- **Porta**: 8000
- **Workers**: 3
- **Timeout**: 30s
- **Logs**: `/var/www/safetyscorebrasil.com.br/logs/`

### 2. Nginx (Servidor Web)
- **Porta**: 80 (HTTP) → 443 (HTTPS)
- **SSL**: Let's Encrypt
- **Arquivos Estáticos**: `/static/`
- **Arquivos de Mídia**: `/media/`

### 3. PostgreSQL (Banco de Dados)
- **Porta**: 5432
- **Database**: projetoteste
- **Usuário**: admin

### 4. Redis (Cache)
- **Porta**: 6379
- **Database**: 1

## 📊 Monitoramento

### Logs
```bash
# Logs da aplicação
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/django.log

# Logs do Gunicorn
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/gunicorn_*.log

# Logs do Nginx
sudo tail -f /var/log/nginx/safetyscorebrasil_*.log
```

### Status dos Serviços
```bash
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx
sudo systemctl status redis-server
```

## 🔄 Atualizações

### Deploy Manual
```bash
cd /var/www/safetyscorebrasil.com.br
git pull origin main
source venv/bin/activate
pip install -r requirements-prod.txt
python manage.py migrate --settings=projeto_teste.settings_prod
python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod
sudo systemctl restart safetyscorebrasil
```

## 🔒 Segurança

### Configurações Implementadas
- ✅ HTTPS obrigatório
- ✅ Headers de segurança
- ✅ Firewall configurado
- ✅ SSL/TLS otimizado
- ✅ Backup automático
- ✅ Logs de auditoria

### Certificado SSL
- **Provedor**: Let's Encrypt
- **Renovação**: Automática
- **Validação**: HTTP-01

## 📈 Performance

### Otimizações
- ✅ Compressão Gzip
- ✅ Cache de arquivos estáticos
- ✅ Redis para cache
- ✅ CDN (CloudFront) opcional
- ✅ Compressão de imagens

## 🆘 Troubleshooting

### Problemas Comuns

#### 1. Erro 502 Bad Gateway
```bash
sudo systemctl status safetyscorebrasil
sudo journalctl -u safetyscorebrasil -f
```

#### 2. Erro de Permissão
```bash
sudo chown -R django:www-data /var/www/safetyscorebrasil.com.br
sudo chmod -R 755 /var/www/safetyscorebrasil.com.br
```

#### 3. Erro de Banco de Dados
```bash
# Verificar conexão RDS
psql -h seu-rds-endpoint -U admin -d projetoteste
```

#### 4. Erro de SSL
```bash
sudo certbot renew --dry-run
```

## 📞 Suporte

### Contatos
- **Email**: admin@safetyscorebrasil.com.br
- **Documentação**: Este arquivo
- **AWS**: Console AWS

### Logs de Suporte
```bash
# Verificar logs de erro
sudo grep -i error /var/www/safetyscorebrasil.com.br/logs/django.log

# Verificar logs de acesso
sudo tail -f /var/log/nginx/safetyscorebrasil_access.log
```

## 🔗 Links Úteis

- [Django Documentation](https://docs.djangoproject.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Status**: ✅ Pronto para Produção  
**Domínio**: safetyscorebrasil.com.br  
**Última Atualização**: Janeiro 2025  
**Versão**: 1.0.0


