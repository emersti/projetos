# Configuração para AWS EC2
# Instruções para deploy no AWS

## 1. Configuração da Instância EC2

### Tipo de Instância Recomendado:
- **t3.medium** ou **t3.large** para produção
- **t3.micro** para testes (gratuito por 12 meses)

### Configuração de Segurança:
- Porta 22 (SSH)
- Porta 80 (HTTP)
- Porta 443 (HTTPS)

### Sistema Operacional:
- Ubuntu 22.04 LTS

## 2. Configuração do Banco de Dados

### Opção 1: RDS PostgreSQL (Recomendado)
```bash
# Criar instância RDS PostgreSQL
# Configurar security group para permitir acesso da EC2
# Usar endpoint do RDS no arquivo .env
```

### Opção 2: PostgreSQL na EC2
```bash
# Instalar PostgreSQL diretamente na EC2
sudo apt install postgresql postgresql-contrib
```

## 3. Configuração de Storage

### Opção 1: S3 para arquivos estáticos
```bash
# Configurar bucket S3
# Usar django-storages para servir arquivos do S3
```

### Opção 2: EFS para arquivos de mídia
```bash
# Montar EFS na EC2
# Usar para arquivos de mídia compartilhados
```

## 4. Configuração de DNS

### Route 53:
- Criar hosted zone para safetyscorebrasil.com.br
- Configurar registros A apontando para IP da EC2
- Configurar registros CNAME para www

## 5. Configuração de SSL

### Certificado SSL:
- Usar AWS Certificate Manager (ACM)
- Configurar Application Load Balancer (ALB)
- Ou usar Let's Encrypt com Certbot

## 6. Configuração de Backup

### RDS:
- Backup automático habilitado
- Retention period: 7 dias

### EC2:
- Snapshot automático do volume EBS
- Backup dos arquivos de mídia para S3

## 7. Configuração de Monitoramento

### CloudWatch:
- Monitorar CPU, memória, disco
- Configurar alertas
- Logs da aplicação

## 8. Configuração de CDN

### CloudFront:
- Distribuição para arquivos estáticos
- Cache de 24 horas
- Compressão habilitada

## 9. Scripts de Deploy

### Deploy Automático:
```bash
# Usar GitHub Actions ou AWS CodeDeploy
# Deploy automático ao fazer push na branch main
```

### Deploy Manual:
```bash
# Executar script deploy.sh na EC2
sudo ./deploy.sh
```

## 10. Configuração de Ambiente

### Variáveis de Ambiente:
```bash
# Configurar no arquivo .env
DB_HOST=your-rds-endpoint.amazonaws.com
DB_NAME=safetyscore_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key
DEBUG=False
```

## 11. Configuração de Logs

### CloudWatch Logs:
- Enviar logs da aplicação para CloudWatch
- Configurar retention policy
- Configurar alertas para erros

## 12. Configuração de Segurança

### Security Groups:
- Apenas portas necessárias abertas
- Acesso SSH apenas do seu IP
- HTTPS obrigatório

### IAM:
- Usuário específico para a aplicação
- Permissões mínimas necessárias
- Rotação de chaves automática

## 13. Configuração de Performance

### Auto Scaling:
- Configurar Auto Scaling Group
- Escalar baseado em CPU/memória
- Load balancer para distribuir carga

### Cache:
- ElastiCache Redis para cache
- Configurar TTL adequado
- Monitorar hit rate

## 14. Configuração de Backup e Disaster Recovery

### Backup:
- Backup diário do banco de dados
- Snapshot semanal da EC2
- Backup dos arquivos para S3

### Disaster Recovery:
- Multi-AZ para RDS
- Backup em região diferente
- Plano de recuperação documentado
















