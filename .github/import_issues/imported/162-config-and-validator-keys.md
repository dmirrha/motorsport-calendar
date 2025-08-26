# Config/Validator: chaves ai.* e defaults alinhados ao plano

## 📝 Descrição
Adicionar chaves `ai.*` ao `config/config.example.json` e validar em `src/utils/config_validator.py` com mensagens claras e defaults alinhados ao plano.

## 🔍 Contexto
- Chaves: `ai.enabled=false`, `ai.model_name`, `ai.device=auto`, `ai.cache_dir`, `ai.batch_size`, `ai.thresholds.category=0.75`, `ai.thresholds.dedup=0.85`, `ai.onnx.enabled=false`, `ai.onnx.providers=[]`.

## 🎯 Comportamento Esperado
- Config consistente e validada; erros descritivos.
- Compatível com `ConfigManager` e demais seções atuais.

## 🛠️ Passos
1. Atualizar `config/config.example.json`.
2. Implementar validações/normalizações em `src/utils/config_validator.py`.
3. Documentar no `docs/CONFIGURATION_GUIDE.md`.
4. Ajustar `requirements.txt` apenas se necessário (deps opcionais).

## 📋 Critérios de Aceitação
- [ ] Defaults corretos e tipos/intervalos validados.
- [ ] Guia de configuração atualizado.
- [ ] Tests básicos de validação com exemplos válidos/ inválidos.

## 📊 Impacto
Médio — base para ativação segura da IA.

## 🔗 Referências
- `src/utils/config_validator.py`
- `config/config.example.json`
- `docs/CONFIGURATION_GUIDE.md`
- `requirements.txt`
