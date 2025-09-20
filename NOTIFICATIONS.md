# DividaFacil - Sistema de Notificações para Parcelas

Este documento descreve o sistema de notificações implementado no DividaFacil para lembrar usuários sobre parcelas de pagamentos pendentes.

## Funcionalidades Implementadas

### 1. Notificações de Parcelas em Atraso
- ✅ Detecção automática de parcelas vencidas
- ✅ Agrupamento por usuário para envio de notificações consolidadas
- ✅ Respeito às preferências de notificação de cada usuário
- ✅ Fallback para console quando email não está configurado

### 2. Notificações de Parcelas Próximas ao Vencimento
- ✅ Configuração de quantos dias antes notificar (padrão: 3 dias)
- ✅ Personalização por usuário do período de antecedência
- ✅ Filtragem baseada nas preferências do usuário

### 3. Preferências de Notificação por Usuário
- ✅ `email_overdue`: Ativa/desativa notificações de parcelas em atraso
- ✅ `email_upcoming`: Ativa/desativa notificações de parcelas próximas
- ✅ `days_ahead_reminder`: Quantos dias antes do vencimento notificar

### 4. Interface de Linha de Comando
- ✅ Script `notifications.py` com comandos para gerenciar notificações
- ✅ Relatórios detalhados de parcelas pendentes
- ✅ Teste de configuração de email
- ✅ Modo de apenas relatório (sem envio de emails)

## Como Usar

### Configuração de Email (Opcional)

Para enviar emails reais, configure as variáveis de ambiente:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="seu-email@gmail.com"
export SMTP_PASSWORD="sua-senha-de-app"
```

### Comandos Disponíveis

#### 1. Verificar Parcelas em Atraso

```bash
# Apenas relatório (sem envio de emails)
python notifications.py overdue --report-only

# Enviar notificações para parcelas em atraso
python notifications.py overdue

# Relatório detalhado após envio
python notifications.py overdue --verbose
```

#### 2. Verificar Parcelas Próximas ao Vencimento

```bash
# Verificar parcelas dos próximos 3 dias (padrão)
python notifications.py upcoming --report-only

# Verificar parcelas dos próximos 7 dias
python notifications.py upcoming --days 7 --report-only

# Enviar notificações para parcelas próximas
python notifications.py upcoming --days 5
```

#### 3. Testar Configuração de Email

```bash
python notifications.py test-email usuario@exemplo.com
```

### Exemplo de Saída

#### Parcelas em Atraso
```
⚠️  Encontradas 2 parcelas em atraso:

👤 Bob Santos (bob@example.com):
   • Conta de Internet - Casa Compartilhada
     Parcela 1: R$ 200.00
     Vencimento: 15/09/2025 (5 dias atraso)

👤 Carol Oliveira (carol@example.com):
   • Conta de Internet - Casa Compartilhada
     Parcela 1: R$ 200.00
     Vencimento: 15/09/2025 (5 dias atraso)
```

#### Notificação por Email/Console
```
📬 Console notification for Bob Santos (bob@example.com):
Subject: DividaFacil - Parcelas em atraso (1 pendente)
---
Olá Bob Santos,

Você possui parcelas em atraso no DividaFacil:

• Conta de Internet - Grupo: Casa Compartilhada
  Parcela 1 de R$ 200.00
  Vencimento: 15/09/2025
  5 dias em atraso

Por favor, acesse o sistema para efetuar o pagamento.

Atenciosamente,
Equipe DividaFacil
==================================================
```

## Arquitetura do Sistema

### Componentes Principais

1. **NotificationService** (`src/services/notification_service.py`)
   - Lógica principal de detecção e envio de notificações
   - Geração de conteúdo para emails/mensagens
   - Respeito às preferências dos usuários

2. **User Model** (`src/models/user.py`)
   - Adição de campo `notification_preferences`
   - Configurações padrão para novos usuários

3. **Database Schema** (`src/database.py`)
   - Persistência das preferências de notificação
   - Suporte para configurações JSON no banco

4. **CLI Tool** (`notifications.py`)
   - Interface de linha de comando para operações
   - Automatização de tarefas de notificação

### Integração com Funcionalidades Existentes

- ✅ **Compatível** com sistema de parcelas existente
- ✅ **Integrado** com cálculo de saldos em tempo real
- ✅ **Mantém** toda funcionalidade anterior do aplicativo
- ✅ **Estende** sem quebrar APIs existentes

## Agendamento de Notificações

Para uso em produção, você pode agendar as notificações usando cron:

```bash
# Verificar parcelas em atraso todos os dias às 9h
0 9 * * * cd /path/to/dividafacil && python notifications.py overdue

# Verificar parcelas próximas todos os dias às 8h
0 8 * * * cd /path/to/dividafacil && python notifications.py upcoming --days 3
```

## Desenvolvimento e Testes

### Criar Dados de Teste

```bash
python create_test_data.py
```

### Executar Testes

```bash
python -m pytest tests/ -v
```

### Visualizar Interface Web

```bash
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000
```

## Próximos Passos

Para expansão futura do sistema:

1. **Interface Web para Preferências**: Permitir usuários configurar notificações pela web
2. **Notificações Push**: Integração com serviços de push notifications
3. **Templates Personalizáveis**: Permitir personalização dos textos das notificações
4. **Múltiplos Canais**: SMS, WhatsApp, etc.
5. **Dashboard de Notificações**: Visualização de histórico de notificações enviadas

## Suporte

Para problemas ou dúvidas sobre o sistema de notificações:

1. Verifique os logs de console para mensagens de erro
2. Teste a configuração de email com `notifications.py test-email`
3. Use o modo `--report-only` para verificar dados sem enviar notificações
4. Confira se as preferências dos usuários estão configuradas corretamente