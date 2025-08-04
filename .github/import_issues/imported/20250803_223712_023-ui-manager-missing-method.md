# Bug: Silent period incorrectly filtering all events and 'UIManager' missing method error

## Descrição
1. O sistema está filtrando incorretamente TODOS os eventos quando um período de silêncio está ativo, mesmo quando os eventos não deveriam ser afetados.
2. Além disso, ocorre um erro no `UIManager` ao tentar chamar o método inexistente `show_warning` quando não há eventos restantes.

## Comportamento Atual
1. O script é executado com configurações que resultam na filtragem de todos os eventos (por exemplo, período de silêncio ativo que cobre toda a janela de busca)
2. O sistema tenta exibir um aviso sobre a ausência de eventos
3. Ocorre o erro: `'UIManager' object has no attribute 'show_warning'`

## Comportamento Esperado
1. O sistema deve aplicar corretamente os períodos de silêncio, filtrando APENAS os eventos que realmente se encaixam no período configurado
2. Se um evento ocorrer parcialmente durante um período de silêncio, apenas a parte sobreposta deve ser considerada
3. O sistema deve lidar graciosamente com a ausência de eventos após a filtragem
4. Exibir uma mensagem de aviso apropriada (se disponível no UIManager) ou usar o logger
5. Encerrar a execução sem erros

## Passos para Reproduzir
1. Configurar um período de silêncio que cubra toda a janela de busca de eventos
2. Executar o script com a flag `-v`
3. Observar o erro no final da execução

## Logs Relevantes
```
22:28:54 - WARNING - ⚠️  ⚠️ No events remaining after processing
22:28:54 - ERROR - ❌ Execution failed: 'UIManager' object has no attribute 'show_warning'
❌ Execution failed: 'UIManager' object has no attribute 'show_warning'
```

## Ambiente
- Branch: `feature/silent-period-ical-archiving`
- Commit: [inserir hash do commit]

## Prioridade
- [ ] Baixa
- [x] Média
- [ ] Alta
- [ ] Crítica

## Categorias
- [x] Bug
- [ ] Melhoria
- [ ] Nova Funcionalidade
- [ ] Documentação
- [ ] Outro

## Tarefas
- [ ] Investigar a lógica de filtragem de períodos de silêncio no `EventProcessor`
- [ ] Corrigir a lógica para garantir que apenas eventos que realmente ocorram DENTRO do período de silêncio sejam filtrados
- [ ] Melhorar o tratamento de eventos que se sobrepõem parcialmente ao período de silêncio
- [ ] Verificar a implementação do `UIManager` para identificar métodos disponíveis
- [ ] Atualizar a chamada para usar um método existente (provavelmente `log_warning` ou similar)
- [ ] Adicionar tratamento de erro para o caso de não haver eventos após a filtragem
- [ ] Adicionar testes unitários para os cenários de filtragem de períodos de silêncio
- [ ] Adicionar logs detalhados para depuração da filtragem de eventos

## Observações Adicionais
- O problema de filtragem incorreta pode estar relacionado à comparação de datas/horários ou à lógica de sobreposição de intervalos
- O erro do `UIManager` ocorre como um sintoma secundário quando todos os eventos são filtrados incorretamente
- A função de log de aviso parece estar tentando usar uma interface que não está implementada
- Verificar se o fuso horário está sendo tratado corretamente durante as comparações de datas
- Analisar se a lógica de filtragem está considerando corretamente eventos que começam antes do período de silêncio mas terminam durante ele, e vice-versa
