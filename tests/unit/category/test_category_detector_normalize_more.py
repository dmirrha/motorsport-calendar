import pytest

from category_detector import CategoryDetector


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []
        self.error_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def info(self, msg):
        self.info_calls.append(msg)

    def error(self, msg, exc_info=False):
        self.error_calls.append((msg, exc_info))


def test_normalize_handles_accents_punctuation_and_spaces():
    det = CategoryDetector(logger=LoggerStub())

    # Acentos + pontuação + múltiplos espaços + palavras de ruído
    raw = "  FórMuLa—1 ,,,   WORLD   Championship!!!  "
    norm = det.normalize_text(raw)
    assert norm == "formula 1"

    # Remoção de termos em PT-BR
    raw2 = "Campeonato de Super Fórmula"
    norm2 = det.normalize_text(raw2)
    assert norm2 == "super formula"

    # Ruídos comuns e consolidação de espaços
    raw3 = "Super   GT!!!"
    norm3 = det.normalize_text(raw3)
    assert norm3 == "super gt"


def test_normalize_edge_words_not_removed_if_not_in_list():
    det = CategoryDetector(logger=LoggerStub())

    # "Mundo" não está na lista de ruídos (apenas "mundial" e "world")
    raw = "Copa do Mundo de Rally"
    norm = det.normalize_text(raw)
    # Remove "copa", "do", "de" e pontuação; mantém "mundo"
    assert norm == "mundo rally"
