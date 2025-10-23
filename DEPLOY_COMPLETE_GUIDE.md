# 🚀 Guia Completo de Deploy em Produção - SafeScore Brasil

## 📋 Visão Geral

Este projeto está completamente preparado para deploy em produção na AWS com o domínio **safetyscorebrasil.com.br**. Todas as configurações foram otimizadas para segurança, performance e escalabilidade.

## 🏗️ Arquitetura de Produção

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Route 53      │    │   CloudFront    │    │   Load Balancer │
│   (DNS)         │────│   (CDN)         │────│   (ALB)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EC2 Instance  │    │   RDS PostgreSQL│    │   ElastiCache   │
│   (Django App)  │────│   (Database)    │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes:
- **Frontend**: Django Templates + CSS/JavaScript
- **Backend**: Django 4.2.7 + Python 3.11
- **Banco de Dados**: PostgreSQL (RDS AWS)
- **Cache**: Redis (ElastiCache)
- **Servidor Web**: Nginx + Gunicorn
- **SSL**: Let's Encrypt (automático)
- **Deploy**: AWS EC2 + Terraform
- **Domínio**: safetyscorebrasil.com.br

## 🚀 Opções de Deploy

### Opção 1: Deploy Manual (Recomendado para iniciantes)

#### 1. Criar Instância EC2
```bash
# Especificações recomendadas:
# - Ubuntu 22.04 LTS
# - Tipo: t3.small (2 vCPU, 2GB RAM)
# - Storage: 30GB GP3
# - Security Group: SSH (22), HTTP (80), HTTPS (443)
```

#### 2. Conectar à Instância
```bash
ssh -i sua-chave.pem ubuntu@seu-ip-ec2
```

#### 3. Executar Deploy Automatizado
```bash
# Upload dos arquivos do projeto
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
DATABASE_URL=postgresql://safetyscore_user:senha@localhost:5432/safetyscore_db
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

#### 5. Configurar Banco de Dados RDS (Opcional)
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

### Opção 3: Deploy com Docker

#### 1. Configurar Docker Compose
```bash
# Copiar arquivo de ambiente
cp env.production .env

# Editar variáveis
nano .env
```

#### 2. Executar Deploy
```bash
docker-compose up -d
```

#### 3. Executar Migrações
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
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
- **Rate Limiting**: Configurado
- **Compressão**: Gzip habilitado
- **Cache**: Arquivos estáticos

### 3. PostgreSQL (Banco de Dados)
- **Porta**: 5432
- **Database**: safetyscore_db
- **Usuário**: safetyscore_user
- **Backup**: Automático diário

### 4. Redis (Cache)
- **Porta**: 6379
- **Database**: 1
- **Persistência**: Configurada

### 5. Celery (Tarefas Assíncronas)
- **Worker**: Processamento em background
- **Beat**: Agendamento de tarefas
- **Broker**: Redis

## 📊 Monitoramento e Logs

### Logs
```bash
# Logs da aplicação
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/django.log

# Logs do Gunicorn
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/gunicorn_*.log

# Logs do Nginx
sudo tail -f /var/log/nginx/safetyscorebrasil_*.log

# Logs do sistema
sudo journalctl -u safetyscorebrasil -f
```

### Status dos Serviços
```bash
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx
sudo systemctl status redis-server
sudo systemctl status postgresql
```

### Monitoramento Automático
- **Health Checks**: Configurados para todos os serviços
- **Alertas**: Email automático em caso de problemas
- **Backup**: Automático diário com retenção de 7 dias
- **Log Rotation**: Configurado para 30 dias

## 🔄 Atualizações e Manutenção

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

### Deploy com Docker
```bash
docker-compose pull
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup Manual
```bash
# Backup do banco de dados
sudo -u postgres pg_dump safetyscore_db > backup_$(date +%Y%m%d).sql

# Backup dos arquivos
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/safetyscorebrasil.com.br/media/
```

## 🔒 Segurança

