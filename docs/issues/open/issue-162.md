# Issue 162 — Config/Validator: chaves ai.* e defaults alinhados ao plano

- ID: 3356427015
- Número: 162
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/162
- Criado em: 2025-08-26T16:56:41Z
- Atualizado em: 2025-08-26T17:11:22Z
- Labels: needs-triage, priority: P1, ai, docs, config

## Contexto
Adicionar chaves `ai.*` ao `config/config.example.json` e validar em `src/utils/config_validator.py` com mensagens claras e defaults alinhados ao plano. Integrar validação no `ConfigManager` e documentar no guia de configuração. Garantir testes cobrindo casos válidos e inválidos.

## Objetivo
- Config consistente e validada para a seção `ai`.
- Defaults sensíveis e erros descritivos.
- Compatibilidade com `ConfigManager` e demais seções atuais.

## Escopo
- Atualizar `config/config.example.json` com a seção `ai`.
- Implementar validações/normalizações em `src/utils/config_validator.py` via `validate_ai_config()`.
- Integrar validação no `src/config_manager.py` dentro de `validate_config()`.
- Documentar em `docs/CONFIGURATION_GUIDE.md`.
- Ajustar `requirements.txt` apenas se necessário (deps opcionais). Nenhum ajuste foi necessário.

## Critérios de Aceite
- [x] Defaults corretos e tipos/intervalos validados.
- [x] Guia de configuração atualizado.
- [x] Testes básicos de validação com exemplos válidos/ inválidos.

## Plano de Resolução (proposto)
1) Config de exemplo
- Adicionar a seção `ai` com chaves: `enabled=false`, `device=auto`, `batch_size=16`, `thresholds.category=0.75`, `thresholds.dedup=0.85`, `onnx.enabled=false`, `onnx.provider=cpu`, `onnx.opset=17`, `cache.enabled=true`, `cache.dir=cache/embeddings`, `cache.ttl_days=30`.

2) Validação e normalização
- Criar `validate_ai_config()` em `src/utils/config_validator.py` para validar e normalizar tipos/valores, preparar diretório de cache e checar permissões.
- Dispositivos aceitos: `auto`, `cpu`, `cuda`, `mps`.
- ONNX providers aceitos: `cpu`, `cuda`, `coreml`.

3) Integração no ConfigManager
- Em `src/config_manager.py`, chamar `validate_ai_config()` dentro de `validate_config()` e armazenar a versão normalizada em `self.config['ai']`.
- Tornar o import de `config_validator` resiliente a diferentes contextos de execução (pacote vs módulo solto).

4) Documentação
- Atualizar `docs/CONFIGURATION_GUIDE.md` com a nova seção `ai`, incluindo tabela de parâmetros, tipos e defaults.

5) Testes
- Cobrir caminhos felizes e erros (tipos inválidos, ranges fora do permitido, provider/device inválidos, permissão de escrita em diretório de cache, etc.) em `tests/unit/utils/test_config_validator.py`.

## Resultados — Verificações
- `config/config.example.json`: seção `ai` presente com chaves e defaults esperados (`173–191`).
- `src/utils/config_validator.py`: `validate_ai_config()` implementada com validação completa e normalização (linhas ~473–609). Exceções via `ConfigValidationError` com `ErrorCode` adequado.
- `docs/CONFIGURATION_GUIDE.md`: seção `ai` documentada com parâmetros, defaults e notas (linhas ~223–260).
- `src/config_manager.py`: import resiliente de `config_validator` via múltiplos caminhos (`14–31`) e chamada a `validate_ai_config()` dentro de `validate_config()` (`299–304`).
- Testes: `tests/unit/utils/test_config_validator.py` cobre casos para `ai` (arquivo presente e em uso; cenários válidos/ inválidos).
- Documentação de release: `CHANGELOG.md` e `RELEASES.md` atualizados com o fix do import resiliente e seção de AI.

## Checklist de Execução
- [x] Seção `ai` adicionada ao `config.example`.
- [x] Função `validate_ai_config()` implementada e coberta por testes.
- [x] Integração no `ConfigManager.validate_config()` realizada.
- [x] Documentação atualizada (`docs/CONFIGURATION_GUIDE.md`, `CHANGELOG.md`, `RELEASES.md`).
- [x] Suíte de testes passou localmente.

## Logs e Referências
- Arquivos: `config/config.example.json`, `src/utils/config_validator.py`, `src/config_manager.py`, `docs/CONFIGURATION_GUIDE.md`, `tests/unit/utils/test_config_validator.py`, `CHANGELOG.md`, `RELEASES.md`.
- Issue: https://github.com/dmirrha/motorsport-calendar/issues/162
- Epic relacionada: #157

## Status
- Aberta; pronta para criação de branch e abertura de PR que referencia e fecha a issue.
