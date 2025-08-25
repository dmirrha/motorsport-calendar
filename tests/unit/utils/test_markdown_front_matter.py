import textwrap

import pytest

from src.utils.markdown_front_matter import split_front_matter, strip_front_matter


def test_valid_front_matter_dict():
    md = textwrap.dedent(
        """
        ---
        title: Teste
        tags:
          - a
          - b
        ---
        # Conteudo
        corpo
        """
    ).strip()

    meta, content = split_front_matter(md)
    assert isinstance(meta, dict)
    assert meta["title"] == "Teste"
    assert meta["tags"] == ["a", "b"]
    assert content.startswith("# Conteudo")


def test_front_matter_non_dict_normalized():
    md = textwrap.dedent(
        """
        ---
        - a
        - b
        ---
        texto
        """
    ).strip()

    meta, content = split_front_matter(md)
    assert isinstance(meta, dict)
    assert meta.get("_front_matter") == ["a", "b"]
    assert content == "texto"


def test_missing_closing_fence_returns_original():
    md = textwrap.dedent(
        """
        ---
        title: Incompleto
        # Falta o fechamento
        """
    ).strip()

    meta, content = split_front_matter(md)
    # Falha segura: nada de meta e conteúdo original intacto
    assert meta is None
    assert content == md


def test_malformed_yaml_returns_original():
    md = textwrap.dedent(
        """
        ---
        : yaml ruim
        ---
        corpo
        """
    ).strip()

    meta, content = split_front_matter(md)
    assert meta is None
    assert content == md


def test_separator_in_the_middle_is_not_front_matter():
    md = textwrap.dedent(
        """
        # Titulo

        ---

        corpo
        """
    ).strip()

    meta, content = split_front_matter(md)
    assert meta is None
    assert content == md

    # strip_front_matter também não deve alterar
    assert strip_front_matter(md) == md


def test_no_front_matter():
    md = "apenas texto simples"
    meta, content = split_front_matter(md)
    assert meta is None
    assert content == md

    assert strip_front_matter(md) == md
