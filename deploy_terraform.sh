#!/bin/bash

# Script para deploy automático usando Terraform
# Execute este script na sua máquina local

echo "=== Deploy Automático na AWS com Terraform ==="
echo "Domínio: safetyscorebrasil.com.br"

# Verificar se Terraform está instalado
if ! command -v terraform &> /dev/null; then
    echo "Terraform não está instalado. Instalando..."
    # Instalar Terraform (Ubuntu/Debian)
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform
fi

# Verificar se AWS CLI está configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo "AWS CLI não está configurado. Configure com: aws configure"
    exit 1
fi

# Navegar para diretório terraform
cd terraform

# Copiar arquivo de variáveis se não existir
if [ ! -f terraform.tfvars ]; then
    echo "Copiando arquivo de variáveis..."
    cp terraform.tfvars.example terraform.tfvars
    echo "Configure o arquivo terraform.tfvars com suas credenciais"
    echo "Especialmente a senha do banco de dados!"
    exit 1
fi

# Inicializar Terraform
echo "Inicializando Terraform..."
terraform init

# Planejar infraestrutura
echo "Planejando infraestrutura..."
terraform plan

# Aplicar infraestrutura
echo "Aplicando infraestrutura..."
read -p "Deseja continuar com o deploy? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply -auto-approve
    
    # Obter outputs
    echo "=== Informações do Deploy ==="
    echo "IP da EC2: $(terraform output -raw ec2_public_ip)"
    echo "Domínio: $(terraform output -raw domain_name)"
    echo "Nameservers: $(terraform output -json nameservers)"
    
    # Aguardar instância estar pronta
    echo "Aguardando instância estar pronta..."
    sleep 60
    
    # Fazer deploy da aplicação
    EC2_IP=$(terraform output -raw ec2_public_ip)
    DOMAIN=$(terraform output -raw domain_name)
    
    echo "Fazendo deploy da aplicação..."
    scp -r -o StrictHostKeyChecking=no ../* ubuntu@$EC2_IP:/home/ubuntu/
    ssh -o StrictHostKeyChecking=no ubuntu@$EC2_IP "sudo chmod +x deploy.sh && sudo ./deploy.sh"
    
    echo "=== Deploy Concluído ==="
    echo "Acesse sua aplicação em: https://$DOMAIN"
    echo "Admin: https://$DOMAIN/painel/login/"
    echo "Usuário: admin"
    echo "Senha: admin123"
    echo ""
    echo "IMPORTANTE: Configure os nameservers do domínio no registro.br:"
    terraform output -json nameservers | jq -r '.[]'
else
    echo "Deploy cancelado"
fi




















