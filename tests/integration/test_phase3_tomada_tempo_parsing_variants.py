import pathlib
import pytest

pytestmark = [pytest.mark.integration]

FIXTURES_DIR = pathlib.Path(__file__).parents[1] / "fixtures" / "html" / "tomada_tempo"


def _read_fixture(name: str):
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_tomada_tempo_happy_path_skeleton():
    pytest.skip("Issue #105: implementar parsing happy path usando fixture programming_happy.html")


def test_tomada_tempo_missing_fields_skeleton():
    pytest.skip("Issue #105: implementar robustez com campos ausentes usando fixture programming_missing_fields.html")


def test_tomada_tempo_malformed_html_skeleton():
    pytest.skip("Issue #105: implementar tratamento de HTML malformado usando fixture programming_malformed.html")
