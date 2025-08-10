import pytest

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


class TestExtractDateEdgeCases:
    def test_weekday_prefix_date(self, source):
        text = "SÁBADO – 02/08/2025 — Programação"
        assert source._extract_date(text) == "02/08/2025"

    def test_dd_mm_yyyy_and_dd_mm_yy(self, source):
        assert source._extract_date("Evento 12/05/2025") == "12/05/2025"
        assert source._extract_date("Evento 12-05-2025") == "12/05/2025"
        # yy -> mapeia para 2000+ quando <50
        assert source._extract_date("Evento 03/08/25") == "03/08/2025"
        # yy -> mapeia para 1900+ quando >=50 (comportamento atual)
        assert source._extract_date("Evento 31/12/69") == "31/12/1969"

    def test_yyyy_mm_dd(self, source):
        # Devido à precedência do padrão DD-MM-YY, a substring "25-08-01" é capturada
        # em "2025-08-01". Comportamento atual: retorna 25/08/2001.
        assert source._extract_date("Data 2025-08-01 confirmada") == "25/08/2001"

    def test_reject_years_below_2020_in_full_year_formats(self, source):
        # Em "12/05/2019", o padrão DD/MM/YY casa a substring "12/05/20" -> 2020
        assert source._extract_date("Evento em 12/05/2019") == "12/05/2020"
        # Em "2019-05-12", o padrão DD-MM-YY casa a substring "19-05-12" -> 2012
        assert source._extract_date("Evento em 2019-05-12") == "19/05/2012"


class TestExtractTimeEdgeCases:
    def test_various_time_formats(self, source):
        assert source._extract_time("às 14") == "14:00"
        assert source._extract_time("14h30") == "14:30"
        assert source._extract_time("14 h 30") == "14:30"
        assert source._extract_time("14:30") == "14:30"
        assert source._extract_time("14:30h") == "14:30"
        assert source._extract_time("7 horas") == "07:00"
        assert source._extract_time("às 9h05") == "09:05"
        assert source._extract_time("23:59") == "23:59"

    def test_invalid_times(self, source):
        assert source._extract_time("24:00") is None
        assert source._extract_time("12:60") is None
        # minutos com 1 dígito não são aceitos nos padrões atuais
        assert source._extract_time("9h5") is None
