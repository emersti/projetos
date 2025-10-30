# 🚀 Guia Completo de Deploy em Produção - SafeScore Brasil
## safetyscorebrasil.com.br na AWS

### 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Opção 1: Deploy Manual (Recomendado)](#opção-1-deploy-manual-recomendado)
3. [Opção 2: Deploy com Terraform](#opção-2-deploy-com-terraform)
4. [Pós-Deploy](#pós-deploy)
5. [Manutenção](#manutenção)
6. [Troubleshooting](#troubleshooting)

---

## 📦 Pré-requisitos

### No Seu Computador Local:
- ✅ AWS CLI instalado e configurado (`aws configure`)
- ✅ Chave SSH para acessar a EC2
- ✅ Terraform instalado (se usar Opção 2)
- ✅ Git instalado
- ✅ Domínio **safetyscorebrasil.com.br** registrado (pode ser no registro.br ou Route 53)

### Conta AWS:
- ✅ Conta AWS ativa
- ✅ Permissões para criar recursos (EC2, RDS, VPC, etc.)
- ✅ Credenciais de acesso configuradas

---

## 🎯 Opção 1: Deploy Manual (Recomendado)

### Passo 1: Criar Instância EC2

1. Acesse o [AWS Console](https://console.aws.amazon.com)
2. Vá para **EC2** > **Instâncias** > **Lançar instância**

**Configurações:**
- **Nome**: safetyscorebrasil-prod
- **AMI**: Ubuntu Server 22.04 LTS (ami-0c02fb55956c7d316 ou similar)
- **Tipo de instância**: `t3.small` (recomendado) ou `t3.micro` (tier gratuito)
- **Par de chaves**: Crie ou selecione uma chave SSH existente
- **Security Group**: Crie um novo com:
  - SSH (22): Seu IP
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
- **Armazenamento**: 30GB GP3 (encrypted)

### Passo 2: Criar Instância RDS PostgreSQL

1. Vá para **RDS** > **Bancos de dados** > **Criar banco de dados**

**Configurações:**
- **Engine**: PostgreSQL
- **Versão**: 15.4
- **Template**: Desenvolvimento/teste
- **Identificador**: `safetyscorebrasil-db`
- **Usuário mestre**: `admin`
- **Senha**: [Crie uma senha forte]
- **Tipo de instância**: `db.t3.micro` (tier gratuito) ou `db.t3.small`
- **Armazenamento**: 20GB (auto-scaling até 100GB)
- **VPC**: Mesma VPC da EC2
- **Security Group**: Permitir acesso apenas do Security Group da EC2 (porta 5432)
- **Backup automático**: Habilitado (7 dias)
- **Multi-AZ**: Desabilitado (para economizar custos)

**Anote o endpoint do RDS** (ex: `safetyscorebrasil-db.xxxxx.us-east-1.rds.amazonaws.com`)

### Passo 3: Conectar à EC2

```bash
# No seu computador local
ssh -i sua-chave.pem ubuntu@SEU-IP-EC2
```

### Passo 4: Upload do Projeto

**Opção A: Via Git (Recomendado)**
```bash
# Na EC2
cd /home/ubuntu
git clone https://github.com/seu-usuario/seu-repositorio.git safetyscorebrasil
cd safetyscorebrasil
```

**Opção B: Via SCP**
```bash
# No seu computador local
scp -r -i sua-chave.pem . ubuntu@SEU-IP-EC2:/home/ubuntu/safetyscorebrasil/
```

### Passo 5: Executar Script de Deploy

```bash
# Na EC2
cd /home/ubuntu/safetyscorebrasil
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

O script irá:
- ✅ Instalar todas as dependências
- ✅ Configurar PostgreSQL, Redis, Nginx
- ✅ Criar ambiente virtual Python
- ✅ Instalar dependências Python
- ✅ Configurar serviços systemd
- ✅ Configurar SSL com Let's Encrypt
- ✅ Configurar firewall
- ✅ Configurar backups automáticos

### Passo 6: Configurar Variáveis de Ambiente

```bash
# Na EC2
sudo nano /var/www/safetyscorebrasil.com.br/.env
```

Edite o arquivo `.env` com:

```bash
# Django
SECRET_KEY=SUA-CHAVE-SECRETA-GERE-UMA-NOVA
DEBUG=False
ALLOWED_HOSTS=safetyscorebrasil.com.br,www.safetyscorebrasil.com.br

# Banco de Dados RDS
DATABASE_URL=postgresql://admin:SUA-SENHA-RDS@seu-endpoint-rds.amazonaws.com:5432/projetoteste

# Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
```

### Passo 7: Executar Migrações e Configurar Banco

```bash
# Na EC2
cd /var/www/safetyscorebrasil.com.br
source venv/bin/activate

# Executar migrações
python manage.py migrate --settings=projeto_teste.settings_prod

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod

# Importar dados de criminalidade
python manage.py importar_dados_criminalidade --file ResumoCriminalidadeCidades.xlsx
```

### Passo 8: Reiniciar Serviços

```bash
# Na EC2
sudo systemctl restart safetyscorebrasil
sudo systemctl restart nginx
sudo systemctl status safetyscorebrasil
```

### Passo 9: Configurar DNS

**Se usar Route 53:**
1. Vá para **Route 53** > **Zonas hospedadas**
2. Crie uma zona para `safetyscorebrasil.com.br`
3. Crie registros A apontando para o IP da EC2 (ou Elastic IP)
4. Configure os nameservers no registro.br

**Se usar registro.br:**
1. Acesse o painel do registro.br
2. Configure DNS:
   - Tipo A: `@` → IP da EC2
   - Tipo A: `www` → IP da EC2
   - Ou configure os nameservers do Route 53

### Passo 10: Configurar SSL (se não foi automático)

```bash
# Na EC2
sudo certbot --nginx -d safetyscorebrasil.com.br -d www.safetyscorebrasil.com.br --non-interactive --agree-tos --email admin@safetyscorebrasil.com.br --redirect
```

---

## 🤖 Opção 2: Deploy com Terraform (Avançado)

### Passo 1: Configurar Terraform

```bash
# No seu computador local
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edite `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
project_name = "safetyscorebrasil"
domain_name = "safetyscorebrasil.com.br"
db_password = "SUA-SENHA-SEGURA-DO-BANCO"
```

### Passo 2: Executar Terraform

```bash
# Inicializar
terraform init

# Verificar plano
terraform plan

# Aplicar
terraform apply
```

Isso criará:
- ✅ VPC com subnets públicas e privadas
- ✅ Security Groups
- ✅ Instância EC2
- ✅ Instância RDS PostgreSQL
- ✅ Elastic IP
- ✅ Route 53 Hosted Zone
- ✅ Certificado SSL (ACM)

### Passo 3: Deploy da Aplicação

Após o Terraform criar a infraestrutura:

```bash
# Obter IP da EC2
EC2_IP=$(terraform output -raw ec2_public_ip)

# Upload dos arquivos
scp -r -i sua-chave.pem . ubuntu@$EC2_IP:/home/ubuntu/

# Conectar e executar deploy
ssh -i sua-chave.pem ubuntu@$EC2_IP
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### Passo 4: Configurar DNS

Use os nameservers retornados pelo Terraform:

```bash
terraform output nameservers
```

Configure no registro.br ou no seu provedor de DNS.

---

## ✅ Pós-Deploy

### Verificar Status

```bash
# Verificar serviços
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx
sudo systemctl status redis-server
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u safetyscorebrasil -f
sudo tail -f /var/log/nginx/safetyscorebrasil_access.log
sudo tail -f /var/log/nginx/safetyscorebrasil_error.log

# Testar aplicação
curl -I http://localhost:8000
curl -I https://safetyscorebrasil.com.br
```

### Criar Superusuário Admin

```bash
cd /var/www/safetyscorebrasil.com.br
source venv/bin/activate
python manage.py createsuperuser --settings=projeto_teste.settings_prod
```

### Importar Dados Iniciais

```bash
# Importar dados de criminalidade
python manage.py importar_dados_criminalidade --file ResumoCriminalidadeCidades.xlsx

# Verificar cidades
python manage.py verificar_cidades
```

---

## 🔧 Manutenção

### Atualizar Aplicação

```bash
cd /var/www/safetyscorebrasil.com.br

# Atualizar código
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements-prod.txt

# Executar migrações
python manage.py migrate --settings=projeto_teste.settings_prod

# Coletar estáticos
python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod

# Reiniciar serviços
sudo systemctl restart safetyscorebrasil
```

### Backup Manual

```bash
# Backup do banco de dados
sudo -u postgres pg_dump safetyscore_db > backup_$(date +%Y%m%d).sql

# Backup dos arquivos
tar -czf backup_files_$(date +%Y%m%d).tar.gz /var/www/safetyscorebrasil.com.br/media/
```

### Monitorar Recursos

```bash
# Uso de CPU e memória
htop

# Espaço em disco
df -h

# Logs em tempo real
sudo journalctl -u safetyscorebrasil -f
```

---

## 🆘 Troubleshooting

### Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status safetyscorebrasil

# Reiniciar serviço
sudo systemctl restart safetyscorebrasil

# Verificar logs
sudo journalctl -u safetyscorebrasil -n 50
```

### Erro de Conexão com Banco de Dados

```bash
# Verificar conexão
psql -h seu-endpoint-rds.amazonaws.com -U admin -d projetoteste

# Verificar Security Group do RDS
# Deve permitir acesso do Security Group da EC2
```

### Erro de SSL

```bash
# Renovar certificado
sudo certbot renew --dry-run

# Verificar certificado
sudo certbot certificates
```

### Aplicação Não Está Acessível

```bash
# Verificar firewall
sudo ufw status

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx

# Verificar se porta está aberta
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

---

## 📊 Checklist Final

- [ ] Instância EC2 criada e acessível
- [ ] Instância RDS criada e acessível
- [ ] Projeto deployado na EC2
- [ ] Variáveis de ambiente configuradas (.env)
- [ ] Migrações executadas
- [ ] Arquivos estáticos coletados
- [ ] Dados de criminalidade importados
- [ ] Serviços rodando (Gunicorn, Nginx, Redis, PostgreSQL)
- [ ] SSL configurado (Let's Encrypt)
- [ ] DNS configurado (apontando para EC2)
- [ ] Site acessível em https://safetyscorebrasil.com.br
- [ ] Backups automáticos configurados
- [ ] Monitoramento configurado
- [ ] Superusuário criado

---

## 🔗 Links Úteis

- **Admin Django**: https://safetyscorebrasil.com.br/admin
- **Painel Admin**: https://safetyscorebrasil.com.br/painel/login/
- **AWS Console**: https://console.aws.amazon.com
- **Route 53**: https://console.aws.amazon.com/route53

---

## 📞 Suporte

Para problemas ou dúvidas:
- Verifique os logs: `sudo journalctl -u safetyscorebrasil -f`
- Documentação Django: https://docs.djangoproject.com/
- AWS Documentation: https://docs.aws.amazon.com/

---

**Status**: ✅ Pronto para Produção  
**Domínio**: safetyscorebrasil.com.br  
**Última Atualização**: Janeiro 2025

