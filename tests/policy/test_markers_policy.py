import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[2]
INTEGRATION_DIR = ROOT / "tests" / "integration"


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Arquivo inválido para leitura como texto — considere como não contendo marcador
        return ""


def test_e2e_files_must_not_have_integration_marker():
    """
    Garante que testes E2E (test_phase2_e2e_*.py) NÃO usem pytest.mark.integration.
    Isso evita que rodem no job de integração do CI por engano.
    """
    e2e_files = sorted(INTEGRATION_DIR.glob("test_phase2_e2e_*.py"))
    offending = []
    for f in e2e_files:
        content = _read_text(f)
        if "pytest.mark.integration" in content:
            offending.append(f.relative_to(ROOT))
    assert not offending, (
        "Arquivos E2E não devem ter marcador integration (remova pytest.mark.integration):\n"
        + "\n".join(str(p) for p in offending)
    )


def test_non_e2e_integration_files_must_have_integration_marker():
    """
    Garante que testes de integração (não-E2E) tenham o marcador pytest.mark.integration.
    Mantém a seleção correta no job de integração do CI.
    """
    all_py = sorted(INTEGRATION_DIR.glob("test_*.py"))
    e2e_files = set(INTEGRATION_DIR.glob("test_phase2_e2e_*.py"))
    non_e2e = [p for p in all_py if p not in e2e_files]

    missing = []
    for f in non_e2e:
        content = _read_text(f)
        if "pytest.mark.integration" not in content:
            missing.append(f.relative_to(ROOT))

    assert not missing, (
        "Arquivos de integração (não-E2E) devem conter pytest.mark.integration:\n"
        + "\n".join(str(p) for p in missing)
    )
