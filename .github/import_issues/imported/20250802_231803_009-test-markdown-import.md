# 🧪 Teste de Importação de Markdown

Este é um teste para verificar a importação correta de arquivos Markdown como corpo de issues.

## 📝 Detalhes do Teste

- **Objetivo**: Verificar se o conteúdo Markdown está sendo importado corretamente
- **Arquivo**: `009-test-markdown-import.md`
- **Script**: `.github/import_issues/import_issues.py`

## 📋 Itens a Verificar

- [x] Formatação de títulos
- [x] Listas
- [x] **Negrito** e *itálico*
- [x] Código inline `print("Hello, World!")`
- [x] Links [GitHub](https://github.com)

## 📝 Código

```python
def test_markdown():
    print("Este é um bloco de código")
    return True
```

## ✅ Resultado Esperado

O conteúdo deste arquivo deve aparecer formatado corretamente na issue do GitHub.
