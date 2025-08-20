# Fontes de Dados - Eventos de Automobilismo

> Nota pós-rollback (0.5.1)
>
> A branch `main` foi revertida para o snapshot do commit `9362503` (PR #34). Algumas referências a integrações futuras (ex.: OpenF1) podem ainda não estar disponíveis nesta versão. Consulte `RELEASES.md` para detalhes.

## **Visão Geral das Fontes de Dados**

### **Objetivo**
Documentar as fontes de dados atualmente integradas ao sistema, incluindo detalhes de implementação, limitações conhecidas e planos futuros de integração.

---

## **📊 Fontes de Dados Implementadas**

### **1. Tomada de Tempo (Fonte Primária)**
- **URL**: https://www.tomadadetempo.com.br/
- **Tipo**: Web scraping
- **Dados Coletados**:
  - Programação de TV e internet
  - Horários de transmissão
  - Categorias de automobilismo
  - Links para transmissões
- **Status**: ✅ Ativa e estável
- **Cobertura**: Excelente para categorias brasileiras e internacionais
- **Frequência de Atualização**: Diária
- **Limitações Conhecidas**:
  - Necessidade de tratamento especial para datas em português
  - Formato de programação pode variar
- **Exemplo de Uso**:
  ```python
  from sources.tomada_tempo import TomadaTempoSource
  source = TomadaTempoSource()
  events = source.fetch_events()
  ```

### **2. Ergast API (F1)**
- **URL**: http://ergast.com/mrd/
- **Tipo**: API REST
- **Dados Coletados**:
  - Calendário da F1
  - Resultados históricos
  - Horários de sessões
- **Status**: ⚠️ Ativa (mas será descontinuada em 2024)
- **Formato**: JSON/XML
- **Limitações**:
  - Dados podem ter atraso de atualização
  - API será descontinuada
- **Plano de Migração**: Transição para OpenF1 API em andamento

### **3. OpenF1 API (Futura Fonte Principal para F1)**
- **URL**: https://openf1.org/
- **Tipo**: API REST
- **Status**: 🔄 Em implementação
- **Vantagens**:
  - Dados em tempo real
  - Comunidade ativa
  - Alternativa moderna ao Ergast
- **Plano**: Tornar-se a fonte primária para dados de F1

## **📡 Provedores de Streaming**

### **Brasil**
- **Globo/SporTV**: Cobertura de F1, Stock Car, Fórmula E
- **Bandeirantes**: MotoGP, WSBK
- **ESPN**: NASCAR, IndyCar
- **F1 TV Pro**: Transmissão oficial da F1 (assinatura)

### **Internacional**
- **F1 TV Pro**: Cobertura completa da F1
- **MotoGP VideoPass**: Transmissões oficiais de MotoGP
- **Motorsport.tv**: Diversas categorias
- **YouTube**: Canais oficiais das categorias

---

## **🔄 Fontes em Desenvolvimento**

### **1. MotoGP Official**
- **URL**: https://www.motogp.com/
- **Tipo**: Web scraping/API não oficial
- **Status**: 🔄 Em desenvolvimento
- **Recursos Planejados**:
  - Calendário completo
  - Horários de sessões
  - Classificações

### **2. Motorsport.com**
- **URL**: https://www.motorsport.com/
- **Tipo**: Web scraping
- **Status**: 🔄 Em desenvolvimento
- **Objetivo**: Complementar dados de categorias menos cobertas

---

## **📅 Estrutura dos Dados**

### **Formato Padrão de Evento**
```json
{
  "event_id": "unique_identifier",
  "name": "Nome do Evento",
  "category": "categoria_detectada",
  "start_time": "ISO 8601 datetime",
  "end_time": "ISO 8601 datetime",
  "timezone": "America/Sao_Paulo",
  "location": "Circuito/Local",
  "description": "Descrição detalhada",
  "source": "fonte_origem",
  "broadcast_info": [
    {
      "provider": "Nome do Provedor",
      "url": "https://link.transmissao",
      "type": "live|replay|highlights"
    }
  ],
  "metadata": {
    "series": "Série/Championship",
    "round": "Número da Rodada",
    "session_type": "qualifying|race|practice"
  }
}
```

## **🔮 Roadmap de Fontes**

### **Prioridade Alta**
1. **Finalizar integração OpenF1**
   - Substituir completamente o Ergast
   - Adicionar suporte a dados em tempo real

2. **MotoGP Official**
   - Implementar coleta de calendário
   - Adicionar sessões de treinos e classificações

### **Prioridade Média**
1. **NASCAR**
   - Calendário oficial
   - Horários de transmissão

2. **IndyCar**
   - Calendário e resultados
   - Links para transmissões

### **Prioridade Baixa**
1. **WEC (World Endurance Championship)**
2. **Fórmula E**
3. **Outras categorias nacionais**

---

## **🔍 Detalhes Técnicos das Fontes

### **Tomada de Tempo**
- **Método de Coleta**: Web Scraping com BeautifulSoup
- **Frequência de Atualização**: A cada execução (com cache de 1h)
- **Tratamento Especial**:
  - Normalização de nomes de categorias
  - Extração de datas em português
  - Mapeamento de canais de TV

### **Ergast API**
- **Endpoint Base**: http://ergast.com/api/f1
- **Exemplo de Requisição**:
  ```
  GET /api/f1/current.json
  ```
- **Limite de Requisições**: 200 por hora
- **Cache**: 24h para dados de calendário

## **⚠️ Limitações e Considerações**

1. **Tomada de Tempo**
   - Depende da estrutura HTML do site
   - Pode quebrar com atualizações no layout
   - Necessário tratamento manual de feriados e datas especiais

2. **Ergast API**
   - Descontinuação prevista para 2024
   - Dados podem não refletir mudanças de última hora

3. **OpenF1**
   - API em desenvolvimento ativo
   - Pode haver mudanças na estrutura dos dados

---

## **🧪 Testes de Fontes**

### **Testes Automatizados**
- Testes unitários para cada fonte
- Verificação de schema dos dados
- Testes de conectividade
- Validação de fusos horários

### **Monitoramento**
- Uptime das fontes
- Taxa de sucesso das requisições
- Tempo de resposta
- Qualidade dos dados coletados

## **📝 Notas de Atualização

### **Últimas Alterações**
- **01/08/2024**: Melhorias na extração de dados do Tomada de Tempo
- **30/07/2024**: Adicionado suporte inicial ao OpenF1 API
- **25/07/2024**: Correção no tratamento de fusos horários

### **Próximas Atualizações**
- Implementação completa do OpenF1
- Adição de mais categorias
- Melhorias na detecção automática de eventos
   - *Dados*: Calendário, horários das corridas
   - *Confiabilidade*: ⭐⭐⭐⭐⭐

#### **Provedores de Streaming:**
- **Brasil**: SporTV
- **Internacional**: WorldSBK VideoPass

---

### **🌐 Fontes Agregadoras**

#### **🥇 Tomada de Tempo** (FONTE PRIMÁRIA)
- *URL*: https://www.tomadadetempo.com.br/
- *Cobertura*: Automobilismo brasileiro e internacional
- *Dados*: Calendários completos, horários, transmissões
- *Confiabilidade*: ⭐⭐⭐⭐⭐
- *Prioridade*: **MÁXIMA** - Fonte brasileira especializada
- *Streaming*: Links diretos para transmissões no Brasil

#### **Motorsport.com**
- *URL*: https://motorsport.com/
- *Cobertura*: Múltiplas categorias globais
- *Dados*: Calendários, notícias, horários
- *Confiabilidade*: ⭐⭐⭐⭐⭐

#### **Autosport**
- *URL*: https://www.autosport.com/
- *Cobertura*: F1, IndyCar, WEC, etc.
- *Dados*: Calendários, análises
- *Confiabilidade*: ⭐⭐⭐⭐

---

## **🔧 Configuração de Prioridades**

### **Ordem de Prioridade Sugerida:**
1. **🥇 Tomada de Tempo** (tomadadetempo.com.br) - FONTE PRIMÁRIA
2. **APIs Oficiais** (quando disponíveis)
3. **Sites Oficiais das Categorias**
4. **Fontes Agregadoras Confiáveis**
5. **APIs Não-Oficiais**

### **Critérios de Exclusão:**
- Fontes com dados inconsistentes
- Sites com anti-bot muito restritivo
- Fontes que requerem autenticação complexa
- Sites com estrutura HTML muito instável

---

## **📺 Mapeamento de Streaming por Região**

### **Brasil:**
```json
{
  "F1": ["SporTV", "F1 TV Pro"],
  "MotoGP": ["SporTV", "ESPN"],
  "StockCar": ["SporTV", "YouTube"],
  "NASCAR": ["ESPN", "Fox Sports"],
  "WSBK": ["SporTV"]
}
```

### **Internacional:**
```json
{
  "F1": ["F1 TV Pro", "Sky Sports"],
  "MotoGP": ["MotoGP VideoPass"],
  "NASCAR": ["NBC Sports", "Fox Sports"],
  "WSBK": ["WorldSBK VideoPass"]
}
```

---

## **⚙️ Implementação Técnica**

### **Estrutura de Dados Coletados:**
```json
{
  "event_id": "unique_identifier",
  "name": "Nome do Evento",
  "category": "categoria_detectada_dinamicamente",
  "category_type": "cars|motorcycles|mixed|other",
  "subcategory": "subcategoria_se_aplicavel",
  "date": "2024-XX-XX",
  "time": "HH:MM",
  "timezone": "America/Sao_Paulo",
  "location": "Nome do Circuito",
  "country": "País",
  "session_type": "race|qualifying|practice|other",
  "streaming_links": ["URL1", "URL2"],
  "official_url": "URL_oficial_do_evento",
  "source": "nome_da_fonte",
  "category_confidence": 0.95,
  "raw_category_text": "texto_original_da_categoria"
}
```

### **✨ Detecção Dinâmica de Categorias**

#### **Sistema de Reconhecimento Inteligente:**
- **Aprendizado automático**: Identifica novas categorias automaticamente
- **Mapeamento de variações**: Reconhece diferentes nomes para a mesma categoria
- **Classificação por tipo**: Carros, motos, misto ou outros
- **Confiança de detecção**: Score de confiança para cada categoria identificada

#### **Exemplos de Mapeamento:**
```json
{
  "F1": ["Formula 1", "Fórmula 1", "Formula One", "Grand Prix"],
  "MotoGP": ["Moto GP", "MotoGrandPrix", "World Championship"],
  "StockCar": ["Stock Car Brasil", "Stock Car", "SCB"],
  "WEC": ["World Endurance", "Endurance Championship", "Le Mans"]
}
```

#### **Algoritmo de Detecção:**
1. **Extração**: Coleta texto bruto da categoria da fonte
2. **Normalização**: Remove acentos, caracteres especiais, padroniza case
3. **Matching**: Compara com base de conhecimento existente
4. **Classificação**: Determina tipo (carros/motos) e subcategoria
5. **Aprendizado**: Adiciona novas variações à base de conhecimento

### **Configurações de Coleta:**
- **Timeout**: 10 segundos por requisição
- **Retry**: controlado por `data_sources.retry_failed_sources` (padrão: `true`), `data_sources.max_retries` (padrão: `1`, exclui a tentativa inicial) e `data_sources.retry_backoff_seconds` (padrão: `0.5`, backoff linear). Compatível com `retry_attempts` (legado) quando as novas chaves não estiverem presentes.
- **Rate Limiting**: 1 requisição por segundo
- **User-Agent**: Rotativo para evitar bloqueios
- **Category Learning**: Habilita/desabilita aprendizado de novas categorias

---

**🔍 VALIDAÇÃO NECESSÁRIA:**

1. **As categorias listadas atendem suas necessidades?**
2. **Há alguma categoria específica que faltou?** (IndyCar, WEC, F2, F3, etc.)
3. **Os provedores de streaming para o Brasil estão corretos?**
4. **Prefere focar em fontes brasileiras ou incluir eventos internacionais?**
5. **Alguma fonte específica que você já conhece e recomenda?**

Confirme se esta estrutura de fontes está adequada para prosseguirmos! 🏁
