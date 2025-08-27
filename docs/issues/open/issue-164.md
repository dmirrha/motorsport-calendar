# Issue #164 — F3 (opcional): ONNX e quantização para aceleração local

Link: https://github.com/dmirrha/motorsport-calendar/issues/164
Estado: aberto
Prioridade/Labels: ai, performance, optional, priority: P2
Autor: @dmirrha
Criado em: 2025-08-26

## Descrição (do GitHub)
Converter o modelo para ONNX e habilitar execução opcional via `onnxruntime` (providers auto: CPU/MPS/GPU). Avaliar ganhos de latência/throughput e qualidade.

Requisitos:
- Não padrão; habilitar por `ai.onnx.enabled=true`.
- Providers configuráveis (`ai.onnx.providers`).

Comportamento Esperado:
- Melhorar latência sem perder qualidade acima da tolerância definida no plano.
- Manter fallback para execução padrão.

Passos sugeridos (GitHub):
1. Pipeline de export PT→ONNX (ou direto do Transformers) e testes de consistência.
2. Integração no `embeddings_service` para usar ORT quando enabled.
3. Benchmarks comparativos e documentação de setup.

Critérios de Aceitação:
- [ ] Execução ONNX habilitável por config; fallback seguro.
- [ ] Benchmarks mostram ganhos claros ou decisão documentada.
- [ ] Sem regressão de qualidade acima do limite.

Referências:
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
- `src/ai/embeddings_service.py`

## Logs e outras evidências
- N/A (nenhum erro; trata-se de melhoria opcional de performance)

---

## Plano de Resolução (proposto)

1) Configuração e estrutura
- Adicionar chave `ai.onnx` em `config.json` (documentação em `docs/CONFIGURATION_GUIDE.md` já tem seção `ai.onnx`, validar/atualizar):
  - `enabled`: boolean (padrão: false)
  - `providers`: lista de providers desejados por prioridade (ex.: ["coreml", "cuda", "cpu", "mps"]) — mapeados para ORT disponíveis no host
  - `model_path`: caminho opcional para um modelo ONNX local (se ausente, manter caminho atual determinístico)
  - `intra_op_num_threads`/`inter_op_num_threads` (opcional)

2) Embeddings Service
- Alterar `src/ai/embeddings_service.py` para suportar backend ORT opcional:
  - Se `ai.onnx.enabled` e `model_path` existir:
    - Criar `onnxruntime.InferenceSession` com providers suportados.
    - Preparar pré-processamento mínimo (tokenização ou featurização) — se inexistente no projeto, manter stub e retornar fallback.
    - Implementar fallback automático para backend atual determinístico se ORT não inicializar.
  - Se não habilitado ou sem `model_path`, comportamento atual permanece inalterado (100% offline/determinístico via hashing).

3) Quantização (opcional)
- Se `model_path` apontar para um modelo quantizado (INT8/FP16), garantir compatibilidade com ORT provider.
- Adicionar campo opcional `quantized: true|false` e observações de suporte.

4) Benchmarks
- Estender `scripts/eval/benchmarks.py` para modo `--engine onnx|default`.
- Medir latência total e por item, throughput e qualidade (métricas existentes) e gerar relatório comparativo.

5) Documentação
- Atualizar `README.md` com seção de ONNX e setup (instalação `onnxruntime`/`onnxruntime-gpu` conforme SO), exemplos de config e troubleshooting.
- Atualizar `REQUIREMENTS.md`/`requirements.txt` (incluir `onnxruntime` como extra opcional, não hard requirement).
- Atualizar `docs/CONFIGURATION_GUIDE.md` com chaves novas/confirmadas.

6) Testes
- Unit: mocks de ORT (session stub), teste de fallback quando provider indisponível, teste de seleção de provider.
- Integração: caminho habilitado com `ai.onnx.enabled=true` mas sem `model_path` (deve fazer fallback sem erro).

## Riscos e Mitigações
- Ausência de modelo real no repo: manter arquitetura plugável, sem quebrar determinismo atual.
- Compatibilidade de providers: detectar disponíveis e registrar aviso, mantendo fallback automático.
- Tamanho do pacote: evitar adicionar `onnxruntime` como dependência obrigatória; usar extra opcional.

## Checklist de Implementação
- [ ] Config `ai.onnx.*` validada (`src/utils/config_validator.py`).
- [ ] `embeddings_service` com caminho ORT opcional e fallback.
- [ ] Extra de instalação documentado para ORT (CPU/GPU/Mac).
- [ ] Benchmarks atualizados com comparação.
- [ ] Docs atualizadas (README, CONFIGURATION_GUIDE, RELEASES, CHANGELOG).
- [ ] PR referencia Issue #164 (Closes #164 se todos os critérios atendidos).

## Solicitação de Confirmação
Deseja que eu prossiga com a implementação conforme o plano acima (foco em infraestrutura ONNX opcional e fallback seguro, sem introduzir modelo proprietário no repositório)?
