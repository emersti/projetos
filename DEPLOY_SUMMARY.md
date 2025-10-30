# Resumo das Configurações de Deploy

## ✅ Preparações Concluídas

### 1. Configurações Django
- ✅ `settings_prod.py` atualizado para safetyscorebrasil.com.br
- ✅ `requirements-prod.txt` com dependências de produção
- ✅ Configurações de segurança habilitadas

### 2. Infraestrutura AWS (Terraform)
- ✅ `main.tf` configurado para safetyscorebrasil.com.br
- ✅ Route 53 para gerenciamento DNS
- ✅ Certificado SSL automático (ACM)
- ✅ EC2, RDS, Security Groups configurados
- ✅ `terraform.tfvars.example` atualizado

### 3. Servidor Web (Nginx)
- ✅ `nginx_config.conf` com HTTPS e segurança
- ✅ Redirecionamento HTTP → HTTPS
- ✅ Headers de segurança configurados
- ✅ Configuração para arquivos estáticos

### 4. Serviços Systemd
- ✅ `projeto_teste.service` atualizado
- ✅ Configuração para Gunicorn
- ✅ Auto-restart em caso de falha

### 5. Scripts de Deploy
- ✅ `deploy.sh` - Deploy completo automatizado
- ✅ `deploy_terraform.sh` - Deploy com Terraform
- ✅ Scripts de inicialização da EC2

### 6. Variáveis de Ambiente
- ✅ `env_example.txt` atualizado
- ✅ `env.production.example` criado
- ✅ Configurações para produção

### 7. Documentação
- ✅ `DEPLOY_GUIDE.md` - Guia completo de deploy
- ✅ `README.md` atualizado
- ✅ `SISTEMA_ATUALIZACAO_PAGINAS.md` - Sistema de páginas

## 🚀 Como Fazer o Deploy

### Pré-requisitos
1. Conta AWS configurada
2. AWS CLI instalado e configurado
3. Terraform instalado
4. Domínio safetyscorebrasil.com.br no registro.br

### Passos
1. **Configurar Terraform**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Editar terraform.tfvars com suas configurações
   ```

2. **Executar Deploy**:
   ```bash
   chmod +x deploy_terraform.sh
   ./deploy_terraform.sh
   ```

3. **Configurar Domínio**:
   - Acessar painel do registro.br
   - Alterar nameservers para os fornecidos pelo Terraform
   - Aguardar propagação DNS (até 48h)

## 📋 Checklist Final

### Antes do Deploy
- [ ] AWS CLI configurado
- [ ] Terraform instalado
- [ ] Chave SSH configurada
- [ ] terraform.tfvars configurado
- [ ] Senha do banco definida

### Após o Deploy
- [ ] Site acessível via HTTPS
- [ ] Certificado SSL funcionando
- [ ] Painel admin acessível
- [ ] Banco de dados conectado
- [ ] Arquivos estáticos servidos
- [ ] Logs funcionando

### Configurações de Segurança
- [ ] HTTPS habilitado
- [ ] Headers de segurança
- [ ] Firewall configurado
- [ ] Senhas fortes
- [ ] Backups automáticos

## 🔧 Comandos Úteis

### Verificar Status
```bash
# Status dos serviços
sudo systemctl status safetyscorebrasil
sudo systemctl status nginx

# Logs
sudo journalctl -u safetyscorebrasil -f
sudo tail -f /var/log/nginx/safetyscorebrasil_error.log
```

### Manutenção
```bash
# Atualizar aplicação
cd /var/www/safetyscorebrasil
git pull
source venv/bin/activate
pip install -r requirements-prod.txt
python manage.py migrate --settings=projeto_teste.settings_prod
python manage.py collectstatic --noinput --settings=projeto_teste.settings_prod
sudo systemctl restart safetyscorebrasil
```

### Backup
```bash
# Backup do banco
pg_dump -h seu-rds-endpoint -U admin projetoteste > backup.sql

# Backup dos arquivos
tar -czf backup_files.tar.gz /var/www/safetyscorebrasil/
```

## 📞 Suporte

- **Email**: atendimento@safetyscorebrasil.com.br
- **Assunto**: Suporte Técnico

---

**Data**: 09 de outubro de 2025
**Status**: Pronto para deploy


















