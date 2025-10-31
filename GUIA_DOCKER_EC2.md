# 🐳 Guia Completo: Deploy Docker na EC2 AWS

Este guia explica passo a passo como fazer o deploy da aplicação Django SafeScore Brasil na EC2 usando Docker e Docker Compose.

## 📋 Pré-requisitos

1. **Instância EC2 em execução** (Amazon Linux 2, Ubuntu ou similar)
2. **Acesso SSH** à instância
3. **Credenciais AWS** configuradas (se necessário)
4. **Git** instalado (ou fazer upload dos arquivos)

---

## 🔧 Passo 1: Conectar à EC2 e Preparar o Ambiente

### 1.1. Conectar via SSH

```bash
ssh -i sua-chave.pem ec2-user@seu-endereco-ec2.amazonaws.com
```

**Nota:** Substitua:
- `sua-chave.pem`: caminho para sua chave SSH
- `seu-endereco-ec2.amazonaws.com`: IP público ou DNS da sua instância

### 1.2. Atualizar o Sistema

```bash
# Para Amazon Linux 2
sudo yum update -y

# Para Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y
```

### 1.3. Instalar Docker

#### Para Amazon Linux 2:
```bash
# Instalar Docker
sudo yum install docker -y

# Ou versão mais recente
sudo amazon-linux-extras install docker

# Iniciar serviço Docker
sudo systemctl start docker
sudo systemctl enable docker  # Inicia automaticamente no boot

# Adicionar usuário ao grupo docker (para não usar sudo)
sudo usermod -aG docker ec2-user

# Recarregar grupos (ou fazer logout/login)
newgrp docker
```

#### Para Ubuntu/Debian:
```bash
# Instalar Docker
sudo apt-get install docker.io -y

# Iniciar serviço Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### 1.4. Instalar Docker Compose

```bash
# Baixar última versão
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

### 1.5. Verificar Instalações

```bash
docker --version
docker ps
docker-compose --version
```

---

## 📁 Passo 2: Preparar o Projeto na EC2

### 2.1. Criar Diretório do Projeto

```bash
# Criar diretório
mkdir -p ~/projeto_safetyscore
cd ~/projeto_safetyscore
```

### 2.2. Transferir Arquivos do Projeto

**Opção A: Via Git (Recomendado)**
```bash
# Clonar repositório
git clone seu-repositorio.git .

# Ou se já tem o projeto local, fazer push e depois clone
```

**Opção B: Via SCP (do seu computador local)**
```bash
# No seu computador local, execute:
scp -i sua-chave.pem -r /caminho/local/projeto ec2-user@seu-endereco-ec2:/home/ec2-user/projeto_safetyscore
```

**Opção C: Via Upload Manual**
- Use WinSCP, FileZilla ou similar
- Faça upload de todos os arquivos do projeto

### 2.3. Criar Arquivo de Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

**Conteúdo do `.env` (ajuste conforme necessário):**

```env
DEBUG=False
DJANGO_SETTINGS_MODULE=projeto_teste.settings_prod
DATABASE_URL=postgresql://postgres:SUA_SENHA_FORTE@db:5432/safetyscore_db
REDIS_URL=redis://redis:6379/1
SECRET_KEY=sua-chave-secreta-super-segura-gerada-aqui
ALLOWED_HOSTS=safetyscorebrasil.com.br,www.safetyscorebrasil.com.br,seu-ip-ec2
```

**Gerar SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🐳 Passo 3: Configurar e Executar Docker

### 3.1. Criar Diretórios Necessários

```bash
mkdir -p staticfiles media logs backups ssl
```

### 3.2. Ajustar docker-compose.yml (se necessário)

Edite o arquivo `docker-compose.yml` para usar variáveis de ambiente:

```bash
nano docker-compose.yml
```

Certifique-se de que as variáveis de ambiente estão corretas ou use o arquivo `.env`.

### 3.3. Construir as Imagens Docker

```bash
# Construir todas as imagens
docker-compose build

# Ou forçar rebuild
docker-compose build --no-cache
```

### 3.4. Coletar Arquivos Estáticos (Antes de Subir)

```bash
# Executar collectstatic dentro do container (depois que subir) OU:
# Criar um container temporário para isso
docker-compose run --rm web python manage.py collectstatic --noinput
```

### 3.5. Executar Migrações do Banco de Dados

```bash
# Primeiro, subir apenas o banco de dados
docker-compose up -d db

# Aguardar banco ficar pronto (alguns segundos)
sleep 10

# Executar migrações
docker-compose run --rm web python manage.py migrate

# Criar superusuário (opcional)
docker-compose run --rm web python manage.py createsuperuser
```

### 3.6. Subir Todos os Serviços

```bash
# Subir todos os serviços em background
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

---

## 🔐 Passo 4: Configurar Security Group e Firewall

### 4.1. Configurar Security Group na AWS

1. Acesse **EC2 Console** → **Security Groups**
2. Selecione o Security Group da sua instância
3. **Inbound Rules** → **Edit inbound rules**
4. Adicione as seguintes regras:

| Tipo | Protocolo | Porta | Origem | Descrição |
|------|-----------|-------|--------|-----------|
| HTTP | TCP | 80 | 0.0.0.0/0 | Tráfego HTTP |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Tráfego HTTPS |
| SSH | TCP | 22 | Seu IP | Acesso SSH |

### 4.2. Configurar Firewall Local (se necessário)

```bash
# Amazon Linux 2 (firewalld pode não estar instalado)
sudo systemctl status firewalld

