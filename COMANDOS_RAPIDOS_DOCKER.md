# ⚡ Comandos Rápidos - Docker na EC2

## 🚀 Deploy Inicial

```bash
# 1. Conectar à EC2
ssh -i sua-chave.pem ec2-user@seu-ip-ec2

# 2. Instalar Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
newgrp docker

# 3. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Transferir projeto e executar deploy
cd ~/projeto_safetyscore
./deploy-docker-ec2.sh
```

## 📋 Comandos Essenciais

### Gerenciar Containers
```bash
# Subir serviços
docker-compose up -d

# Parar serviços
docker-compose stop

# Reiniciar serviços
docker-compose restart

# Parar e remover containers
docker-compose down

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f nginx
```

### Gerenciar Aplicação Django
```bash
# Executar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Entrar no shell do Django
docker-compose exec web python manage.py shell

# Entrar no container
docker-compose exec web bash
```

### Backup e Restauração
```bash
# Criar backup do banco
./backup-db.sh

# Restaurar backup
./restore-db.sh
```

### Atualizar Aplicação
```bash
# Deploy completo (recomendado)
./deploy-docker-ec2.sh

# Ou manualmente:
git pull
docker-compose build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose up -d --build
```

## 🔍 Verificações

```bash
# Verificar se está rodando
docker-compose ps

# Testar aplicação
curl http://localhost:8000

# Ver uso de recursos
docker stats

# Ver espaço em disco
df -h
docker system df
```

## 🐛 Troubleshooting

```bash
# Ver logs de erro
docker-compose logs --tail=100 web

# Reconstruir do zero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Verificar configuração
docker-compose config

# Limpar sistema Docker
docker system prune -a
```

## 🔐 Configuração SSL

```bash
# Obter certificado Let's Encrypt
sudo certbot certonly --standalone -d seu-dominio.com.br

# Renovar certificado
sudo certbot renew
docker-compose restart nginx
```

## 📊 Monitoramento

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver apenas erros
docker-compose logs web | grep ERROR

# Verificar health checks
docker-compose ps
```

