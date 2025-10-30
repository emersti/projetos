# ✅ Checklist de Deploy - SafeScore Brasil
## safetyscorebrasil.com.br

Use este checklist para garantir que todos os passos foram concluídos:

### 📋 Pré-Deploy

- [ ] Conta AWS configurada e ativa
- [ ] AWS CLI instalado e configurado (`aws configure`)
- [ ] Chave SSH criada e salva em local seguro
- [ ] Domínio **safetyscorebrasil.com.br** registrado
- [ ] Repositório Git atualizado com código de produção
- [ ] Arquivo `requirements-prod.txt` atualizado
- [ ] Arquivo `env.production` revisado

### 🏗️ Infraestrutura AWS

- [ ] Instância EC2 criada (Ubuntu 22.04 LTS)
  - [ ] Tipo: t3.small ou t3.micro
  - [ ] Security Group configurado (SSH, HTTP, HTTPS)
  - [ ] Armazenamento: 30GB GP3 (encrypted)
  - [ ] Elastic IP associado (opcional, recomendado)
  
- [ ] Instância RDS PostgreSQL criada
  - [ ] Versão: PostgreSQL 15.4
  - [ ] Tipo: db.t3.micro ou db.t3.small
  - [ ] Security Group permite acesso da EC2
  - [ ] Backup automático habilitado (7 dias)
  - [ ] Endpoint anotado
  
- [ ] VPC e Networking configurados (se usar Terraform)
  - [ ] VPC criada
  - [ ] Subnets públicas e privadas
  - [ ] Internet Gateway
  - [ ] Route Tables configuradas

### 📦 Deploy da Aplicação

- [ ] Conectado à EC2 via SSH
- [ ] Código do projeto transferido para EC2
  - [ ] Via Git: `git clone`
  - [ ] Via SCP: `scp`
  
- [ ] Script de deploy executado (`deploy.sh`)
  - [ ] Dependências do sistema instaladas
  - [ ] Ambiente virtual Python criado
  - [ ] Dependências Python instaladas
  - [ ] PostgreSQL configurado
  - [ ] Redis configurado
  - [ ] Nginx configurado
  - [ ] Gunicorn configurado como serviço

### ⚙️ Configuração

- [ ] Arquivo `.env` criado em `/var/www/safetyscorebrasil.com.br/.env`
  - [ ] `SECRET_KEY` gerada e configurada
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS` configurado com domínio
  - [ ] `DATABASE_URL` configurado com endpoint RDS
  - [ ] Credenciais do banco de dados corretas
  - [ ] `REDIS_URL` configurado
  - [ ] Configurações de segurança (SSL, cookies, etc.)

- [ ] Migrações do banco de dados executadas
  ```bash
  python manage.py migrate --settings=projeto_teste.settings_prod
  ```

- [ ] Arquivos estáticos coletados
  ```bash
  python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod
  ```

- [ ] Dados iniciais importados
  ```bash
  python manage.py importar_dados_criminalidade --file ResumoCriminalidadeCidades.xlsx
  ```

- [ ] Superusuário criado
  ```bash
  python manage.py createsuperuser --settings=projeto_teste.settings_prod
  ```

### 🌐 DNS e SSL

- [ ] DNS configurado
  - [ ] Registro A para `safetyscorebrasil.com.br` → IP da EC2
  - [ ] Registro A para `www.safetyscorebrasil.com.br` → IP da EC2
  - [ ] Ou nameservers do Route 53 configurados no registro.br
  
- [ ] SSL/TLS configurado
  - [ ] Certificado Let's Encrypt obtido
  - [ ] Renovação automática configurada
  - [ ] HTTPS funcionando (redirecionamento HTTP → HTTPS)

### 🔒 Segurança

- [ ] Firewall configurado (UFW)
  - [ ] SSH (22) permitido apenas do seu IP
  - [ ] HTTP (80) permitido
  - [ ] HTTPS (443) permitido
  
- [ ] Fail2ban configurado e ativo
- [ ] Senhas fortes configuradas (banco, admin, etc.)
- [ ] SECRET_KEY única e segura
- [ ] Headers de segurança configurados no Nginx

### 📊 Serviços

- [ ] Serviços rodando e habilitados:
  ```bash
  sudo systemctl status safetyscorebrasil  # ✅
  sudo systemctl status nginx              # ✅
  sudo systemctl status redis-server       # ✅
  sudo systemctl status postgresql        # ✅ (se local)
  ```

- [ ] Logs verificados (sem erros críticos):
  ```bash
  sudo journalctl -u safetyscorebrasil -n 50
  sudo tail -f /var/log/nginx/safetyscorebrasil_error.log
  ```

### 🧪 Testes

- [ ] Site acessível via HTTP (redireciona para HTTPS)
- [ ] Site acessível via HTTPS: `https://safetyscorebrasil.com.br`
- [ ] WWW redirecionando corretamente: `https://www.safetyscorebrasil.com.br`
- [ ] Página inicial carregando corretamente
- [ ] Formulário de consulta funcionando
- [ ] API de cidades funcionando (`/api/cidades/`)
- [ ] Admin Django acessível: `https://safetyscorebrasil.com.br/admin`
- [ ] Painel admin acessível: `https://safetyscorebrasil.com.br/painel/login/`
- [ ] Arquivos estáticos carregando (CSS, JS, imagens)
- [ ] SSL válido (sem avisos de certificado)

### 💾 Backup e Monitoramento

- [ ] Backup automático configurado (`/etc/cron.daily/safetyscorebrasil-backup`)
- [ ] Monitoramento de saúde configurado (`/etc/cron.daily/safetyscorebrasil-health`)
- [ ] Logs sendo rotacionados corretamente
- [ ] CloudWatch configurado (opcional)

### 📝 Documentação

- [ ] Credenciais salvas em local seguro
- [ ] IP da EC2 anotado
- [ ] Endpoint do RDS anotado
- [ ] Informações de acesso ao admin anotadas
- [ ] Processo de atualização documentado

### 🎯 Pós-Deploy

- [ ] Testar funcionalidades principais do site
- [ ] Verificar performance (tempo de carregamento)
- [ ] Verificar logs por 24h após deploy
- [ ] Configurar alertas de monitoramento
- [ ] Documentar procedimentos de rollback (se necessário)

---

## 🚨 Problemas Comuns

Se algo não funcionar, verifique:

1. **502 Bad Gateway**
   - Verificar se Gunicorn está rodando: `sudo systemctl status safetyscorebrasil`
   - Verificar logs: `sudo journalctl -u safetyscorebrasil -f`

2. **Erro de banco de dados**
   - Verificar Security Group do RDS
   - Verificar `DATABASE_URL` no `.env`
   - Testar conexão: `psql -h endpoint -U admin -d projetoteste`

3. **SSL não funciona**
   - Verificar DNS apontando para EC2
   - Executar: `sudo certbot --nginx -d safetyscorebrasil.com.br -d www.safetyscorebrasil.com.br`

4. **Arquivos estáticos não carregam**
   - Executar: `python manage.py collectstatic --noinput`
   - Verificar permissões: `sudo chown -R django:www-data staticfiles/`

---

## ✅ Status Final

- [ ] **DEPLOY CONCLUÍDO COM SUCESSO**
- [ ] **SITE ACESSÍVEL EM PRODUÇÃO**
- [ ] **TODOS OS SERVIÇOS FUNCIONANDO**

**Data do Deploy:** _______________
**Realizado por:** _______________
**IP da EC2:** _______________
**Endpoint RDS:** _______________

---

**Última atualização:** Janeiro 2025

