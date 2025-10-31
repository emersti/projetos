# 🚀 Resumo Rápido - Deploy em Produção
## SafeScore Brasil - safetyscorebrasil.com.br

### ⚡ Início Rápido

1. **Criar instâncias AWS:**
   - EC2 (Ubuntu 22.04, t3.small, 30GB)
   - RDS PostgreSQL (db.t3.micro, 20GB)
   - Security Groups configurados

2. **Conectar e fazer deploy:**
   ```bash
   ssh -i sua-chave.pem ubuntu@SEU-IP-EC2
   git clone seu-repo /var/www/safetyscorebrasil.com.br
   cd /var/www/safetyscorebrasil.com.br
   sudo chmod +x deploy.sh
   sudo ./deploy.sh
   ```

3. **Configurar .env:**
   ```bash
   sudo nano /var/www/safetyscorebrasil.com.br/.env
   # Configure SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS
   ```

4. **Executar migrações:**
   ```bash
   source venv/bin/activate
   python manage.py migrate --settings=projeto_teste.settings_prod
   python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod
   python manage.py importar_dados_criminalidade --file ResumoCriminalidadeCidades.xlsx
   ```

5. **Configurar DNS:**
   - Apontar `safetyscorebrasil.com.br` → IP da EC2
   - Configurar SSL: `sudo certbot --nginx -d safetyscorebrasil.com.br -d www.safetyscorebrasil.com.br`

### 📚 Documentação Completa

- **Guia Completo**: `DEPLOY_AWS_COMPLETO.md`
- **Checklist**: `CHECKLIST_DEPLOY.md`
- **Terraform**: `terraform/main.tf`
- **Scripts**: `deploy.sh`, `deploy_terraform.sh`

### 🔑 Arquivos Importantes

- **Configuração Produção**: `projeto_teste/settings_prod.py`
- **Variáveis Ambiente**: `env.production` (copiar para `.env` na EC2)
- **Nginx**: `nginx_config.conf`
- **Gunicorn**: `gunicorn_config.py`
- **Systemd**: `projeto_teste.service`

### 🛠️ Comandos Úteis

```bash
# Status dos serviços
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx

# Logs
sudo journalctl -u safetyscorebrasil -f
sudo tail -f /var/log/nginx/safetyscorebrasil_error.log

# Reiniciar
sudo systemctl restart safetyscorebrasil

# Atualizar
cd /var/www/safetyscorebrasil.com.br
git pull
source venv/bin/activate
pip install -r requirements-prod.txt
python manage.py migrate --settings=projeto_teste.settings_prod
python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod
sudo systemctl restart safetyscorebrasil
```

### 📞 Suporte

Em caso de problemas, consulte:
- `DEPLOY_AWS_COMPLETO.md` - Seção Troubleshooting
- `CHECKLIST_DEPLOY.md` - Verificações passo a passo

---

**Domínio**: safetyscorebrasil.com.br  
**Última Atualização**: Janeiro 2025


