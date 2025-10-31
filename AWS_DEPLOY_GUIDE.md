# Guia Completo de Deploy na AWS

## Pré-requisitos
- Conta AWS ativa
- AWS CLI configurado
- Terraform instalado (opcional, para infraestrutura como código)

## Opção 1: Deploy Manual (Recomendado para iniciantes)

### 1. Criar Instância EC2
1. Acesse o AWS Console
2. Vá para EC2 > Instâncias > Lançar instância
3. Escolha Ubuntu Server 22.04 LTS
4. Tipo de instância: t3.micro (elegível para tier gratuito)
5. Configure Security Group:
   - SSH (22): Sua IP
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
6. Crie um par de chaves para SSH

### 2. Configurar Banco de Dados RDS
1. Vá para RDS > Bancos de dados > Criar banco de dados
2. Escolha PostgreSQL
3. Template: Desenvolvimento/teste
4. Configurações:
   - Identificador: projeto-teste-db
   - Usuário mestre: admin
   - Senha: [senha segura]
   - Tipo de instância: db.t3.micro
5. Configure Security Group para permitir acesso da EC2

### 3. Conectar à EC2
```bash
ssh -i sua-chave.pem ubuntu@seu-ip-ec2
```

### 4. Executar Deploy
```bash
# Upload dos arquivos do projeto
scp -r -i sua-chave.pem . ubuntu@seu-ip-ec2:/home/ubuntu/

# Na EC2, executar:
sudo chmod +x deploy.sh
./deploy.sh
```

### 5. Configurar Nginx e Gunicorn
```bash
# Copiar configuração do Nginx
sudo cp nginx_config.conf /etc/nginx/sites-available/projeto_teste
sudo ln -s /etc/nginx/sites-available/projeto_teste /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Copiar serviço do Gunicorn
sudo cp projeto_teste.service /etc/systemd/system/

# Iniciar serviços
sudo systemctl daemon-reload
sudo systemctl start projeto_teste
sudo systemctl enable projeto_teste
sudo systemctl restart nginx
```

### 6. Configurar Variáveis de Ambiente
```bash
sudo nano /var/www/projeto_teste/.env
```

Configure com suas credenciais:
- SECRET_KEY: Gere uma nova chave
- DATABASE_URL: URL do seu RDS
- ALLOWED_HOSTS: Seu domínio/IP

## Opção 2: Deploy com Terraform (Avançado)

### Arquivo terraform/main.tf
```hcl
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# Subnet pública
resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

# Security Group para EC2
resource "aws_security_group" "ec2" {
  name_prefix = "projeto-teste-ec2"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group para RDS
resource "aws_security_group" "rds" {
  name_prefix = "projeto-teste-rds"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }
}

# Instância EC2
resource "aws_instance" "app" {
  ami           = "ami-0c02fb55956c7d316"  # Ubuntu 22.04 LTS
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  security_groups = [aws_security_group.ec2.id]

  user_data = file("user_data.sh")

  tags = {
    Name = "projeto-teste-app"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier = "projeto-teste-db"
  engine     = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_type = "gp2"

  db_name  = "projetoteste"
  username = "admin"
  password = "sua-senha-segura"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
}

resource "aws_db_subnet_group" "main" {
  name       = "projeto-teste-subnet-group"
  subnet_ids = [aws_subnet.public.id]

  tags = {
    Name = "Projeto Teste DB subnet group"
  }
}
```

## Configuração de Domínio (Opcional)

### 1. Registrar Domínio
- Use Route 53 ou outro provedor
- Configure DNS para apontar para seu IP da EC2

### 2. SSL com Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

## Monitoramento e Logs

### CloudWatch
- Configure logs do Django no CloudWatch
- Monitore métricas da EC2 e RDS

### Backup
- Configure backup automático do RDS
- Backup dos arquivos estáticos no S3

## Custos Estimados (Tier Gratuito)
- EC2 t3.micro: Gratuito por 12 meses
- RDS db.t3.micro: Gratuito por 12 meses
- Armazenamento: 30GB gratuito
- Transferência: 1GB/mês gratuito

## Próximos Passos
1. Configure CI/CD com GitHub Actions
2. Implemente CDN com CloudFront
3. Configure auto-scaling
4. Implemente monitoramento avançado







































