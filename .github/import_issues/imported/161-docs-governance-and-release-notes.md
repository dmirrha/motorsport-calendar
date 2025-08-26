# Docs/Governança: sincronia com IA (README, REQUIREMENTS, CONFIGURATION_GUIDE, CHANGELOG, RELEASES)

## 📝 Descrição
Atualizar documentação e governança para refletir as novas capacidades de IA, mantendo opt-in e orientações de execução local/offline.

## 🔍 Contexto
- Atualizar: `README.md`, `REQUIREMENTS.md`, `CONFIGURATION_GUIDE.md`, `CHANGELOG.md`, `RELEASES.md`.
- Alinhar com Release Drafter e SemVer adotado.

## 🎯 Comportamento Esperado
- Documentação clara de setup local (CPU/MPS/GPU), flags `ai.*`, troubleshooting e performance tips.
- Notas de versão com impactos e compatibilidade (IA desativada por padrão).

## 🛠️ Passos
1. Atualizar seções e exemplos de configuração.
2. Descrever execução offline e dependências opcionais.
3. Checklist de release com validação dos docs.

## 📋 Critérios de Aceitação
- [ ] Docs atualizadas e consistentes com o código.
- [ ] Release notes alinhadas ao Release Drafter.
- [ ] Sem breaking changes não documentados.

## 📊 Impacto
Médio — melhora a adoção segura e a rastreabilidade.

## 🔗 Relacionamento
- EPIC: #157

## 🔗 Referências
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
- `src/utils/config_validator.py`
