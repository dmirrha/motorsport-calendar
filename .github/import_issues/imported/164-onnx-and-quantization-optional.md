# F3 (opcional): ONNX e quantização para aceleração local

## 📝 Descrição
Converter o modelo para ONNX e habilitar execução opcional via `onnxruntime` (providers auto: CPU/MPS/GPU). Avaliar ganhos de latência/throughput e qualidade.

## 🔍 Contexto
- Não deve ser padrão; habilitar por `ai.onnx.enabled=true`.
- Providers configuráveis (`ai.onnx.providers`).

## 🎯 Comportamento Esperado
- Melhorar latência sem perder qualidade acima da tolerância definida no plano.
- Manter fallback para execução padrão.

## 🛠️ Passos
1. Pipeline de export PT→ONNX (ou direto do Transformers) e testes de consistência.
2. Integração no `embeddings_service` para usar ORT quando enabled.
3. Benchmarks comparativos e documentação de setup.

## 📋 Critérios de Aceitação
- [ ] Execução ONNX habilitável por config; fallback seguro.
- [ ] Benchmarks mostram ganhos claros ou decisão documentada.
- [ ] Sem regressão de qualidade acima do limite.

## 📊 Impacto
Médio — otimização de performance opcional.

## 🔗 Referências
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
- `src/ai/embeddings_service.py`