### Configurações Implementadas
- ✅ HTTPS obrigatório
- ✅ Headers de segurança
- ✅ Firewall configurado (UFW)
- ✅ Fail2ban para proteção contra ataques
- ✅ SSL/TLS otimizado
- ✅ Rate limiting no Nginx
- ✅ Backup automático
- ✅ Logs de auditoria
- ✅ Usuário não-root para aplicação

### Certificado SSL
- **Provedor**: Let's Encrypt
- **Renovação**: Automática via cron
- **Validação**: HTTP-01
- **HSTS**: Configurado

### Firewall
```bash
# Regras configuradas:
# - SSH (22): Permitido
# - HTTP (80): Permitido
# - HTTPS (443): Permitido
# - Outros: Negados por padrão
```

## 📈 Performance

### Otimizações Implementadas
- ✅ Compressão Gzip
- ✅ Cache de arquivos estáticos
- ✅ Redis para cache de aplicação
- ✅ CDN (CloudFront) opcional
- ✅ Compressão de imagens
- ✅ Minificação de CSS/JS
- ✅ Database indexing
- ✅ Query optimization

### Métricas Esperadas
- **Tempo de Resposta**: < 200ms
- **Uptime**: 99.9%
- **Throughput**: 1000 req/s
- **Cache Hit Rate**: > 90%

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
# Verificar conexão local
sudo -u postgres psql -c "SELECT 1;"

# Verificar conexão RDS
psql -h seu-rds-endpoint -U admin -d projetoteste
```

#### 4. Erro de SSL
```bash
sudo certbot renew --dry-run
```

#### 5. Erro de Cache Redis
```bash
redis-cli ping
sudo systemctl restart redis-server
```

### Comandos Úteis
```bash
# Status geral
sudo systemctl status safetyscorebrasil nginx redis-server postgresql

# Logs em tempo real
sudo journalctl -u safetyscorebrasil -f

# Reiniciar serviços
sudo systemctl restart safetyscorebrasil
sudo systemctl restart nginx

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos
htop
```

## 📞 Suporte e Monitoramento

### Contatos
- **Email**: admin@safetyscorebrasil.com.br
- **Documentação**: Este arquivo
- **AWS Console**: https://console.aws.amazon.com/

### Logs de Suporte
```bash
# Verificar logs de erro
sudo grep -i error /var/www/safetyscorebrasil.com.br/logs/django.log

# Verificar logs de acesso
sudo tail -f /var/log/nginx/safetyscorebrasil_access.log

# Verificar logs do sistema
sudo journalctl -u safetyscorebrasil --since "1 hour ago"
```

### Alertas Configurados
- **Serviço Down**: Email automático
- **Espaço em Disco**: Alerta em 80%
- **Uso de Memória**: Alerta em 90%
- **SSL Expiry**: Renovação automática

## 🔗 Links Úteis

- [Django Documentation](https://docs.djangoproject.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 📋 Checklist de Deploy

### Pré-Deploy
- [ ] Instância EC2 criada
- [ ] Security Group configurado
- [ ] Chave SSH configurada
- [ ] Domínio registrado
- [ ] DNS configurado

### Deploy
- [ ] Script de deploy executado
- [ ] Arquivo .env configurado
- [ ] Banco de dados configurado
- [ ] Migrações executadas
- [ ] Arquivos estáticos coletados
- [ ] Serviços iniciados

### Pós-Deploy
- [ ] SSL configurado
- [ ] Site funcionando
- [ ] Admin acessível
- [ ] Logs funcionando
- [ ] Backup configurado
- [ ] Monitoramento ativo

### Testes
- [ ] Site carrega corretamente
- [ ] HTTPS funcionando
- [ ] Admin acessível
- [ ] Formulários funcionando
- [ ] Banco de dados conectado
- [ ] Cache funcionando

---

**Status**: ✅ Pronto para Produção  
**Domínio**: safetyscorebrasil.com.br  
**Última Atualização**: Janeiro 2025  
**Versão**: 2.0.0  
**Favicon**: ✅ Implementado (círculo laranja com "S" branca)
