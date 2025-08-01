# 🏁 Motorsport Calendar Generator

Um script Python para coletar automaticamente eventos de automobilismo do fim de semana e gerar arquivos iCal para importação no Google Calendar.

## 🎯 Características

- ✅ **Coleta automática** de eventos de múltiplas fontes
- ✅ **Interface visual colorida** com progresso em tempo real
- ✅ **Detecção inteligente** do fim de semana alvo
- ✅ **Remoção de duplicatas** entre fontes
- ✅ **Configuração flexível** via arquivo JSON
- ✅ **Logging avançado** com payloads preservados
- ✅ **Compatível com Google Calendar**

## 🏎️ Categorias Suportadas

- **Fórmula 1** (F1)
- **MotoGP**
- **Stock Car Brasil**
- **NASCAR**
- **World Superbike (WSBK)**

## 🔧 Requisitos

- **Python 3.8+**
- **macOS** (testado no MacBook)
- Conexão com internet

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

### Fontes Secundárias
- Ergast API (F1)
- OpenF1 API (F1)
- Sites oficiais das categorias
- Motorsport.com
- Autosport

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

🚧 **Em Desenvolvimento** - Versão inicial em construção

---

**Desenvolvido com ❤️ para entusiastas do automobilismo**
