# Dockerfile para safetyscorebrasil.com.br - Produção
FROM python:3.11-slim

# Variáveis do ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=projeto_teste.settings_prod

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements-prod.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# Copiar código da aplicação
COPY . .

# Comando default (ajusta conforme seu stack)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projeto_teste.wsgi:application"]
