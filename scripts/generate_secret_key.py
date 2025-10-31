#!/usr/bin/env python3
"""
Script para gerar SECRET_KEY do Django para produção
Execute: python scripts/generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("SECRET_KEY gerada para produção:")
    print("="*70)
    print(secret_key)
    print("="*70)
    print("\nCopie este valor para o arquivo .env na instância EC2")
    print("Arquivo: /var/www/safetyscorebrasil.com.br/.env")
    print("\n")


