---
name: "🐛 [CRÍTICO] Correção na Detecção da Página Alvo - Tomada de Tempo"
about: Correção crítica na detecção e processamento de eventos do site tomadadetempo.com.br
labels: 'bug, critical, enhancement, help wanted'
assignees: ''
---

## 🚨 Descrição do Problema

A detecção da página alvo no site tomadadetempo.com.br não está funcionando conforme o esperado, resultando em uma baixa taxa de coleta de eventos. Apenas 6 de 34 eventos estão sendo processados atualmente.

### Comportamento Atual
- O script está acessando a página principal, mas não está identificando corretamente o link para a programação detalhada
- Muitos eventos estão sendo perdidos durante o processo de extração
- Eventos sem data explícita não estão sendo associados corretamente ao contexto da página

### Comportamento Esperado
- O script deve identificar corretamente o link para a programação detalhada
- Todos os eventos relevantes devem ser capturados e processados
- Eventos sem data explícita devem ser associados ao contexto correto da página

## 🔍 Análise Inicial

### Problemas Identificados
1. **Falha na Detecção do Link Alvo**
   - O script não está encontrando corretamente o link para a página de programação
   - A estrutura do site pode ter sido alterada recentemente

2. **Processamento Incompleto de Eventos**
   - Apenas eventos com datas explícitas estão sendo processados
   - Muitos eventos importantes estão sendo ignorados
   - Exemplo de eventos perdidos: "16:30 – NASCAR CUP", "19:00 – FÓRMULA 1"

3. **Filtro de Fim de Semana**
   - O filtro está eliminando eventos válidos
   - A associação de eventos sem data ao contexto da página não está funcionando corretamente

## 🎯 Tarefas

### 1. Correção da Detecção da Página Alvo
- [ ] Identificar o seletor CSS/XPATH correto para o link da programação
- [ ] Implementar lógica de fallback caso o link principal mude
- [ ] Adicionar validação para garantir que a página correta foi carregada

### 2. Melhoria no Processamento de Eventos
- [ ] Corrigir a extração de eventos sem data explícita
- [ ] Melhorar a associação de eventos ao contexto da página
- [ ] Implementar tratamento especial para eventos da programação semanal

### 3. Aprimoramento da Resiliência
- [ ] Adicionar logs detalhados para facilitar o diagnóstico
- [ ] Implementar tratamento de erros mais robusto
- [ ] Adicionar testes automatizados para evitar regressões

## 📊 Dados para Análise

### Eventos que estão sendo capturados atualmente:
- F1: "entre os dias 01 e"
- StockCar: "SEXTA"
- F2: "SÁBADO – 02/08/2025", "DOMINGO – 03/08/2025", "02/08/2025", "03/08/2025"

### Exemplos de eventos que estão sendo perdidos:
- "16:30 – NASCAR CUP"
- "19:00 – FÓRMULA 1"
- Tags simples como "F1", "F2", "F3", "nascar"

## 🔧 Ambiente
- **Versão do Script**: [Inserir versão]
- **Python**: 3.8+
- **Sistema Operacional**: [Inserir SO]
- **Navegador/Driver**: [Inserir versão do navegador/driver]

## 📝 Notas Adicionais
- Esta é uma correção crítica que afeta diretamente a funcionalidade principal do sistema
- A solução deve ser compatível com as versões futuras do site
- Documentar todas as alterações realizadas

## ✅ Critérios de Aceitação
- [ ] Todas as tarefas da lista acima foram concluídas
- [ ] Pelo menos 90% dos eventos estão sendo capturados corretamente
- [ ] Os logs mostram o processo de detecção e extração funcionando corretamente
- [ ] Os testes automatizados foram atualizados e estão passando
- [ ] A documentação foi atualizada com as alterações realizadas
