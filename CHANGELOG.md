# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-01-31

### 🚀 Adicionado
- **Módulo de Recursos Cloud Completo**
  - CRUD completo para recursos cloud (Create, Read, Update, Delete)
  - Suporte a 7 tipos de recursos AWS:
    - S3 (Buckets de armazenamento)
    - Load Balancer (Balanceadores de carga)
    - CloudFront (CDN)
    - API Gateway (Gateway de APIs)
    - EC2 (Instâncias de computação)
    - RDS (Bancos de dados)
    - Lambda (Funções serverless)
  - Formulários com validação específica por tipo de recurso
  - Sistema de busca e filtros avançados
  - Associação obrigatória com contas cloud
  - Teste de conectividade AWS via AJAX
  - Interface responsiva com Bootstrap 5

### 🎨 Melhorado
- **Dashboard Principal**
  - Adicionado card de estatísticas de recursos
  - Seção de recursos recentes
  - Resumo por tipo de recurso
  - Status dos recursos (Ativo, Inativo, Manutenção)
  - Ação rápida para criar novos recursos

- **Integração AWS**
  - Função `_get_resource_aws_info()` para obter informações específicas do recurso
  - Função `_test_resource_connectivity()` para teste de conectividade
  - Suporte a verificação de buckets S3
  - Informações detalhadas por tipo de serviço

### 🧪 Testes
- **25 novos testes** para o módulo de recursos
- Cobertura de testes aumentada de 84% para **87%**
- Total de testes: **67** (aumento de 42 para 67)
- Testes abrangentes cobrindo:
  - Modelos e propriedades
  - Formulários e validações
  - Views e CRUD operations
  - Integração AWS (com mocks)
  - Relacionamentos entre modelos

### 🔧 Técnico
- Migração `0002_add_account_status_descricao` para adicionar novos campos
- Propriedades `status_badge_class` e `tipo_icon` no modelo Resource
- URLs completas para todas as operações CRUD
- Templates responsivos com validação JavaScript em tempo real
- Integração com sistema de mensagens do Django

### 📊 Estatísticas
- **Módulos Implementados**: 4/5 (80%)
- **Cobertura de Testes**: 87%
- **Total de Testes**: 67
- **Linhas de Código**: 1.511 (201 não cobertas)

## [1.3.0] - 2025-01-30

### 🚀 Adicionado
- **Módulo de Contas Cloud Completo**
  - CRUD completo para contas AWS
  - Validação rigorosa de credenciais AWS
  - Teste de conectividade em tempo real
  - Integração com serviços AWS (EC2, S3, RDS)
  - Interface para visualização de informações da conta

### 🎨 Melhorado
- **Dashboard**
  - Card de estatísticas de contas cloud
  - Seção de contas recentes
  - Ações rápidas para criar nova conta

### 🧪 Testes
- 20 novos testes para contas cloud
- Cobertura mantida em 84%
- Mocks para serviços AWS

### 🔧 Técnico
- Formulários com validação AWS
- Templates responsivos
- Integração boto3

## [1.2.0] - 2025-01-29

### 🚀 Adicionado
- **Sistema de Busca Avançada para Certificados**
  - Filtros por requerente, número de série, emissor
  - Filtros por status e período de validade
  - Paginação inteligente
  - Preservação de filtros na navegação

### 🎨 Melhorado
- **Interface de Certificados**
  - Cards de estatísticas no topo da página
  - Indicadores visuais de status
  - Badges coloridos para diferentes estados
  - Layout responsivo aprimorado

### 🧪 Testes
- Testes para sistema de busca
- Validação de filtros
- Testes de paginação

## [1.1.0] - 2025-01-28

### 🚀 Adicionado
- **Módulo de Usuários Completo**
  - CRUD completo de usuários
  - Sistema de autenticação por email
  - Controle de status (Ativo/Inativo)
  - Busca e paginação

### 🎨 Melhorado
- **Dashboard**
  - Estatísticas de usuários
  - Usuários recentes
  - Ações rápidas

### 🧪 Testes
- 15 testes para módulo de usuários
- Cobertura de 82%

## [1.0.0] - 2025-01-27

### 🚀 Adicionado
- **Módulo de Certificados Completo**
  - CRUD completo de certificados digitais
  - Upload e validação de arquivos
  - Sistema de alertas para certificados expirando
  - Download seguro de certificados
  - Busca por múltiplos critérios

- **Dashboard Principal**
  - Estatísticas em tempo real
  - Certificados expirando em breve
  - Ações rápidas
  - Interface responsiva

- **Sistema Base**
  - Autenticação OAuth2
  - Templates Bootstrap 5
  - Sistema de mensagens
  - Estrutura modular

### 🧪 Testes
- 22 testes iniciais
- Cobertura de 82%
- Testes para modelos, views e forms

### 🔧 Técnico
- Django 4.2.16
- PostgreSQL
- Bootstrap 5
- Crispy Forms
- OAuth2 Provider

---

## Convenções do Changelog

### Tipos de Mudanças
- `🚀 Adicionado` - para novas funcionalidades
- `🎨 Melhorado` - para mudanças em funcionalidades existentes
- `🐛 Corrigido` - para correção de bugs
- `🔧 Técnico` - para mudanças técnicas/internas
- `🧪 Testes` - para adições/mudanças em testes
- `📊 Estatísticas` - para métricas do projeto
- `⚠️ Depreciado` - para funcionalidades que serão removidas
- `🗑️ Removido` - para funcionalidades removidas
- `🔒 Segurança` - para correções de segurança

### Formato de Versão
- **MAJOR.MINOR.PATCH** (ex: 1.2.3)
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades adicionadas de forma compatível
- **PATCH**: Correções de bugs compatíveis 