# Sistema de Controle de Atualização de Páginas

## Visão Geral

Este sistema permite controlar individualmente a data de última atualização de páginas específicas do site, independente da data geral do sistema.

## Como Usar

### 1. Atualizar Data de uma Página

Use o comando de management:

```bash
python manage.py atualizar_pagina [nome_da_pagina] --descricao "Descrição da atualização"
```

**Exemplos:**
```bash
# Atualizar página LGPD
python manage.py atualizar_pagina lgpd --descricao "Atualização da política de privacidade"

# Atualizar página FAQ
python manage.py atualizar_pagina faq --descricao "Adição de novas perguntas frequentes"

# Atualizar página Sobre
python manage.py atualizar_pagina sobre --descricao "Atualização das informações da empresa"
```

### 2. Usar nos Templates

Carregue o template tag e use a função:

```html
{% load consulta_risco_tags %}

<p class="last-update">
    <strong>Última atualização:</strong> {% get_ultima_atualizacao_pagina 'lgpd' %}
</p>
```

### 3. Páginas Disponíveis

- `lgpd` - Página de Política de Privacidade
- `faq` - Página de Perguntas Frequentes
- `sobre` - Página Sobre a Empresa
- `cupons` - Página de Cupons
- `home` - Página Inicial

## Funcionalidades

### Template Tags Disponíveis

1. **`get_ultima_atualizacao()`**
   - Retorna a data geral do sistema
   - Usado no footer global

2. **`get_ultima_atualizacao_pagina(nome_pagina)`**
   - Retorna a data específica de uma página
   - Formato: "09 de outubro de 2025"
   - Fuso horário: Brasília/Brasil

### Modelos

1. **`SistemaAtualizacao`**
   - Controla a data geral do sistema
   - Usado para o footer global

2. **`PaginaAtualizacao`**
   - Controla datas específicas de páginas
   - Campos: nome_pagina, data_atualizacao, descricao

## Exemplos de Uso

### Atualizar LGPD após mudanças na política
```bash
python manage.py atualizar_pagina lgpd --descricao "Revisão da política conforme nova legislação"
```

### Atualizar FAQ com novas perguntas
```bash
python manage.py atualizar_pagina faq --descricao "Adição de 5 novas perguntas frequentes"
```

### Atualizar página Sobre com novas informações
```bash
python manage.py atualizar_pagina sobre --descricao "Atualização do histórico da empresa"
```

## Formato de Data

- **Template tag geral**: `09/10/2025 às 18:56`
- **Template tag página**: `09 de outubro de 2025`
- **Fuso horário**: Brasília/Brasil (UTC-3)
- **Idioma**: Português brasileiro



















