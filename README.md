# 🏁 Motorsport Calendar Generator

Um script Python avançado para coleta automática de eventos de automobilismo de múltiplas fontes e geração de arquivos iCal para importação no Google Calendar. Desenvolvido para entusiastas de automobilismo que desejam acompanhar todas as corridas do fim de semana em um só lugar.

## 🎯 Características

- ✅ **Coleta automática** de eventos de múltiplas fontes
- ✅ **Interface visual colorida** com progresso em tempo real
- ✅ **Detecção inteligente** do fim de semana alvo
- ✅ **Remoção de duplicatas** entre fontes
- ✅ **Configuração flexível** via arquivo JSON
- ✅ **Logging avançado** com payloads preservados
- ✅ **Compatível com Google Calendar**
- ✅ **Detecção dinâmica** de categorias de automobilismo
- ✅ **Processamento inteligente** de datas e horários
- ✅ **Suporte a múltiplos fusos horários**
- ✅ **Gerenciamento de erros** robusto e informativo

## 🏎️ Categorias Suportadas

**✨ Suporte Dinâmico a TODAS as Categorias de Esporte Automotor**

O script detecta automaticamente e coleta eventos de **qualquer categoria** encontrada nas fontes de dados, incluindo mas não limitado a:

### **🏎️ Carros:**
- Fórmula 1, F2, F3, F4
- Stock Car Brasil, NASCAR
- IndyCar, Super Fórmula
- WEC (World Endurance Championship)
- IMSA, DTM, Super GT
- Fórmula E, Extreme E
- Rally (WRC), Rallycross
- Turismo, GT World Challenge

### **🏍️ Motos:**
- MotoGP, Moto2, Moto3
- World Superbike (WSBK)
- Supersport, Superstock
- MotoE, MotoAmerica
- British Superbike (BSB)

### **🚗 Outras Modalidades:**
- Karting, Drift
- Arrancada, Autocross
- Hill Climb, Time Attack
- **E muito mais!**

> 💡 **Flexibilidade Total:** O sistema se adapta automaticamente a novas categorias que apareçam nas fontes de dados, sem necessidade de atualizações no código.

## 🔧 Requisitos

- **Python 3.8+**
- **Sistema Operacional**: macOS, Linux, Windows (testado principalmente no macOS)
- **Conexão com internet** para coleta de dados
- **Dependências**: Verifique o arquivo `requirements.txt` para a lista completa

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/motorsport-calendar.git
cd motorsport-calendar

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o arquivo de configuração
cp config.example.json config.json
# Edite config.json conforme necessário
```

## 🚀 Uso

```bash
# Execução básica
python motorsport_calendar.py

# Com configuração personalizada
python motorsport_calendar.py --config custom_config.json

# Com saída personalizada
python motorsport_calendar.py --output meu_calendario.ics

# Modo verbose
python motorsport_calendar.py --verbose
```

## 📁 Estrutura do Projeto

```
motorsport-calendar/
├── motorsport_calendar.py     # Script principal
├── config.json               # Configuração principal
├── config.example.json       # Exemplo de configuração
├── requirements.txt          # Dependências
├── src/                      # Código fonte modular
├── sources/                  # Módulos de coleta por fonte
├── output/                   # Arquivos iCal gerados
├── logs/                     # Logs e payloads
└── tests/                    # Testes unitários
```

## ⚙️ Configuração

O arquivo `config.json` permite personalizar:

- **Fontes de dados** e prioridades
- **Categorias** incluídas/excluídas
- **Parâmetros iCal** (timezone, lembretes, etc.)
- **Links de transmissão** por região
- **Sistema de logging**

## 🎨 Interface Visual

O script exibe uma interface colorida com:
- Progress bars em tempo real
- Status de cada fonte de dados
- Contadores de eventos coletados
- Indicadores visuais de sucesso/erro

## 📊 Logging e Debug

- **Logs centralizados** com múltiplos níveis
- **Payloads raw** preservados por fonte
- **Rotação automática** por execução
- **Debug completo** para troubleshooting

## 🌐 Fontes de Dados

### Fonte Primária
- **Tomada de Tempo** (tomadadetempo.com.br) - Prioridade máxima
  - Coleta detalhada de programação de TV e internet
  - Suporte a múltiplas categorias de automobilismo
  - Atualização em tempo real dos horários de transmissão

### Fontes Secundárias
- **Ergast API** (http://ergast.com/mrd/) - Dados históricos e atuais de F1
- **OpenF1 API** (https://openf1.org/) - Alternativa moderna para dados de F1
- **Sites oficiais** das categorias - Para informações diretas das fontes oficiais
- **Motorsport.com** - Cobertura abrangente de múltiplas categorias
- **Autosport** - Dados confiáveis sobre automobilismo mundial

> ⚠️ **Nota sobre a Ergast API**: Será descontinuada em 2024. O sistema já está preparado para a transição para a OpenF1 API.

## 📅 Importação no Google Calendar

1. Execute o script para gerar o arquivo `.ics`
2. Abra o Google Calendar
3. Clique em "+" ao lado de "Outros calendários"
4. Selecione "Importar"
5. Faça upload do arquivo `motorsport_events.ics`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🏁 Status do Projeto

🚀 **Versão Estável** - Em produção

### Últimas Atualizações
- Melhoria na detecção de eventos do Tomada de Tempo
- Correção de bugs no processamento de datas e horários
- Aprimoramento do sistema de logging
- Melhor tratamento de erros e recuperação
- Otimização de performance para processamento em lote

### Próximos Passos
- Implementação de mais fontes de dados
- Melhorias na detecção de categorias
- Suporte a notificações personalizadas
- Interface web para configuração e visualização
- Exportação para outros formatos de calendário

---

**Desenvolvido com ❤️ para entusiastas do automobilismo**