# Se estiver ativo, permitir portas
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🔒 Passo 5: Configurar SSL/HTTPS (Let's Encrypt)

### 5.1. Instalar Certbot

```bash
# Para Amazon Linux 2
sudo yum install certbot -y

# Para Ubuntu
sudo apt-get install certbot -y
```

### 5.2. Obter Certificado SSL

```bash
# Parar nginx temporariamente
docker-compose stop nginx

# Gerar certificado
sudo certbot certonly --standalone -d safetyscorebrasil.com.br -d www.safetyscorebrasil.com.br

# Certificados estarão em:
# /etc/letsencrypt/live/safetyscorebrasil.com.br/
```

### 5.3. Atualizar docker-compose.yml para Montar Certificados

Adicione ao serviço nginx no `docker-compose.yml`:

```yaml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

### 5.4. Renovar Certificado Automaticamente

```bash
# Criar script de renovação
sudo nano /usr/local/bin/renew-cert.sh
```

Conteúdo:
```bash
#!/bin/bash
certbot renew --quiet
docker-compose -f /home/ec2-user/projeto_safetyscore/docker-compose.yml restart nginx
```

```bash
# Tornar executável
sudo chmod +x /usr/local/bin/renew-cert.sh

# Adicionar ao crontab (renovar duas vezes por dia)
sudo crontab -e
# Adicionar linha:
0 0,12 * * * /usr/local/bin/renew-cert.sh
```

---

## ✅ Passo 6: Verificar e Testar

### 6.1. Verificar Status dos Containers

```bash
# Ver containers em execução
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f web
docker-compose logs -f nginx
```

### 6.2. Testar Aplicação

```bash
# Testar localmente na EC2
curl http://localhost:8000

# Ou no navegador acesse:
# http://seu-ip-ec2
# https://safetyscorebrasil.com.br
```

### 6.3. Comandos Úteis de Gerenciamento

```bash
# Parar todos os serviços
docker-compose stop

# Iniciar serviços
docker-compose start

# Reiniciar serviços
docker-compose restart

# Ver logs de um serviço específico
docker-compose logs -f web

# Entrar no container
docker-compose exec web bash

# Executar comandos Django
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Reconstruir após mudanças
docker-compose up -d --build

# Parar e remover tudo (CUIDADO!)
docker-compose down

# Parar e remover volumes (CUIDADO - apaga dados!)
docker-compose down -v
```

---

## 🔄 Passo 7: Atualizar Aplicação (Deploy Contínuo)

### 7.1. Script de Deploy Automatizado

Crie um script `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy..."

# Atualizar código
git pull origin main

# Reconstruir imagens
docker-compose build

# Executar migrações
docker-compose run --rm web python manage.py migrate

# Coletar arquivos estáticos
docker-compose run --rm web python manage.py collectstatic --noinput

# Reiniciar serviços
docker-compose up -d

# Limpar imagens antigas
docker image prune -f

echo "✅ Deploy concluído!"
```

```bash
# Tornar executável
chmod +x deploy.sh

# Executar
./deploy.sh
```

---

## 📊 Passo 8: Monitoramento e Logs

### 8.1. Verificar Logs

```bash
# Todos os logs
docker-compose logs -f

# Logs específicos
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db

# Últimas 100 linhas
docker-compose logs --tail=100 web
```

### 8.2. Verificar Recursos

```bash
# Uso de recursos dos containers
docker stats

# Espaço em disco
df -h
docker system df
```

### 8.3. Backup do Banco de Dados

```bash
# Criar script de backup
nano backup-db.sh
```

Conteúdo:
```bash
#!/bin/bash
BACKUP_DIR="/home/ec2-user/projeto_safetyscore/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T db pg_dump -U postgres safetyscore_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Manter apenas últimos 7 backups
ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +8 | xargs rm -f

echo "✅ Backup criado: backup_$DATE.sql.gz"
```

```bash
chmod +x backup-db.sh

# Executar manualmente ou via cron
# Adicionar ao crontab para backup diário às 2h
0 2 * * * /home/ec2-user/projeto_safetyscore/backup-db.sh
```

---

## 🐛 Troubleshooting (Solução de Problemas)

### Problema: Container não inicia

```bash
# Ver logs de erro
docker-compose logs web

# Verificar se porta está em uso
sudo netstat -tulpn | grep 8000

# Verificar configurações
docker-compose config
```

### Problema: Erro de permissões

```bash
# Ajustar permissões de diretórios
sudo chown -R ec2-user:ec2-user ~/projeto_safetyscore
chmod -R 755 ~/projeto_safetyscore
```

### Problema: Banco de dados não conecta

```bash
# Verificar se banco está rodando
docker-compose ps db

# Ver logs do banco
docker-compose logs db

# Testar conexão
docker-compose exec db psql -U postgres -d safetyscore_db
```

### Problema: Arquivos estáticos não carregam

```bash
# Recriar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput --clear

# Verificar permissões
ls -la staticfiles/
```

---

## 📝 Checklist Final

- [ ] Docker e Docker Compose instalados
- [ ] Arquivos do projeto transferidos
- [ ] Arquivo `.env` configurado
- [ ] Diretórios criados (staticfiles, media, logs)
- [ ] Imagens Docker construídas
- [ ] Migrações executadas
- [ ] Superusuário criado (se necessário)
- [ ] Todos os serviços rodando (`docker-compose ps`)
- [ ] Security Group configurado na AWS
- [ ] SSL/HTTPS configurado (se aplicável)
- [ ] Aplicação acessível via navegador
- [ ] Scripts de backup configurados
- [ ] Monitoramento e logs funcionando

---

## 🎉 Pronto!

Sua aplicação Django está rodando com Docker na EC2! 

Para dúvidas ou problemas, consulte os logs com `docker-compose logs -f`.

---

**Última atualização:** Dezembro 2024

