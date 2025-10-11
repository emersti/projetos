# Safety Score Brasil - Consulta de Risco de Trajeto

Um sistema web desenvolvido em Django para consultar o risco de segurança de trajetos entre cidades brasileiras.

**🌐 Site**: [safetyscorebrasil.com.br](https://safetyscorebrasil.com.br)

## 🎨 Design

O site utiliza as cores principais:
- **Laranja** (#FF6B35) - Para elementos de destaque e botões
- **Azul Escuro** (#1A365D) - Para títulos e elementos principais
- **Cinza** (#718096) - Para textos secundários e elementos neutros

## 🚀 Funcionalidades

- Interface responsiva e moderna
- Seleção de estado e cidade de origem
- Seleção de estado e cidade de destino
- Consulta simulada de risco de trajeto
- Resultados com recomendações de segurança
- Design responsivo para mobile e desktop
- Sistema de cupons de desconto
- Painel administrativo completo
- Páginas institucionais (Sobre, FAQ, LGPD)

## 🌐 Deploy em Produção

### Deploy Automático na AWS
```bash
# Configurar AWS CLI
aws configure

# Executar deploy automático
chmod +x deploy_terraform.sh
./deploy_terraform.sh
```

### Infraestrutura AWS
- **EC2**: Instância Ubuntu 22.04
- **RDS**: Banco PostgreSQL
- **Route 53**: Gerenciamento DNS
- **ACM**: Certificado SSL
- **Nginx**: Servidor web

### Domínio
- **Principal**: safetyscorebrasil.com.br
- **WWW**: www.safetyscorebrasil.com.br
- **SSL**: Certificado Let's Encrypt automático

📖 **Documentação completa**: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

1. **Clone ou baixe o projeto**
   ```bash
   cd projeto_teste
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # No Windows:
   venv\Scripts\activate
   
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute as migrações do banco de dados**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Popule o banco com dados de exemplo**
   ```bash
   python manage.py popular_cidades
   ```

6. **Importe os dados de criminalidade (opcional)**
   ```bash
   python manage.py importar_dados_criminalidade
   ```

7. **Execute o servidor de desenvolvimento**
   ```bash
   python manage.py runserver
   ```

8. **Acesse o site**
   Abra seu navegador e acesse: http://127.0.0.1:8000

## 📁 Estrutura do Projeto

```
projeto_teste/
├── manage.py
├── requirements.txt
├── README.md
├── projeto_teste/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── consulta_risco/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── popular_cidades.py
├── templates/
│   ├── base.html
│   └── consulta_risco/
│       └── home.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🎯 Como Usar

1. **Acesse a página principal**
   - O título "Consulte o risco de seu trajeto" estará em destaque

2. **Selecione a origem**
   - Escolha o estado de origem no primeiro dropdown
   - Selecione a cidade de origem no segundo dropdown

3. **Selecione o destino**
   - Escolha o estado de destino no terceiro dropdown
   - Selecione a cidade de destino no quarto dropdown

4. **Consulte o risco**
   - Clique no botão "Consultar Risco"
   - Aguarde o resultado da consulta
   - Visualize o nível de risco e as recomendações

## 🔧 Comandos Úteis

- **Criar superusuário (admin)**
  ```bash
  python manage.py createsuperuser
  ```

- **Acessar painel admin**
  http://127.0.0.1:8000/admin

- **Executar testes**
  ```bash
  python manage.py test
  ```

- **Controle de Manutenção**
  ```bash
  # Verificar status do modo de manutenção
  python manage.py toggle_maintenance --status
  
  # Ativar modo de manutenção
  python manage.py toggle_maintenance --on
  
  # Desativar modo de manutenção
  python manage.py toggle_maintenance --off
  
  # Alternar modo de manutenção (on/off)
  python manage.py toggle_maintenance
  ```

## 📱 Responsividade

O site é totalmente responsivo e funciona bem em:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (até 767px)

## 🎨 Tecnologias Utilizadas

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: SQLite (desenvolvimento)
- **Design**: CSS Grid, Flexbox, Gradientes
- **Fontes**: Google Fonts (Inter)

## 🚧 Modo de Manutenção

O sistema inclui uma funcionalidade de modo de manutenção que permite exibir uma página de aviso quando o sistema estiver instável.

### Como usar:

1. **Ativar modo de manutenção:**
   ```bash
   python manage.py toggle_maintenance --on
   ```

2. **Desativar modo de manutenção:**
   ```bash
   python manage.py toggle_maintenance --off
   ```

3. **Verificar status:**
   ```bash
   python manage.py toggle_maintenance --status
   ```

### Página de Manutenção:
- **URL**: http://127.0.0.1:8000/maintenance/
- **Mensagem**: "Estamos enfrentando instabilidade. Em breve retornaremos"
- **Design**: Consistente com o tema do site (laranja, azul escuro, cinza)
- **Funcionalidades**: Botão "Tentar Novamente" e informações de contato

## 📝 Notas Importantes

- Este é um sistema de demonstração com dados simulados
- Os níveis de risco são gerados aleatoriamente
- Em um sistema real, os dados seriam baseados em informações atualizadas de segurança
- O banco de dados inclui todos os estados brasileiros e suas principais cidades
- O modo de manutenção pode ser ativado/desativado facilmente via comando

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.





