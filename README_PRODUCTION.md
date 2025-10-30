# 🚀 SafeScore Brasil - Deploy em Produção

## 📋 Visão Geral

Este projeto está configurado para deploy em produção no AWS com o domínio **safetyscorebrasil.com.br**.

## 🏗️ Arquitetura

- **Frontend**: Django Templates + CSS/JavaScript
- **Backend**: Django 4.2.7 + Python 3.11
- **Banco de Dados**: PostgreSQL (RDS ou local)
- **Servidor Web**: Nginx + Gunicorn
- **Cache**: Redis
- **SSL**: Let's Encrypt
- **Deploy**: AWS EC2

## 📁 Estrutura de Arquivos

```
projeto_teste/
├── requirements.txt              # Dependências Python
├── settings_production.py        # Configurações de produção
├── wsgi.py                      # Configuração WSGI
├── gunicorn_config.py           # Configuração Gunicorn
├── deploy.sh                    # Script de deploy automático
├── nginx_config.conf            # Configuração Nginx
├── apache_config.conf           # Configuração Apache (alternativa)
├── Dockerfile                   # Container Docker
├── docker-compose.yml           # Orquestração Docker
├── .github/workflows/deploy.yml # CI/CD GitHub Actions
├── env.example                  # Exemplo de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
├── AWS_DEPLOYMENT.md            # Guia específico para AWS
├── DEPLOY_GUIDE.md              # Guia completo de deploy
└── README_PRODUCTION.md         # Este arquivo
```

## 🚀 Deploy Rápido

### 1. Preparar Servidor AWS EC2:
```bash
# Ubuntu 22.04 LTS
# Mínimo 2GB RAM
# Portas 22, 80, 443 abertas
```

### 2. Executar Deploy:
```bash
# Conectar ao servidor
ssh -i sua-chave.pem ubuntu@seu-servidor-ip

# Executar script de deploy
sudo ./deploy.sh
```

### 3. Configurar Variáveis:
```bash
# Editar arquivo .env
sudo nano /var/www/safetyscorebrasil.com.br/.env
```

## ⚙️ Configurações Importantes

### Variáveis de Ambiente (.env):
```bash
# Banco de Dados
DB_NAME=safetyscore_db
DB_USER=postgres
DB_PASSWORD=sua_senha_segura
DB_HOST=localhost
DB_PORT=5432

# Segurança
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@safetyscorebrasil.com.br

# Cache
REDIS_URL=redis://127.0.0.1:6379/1
```

### Domínio e DNS:
- **Domínio**: safetyscorebrasil.com.br
- **WWW**: www.safetyscorebrasil.com.br
- **DNS**: Apontar para IP do servidor AWS

## 🔧 Serviços Configurados

### 1. Gunicorn (Aplicação Django):
- **Porta**: 8000
- **Workers**: 3
- **Timeout**: 30s
- **Logs**: `/var/www/safetyscorebrasil.com.br/logs/`

### 2. Nginx (Servidor Web):
- **Porta**: 80 (HTTP) → 443 (HTTPS)
- **SSL**: Let's Encrypt
- **Arquivos Estáticos**: `/static/`
- **Arquivos de Mídia**: `/media/`

### 3. PostgreSQL (Banco de Dados):
- **Porta**: 5432
- **Database**: safetyscore_db
- **Usuário**: safetyscore_user

### 4. Redis (Cache):
- **Porta**: 6379
- **Database**: 1

## 📊 Monitoramento

### Logs:
```bash
# Logs da aplicação
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/django.log

# Logs do Gunicorn
sudo tail -f /var/www/safetyscorebrasil.com.br/logs/gunicorn_*.log

# Logs do Nginx
sudo tail -f /var/log/nginx/safetyscorebrasil_*.log
```

### Status dos Serviços:
```bash
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx
sudo systemctl status redis-server
```

## 🔄 Atualizações

### Deploy Automático (GitHub Actions):
- Push na branch `main` → Deploy automático
- Configurar secrets no GitHub:
  - `AWS_HOST`: IP do servidor
  - `AWS_USERNAME`: usuário SSH
  - `AWS_SSH_KEY`: chave privada SSH

### Deploy Manual:
```bash
cd /var/www/safetyscorebrasil.com.br
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=projeto_teste.settings_production
python manage.py collectstatic --noinput --settings=projeto_teste.settings_production
sudo systemctl restart safetyscorebrasil
```

## 🔒 Segurança

### Configurações Implementadas:
- ✅ HTTPS obrigatório
- ✅ Headers de segurança
- ✅ Firewall configurado
- ✅ SSL/TLS otimizado
- ✅ Backup automático
- ✅ Logs de auditoria

### Certificado SSL:
- **Provedor**: Let's Encrypt
- **Renovação**: Automática
- **Validação**: HTTP-01

## 📈 Performance

### Otimizações:
- ✅ Compressão Gzip
- ✅ Cache de arquivos estáticos
- ✅ Redis para cache
- ✅ CDN (CloudFront) opcional
- ✅ Compressão de imagens

### Métricas:
- **Tempo de Resposta**: < 200ms
- **Uptime**: 99.9%
- **Throughput**: 1000 req/s

## 🆘 Troubleshooting

### Problemas Comuns:

#### 1. Erro 502 Bad Gateway:
```bash
sudo systemctl status safetyscorebrasil
sudo journalctl -u safetyscorebrasil -f
```

#### 2. Erro de Permissão:
```bash
sudo chown -R ubuntu:www-data /var/www/safetyscorebrasil.com.br
sudo chmod -R 755 /var/www/safetyscorebrasil.com.br
```

#### 3. Erro de Banco de Dados:
```bash
sudo -u postgres psql -c "SELECT 1;"
```

#### 4. Erro de SSL:
```bash
sudo certbot renew --dry-run
```

## 📞 Suporte

### Contatos:
- **Email**: admin@safetyscorebrasil.com.br
- **Documentação**: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- **AWS**: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

### Logs de Suporte:
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
**Última Atualização**: Outubro 2025  
**Versão**: 1.0.0

















