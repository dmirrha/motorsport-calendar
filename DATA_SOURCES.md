# Fontes de Dados - Eventos de Automobilismo

## **Passo 1.1: Definir Fontes de Dados para Eventos de Automobilismo**

### **Objetivo**
Identificar e catalogar fontes confiáveis de dados para eventos de automobilismo, incluindo APIs públicas, sites oficiais e provedores de streaming, organizados por prioridade e categoria.

---

## **📊 Fontes de Dados por Categoria**

### **🏎️ Fórmula 1 (F1)**

#### **Fontes Prioritárias:**
1. **Ergast API** (http://ergast.com/mrd/)
   - *Tipo*: API REST gratuita
   - *Dados*: Calendário, resultados, horários de sessões
   - *Formato*: JSON/XML
   - *Confiabilidade*: ⭐⭐⭐⭐⭐
   - *Status*: Ativa (mas será descontinuada em 2024)

2. **Formula 1 Official API** (https://www.formula1.com/)
   - *Tipo*: Web scraping do site oficial
   - *Dados*: Calendário oficial, horários, circuitos
   - *Confiabilidade*: ⭐⭐⭐⭐⭐
   - *Streaming*: F1 TV Pro (regional)

3. **OpenF1 API** (https://openf1.org/)
   - *Tipo*: API REST gratuita (substituto do Ergast)
   - *Dados*: Dados em tempo real, calendário, sessões
   - *Formato*: JSON
   - *Confiabilidade*: ⭐⭐⭐⭐

#### **Provedores de Streaming:**
- **Brasil**: Globo/SporTV, F1 TV Pro
- **Internacional**: F1 TV Pro, Sky Sports, ESPN

---

### **🏍️ MotoGP**

#### **Fontes Prioritárias:**
1. **MotoGP Official Website** (https://www.motogp.com/)
   - *Tipo*: Web scraping
   - *Dados*: Calendário oficial, horários das sessões
   - *Confiabilidade*: ⭐⭐⭐⭐⭐

2. **MotoGP API** (não oficial)
   - *Tipo*: API extraída do site oficial
   - *Dados*: Resultados, calendário, pilotos
   - *Confiabilidade*: ⭐⭐⭐⭐

#### **Provedores de Streaming:**
- **Brasil**: SporTV, ESPN
- **Internacional**: MotoGP VideoPass

---

### **🏁 Stock Car Brasil**

#### **Fontes Prioritárias:**
1. **Stock Car Official Website** (https://stockcar.com.br/)
   - *Tipo*: Web scraping
   - *Dados*: Calendário, horários, circuitos
   - *Confiabilidade*: ⭐⭐⭐⭐⭐

2. **Motorsport.com Brasil** (https://motorsport.com/br/)
   - *Tipo*: Web scraping
   - *Dados*: Calendários múltiplas categorias
   - *Confiabilidade*: ⭐⭐⭐⭐

#### **Provedores de Streaming:**
- **Brasil**: SporTV, Motorsport.tv, YouTube (oficial)

---

### **🏎️ NASCAR**

#### **Fontes Prioritárias:**
1. **NASCAR Official API** (https://www.nascar.com/)
   - *Tipo*: Web scraping
   - *Dados*: Calendário Cup Series, Xfinity, Truck
   - *Confiabilidade*: ⭐⭐⭐⭐⭐

2. **ESPN NASCAR** (https://www.espn.com/racing/nascar/)
   - *Tipo*: Web scraping
   - *Dados*: Horários, resultados
   - *Confiabilidade*: ⭐⭐⭐⭐

#### **Provedores de Streaming:**
- **Brasil**: ESPN, Fox Sports
- **Internacional**: NBC Sports, Fox Sports

---

### **🏍️ World Superbike (WSBK)**

#### **Fontes Prioritárias:**
1. **WorldSBK Official Website** (https://www.worldsbk.com/)
   - *Tipo*: Web scraping
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
- **Retry**: 3 tentativas com backoff exponencial
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
