## 🚀 Descrição da Feature
Implementar um sistema de "período de silêncio" que permita configurar intervalos de tempo durante os quais os eventos não serão incluídos no arquivo iCal de saída, mas ainda serão exibidos nos logs e na saída do terminal para fins de monitoramento.

## 📌 Objetivo
Permitir que os usuários configurem períodos específicos (por exemplo, durante a noite ou finais de semana) onde eventos de calendário não devem ser incluídos no arquivo iCal final, mas ainda assim sejam visíveis nos logs para fins de auditoria e monitoramento.

## 💡 Solução Proposta
1. **Configuração no arquivo de configuração**:
   ```json
   "silent_periods": [
     {
       "enabled": true,
       "name": "Noite",
       "start_time": "22:00",
       "end_time": "06:00",
       "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "sunday"]
     },
     {
       "enabled": true,
       "name": "Fim de Semana",
       "start_time": "00:00",
       "end_time": "23:59",
       "days_of_week": ["saturday", "sunday"]
     }
   ]
   ```

2. **Comportamento esperado**:
   - Eventos que ocorrem durante os períodos de silêncio configurados são filtrados do arquivo iCal final
   - Os eventos filtrados são registrados nos logs com nível INFO
   - Um resumo dos eventos filtrados é exibido na saída do terminal
   - O sistema deve lidar corretamente com períodos que cruzam a meia-noite

## 🔄 Alternativas Consideradas
1. **Filtragem pós-processamento**: Processar todos os eventos e depois filtrar os que estão no período de silêncio
   - **Vantagem**: Mais simples de implementar
   - **Desvantagem**: Menos eficiente para grandes volumes de eventos

2. **Filtragem durante o processamento**: Filtrar eventos durante o processamento inicial
   - **Vantagem**: Mais eficiente
   - **Desvantagem**: Pode ser mais complexo de implementar

## 📊 Impacto Esperado
- **Usuários finais**: Maior controle sobre quais eventos aparecem em seus calendários
- **Desenvolvedores**: Melhor visibilidade de eventos que foram filtrados
- **Sistema**: Leve aumento no uso de recursos para verificação dos períodos de silêncio

## 📝 Plano de Trabalho

### 1. Análise e Planejamento
- [ ] Analisar o código atual de processamento de eventos
- [ ] Definir a estrutura de dados para os períodos de silêncio
- [ ] Documentar o formato de configuração

### 2. Implementação
- [ ] Criar classe `SilentPeriod` para gerenciar os períodos
- [ ] Implementar lógica de verificação se um evento está em um período de silêncio
- [ ] Modificar o processador de eventos para filtrar eventos em períodos de silêncio
- [ ] Adicionar logs detalhados para eventos filtrados

### 3. Testes
- [ ] Criar testes unitários para a nova funcionalidade
- [ ] Testar com diferentes configurações de período de silêncio
- [ ] Verificar o comportamento com fusos horários diferentes
- [ ] Testar com períodos que cruzam a meia-noite

### 4. Documentação
- [ ] Atualizar README.md com a nova funcionalidade
- [ ] Adicionar exemplos de configuração
- [ ] Documentar como visualizar eventos filtrados nos logs

### 5. Implantação
- [ ] Atualizar CHANGELOG.md
- [ ] Atualizar RELEASES.md
- [ ] Criar pull request

## 🔗 Links Relacionados
- [Issue #20 - Links de transmissão não estão sendo incluídos nos eventos iCal](#20)

## 📱 Contexto Adicional
Esta funcionalidade é especialmente útil para usuários que desejam evitar notificações de eventos durante horários específicos, mas ainda assim desejam manter o histórico desses eventos para referência futura.
