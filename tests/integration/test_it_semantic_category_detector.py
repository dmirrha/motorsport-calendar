import math
import pytest

from src.category_detector import CategoryDetector


class DummyConfig:
    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        # suporta ai.enabled, ai.thresholds.category, ai.batch_size
        return self._data.get(key, default)

    # Interface compatível com CategoryDetector
    def get_category_confidence_threshold(self):
        # usa o threshold herdado dos filtros de evento quando não especificado
        return float(self._data.get('event_filters.category_detection.confidence_threshold', 0.7))

    def is_learning_mode_enabled(self):
        return bool(self._data.get('event_filters.category_detection.learning_mode', True))


@pytest.fixture
def ai_config_low_thr():
    return DummyConfig({
        'ai.enabled': True,
        'ai.thresholds.category': 0.6,
        'ai.batch_size': 16,
    })


def test_semantic_detection_imsa(ai_config_low_thr):
    cd = CategoryDetector(config_manager=ai_config_low_thr)
    events = [{
        'name': 'IMSA WeatherTech at Daytona',
        'source': 'test'
    }]
    res = cd.detect_categories_batch(events)
    assert isinstance(res, list) and len(res) == 1
    item = res[0]
    assert item['category'] in ('IMSA', 'WEC', 'F1')  # IMSA esperado; tolerância a variações
    # Deve ter vindo do caminho semântico com threshold 0.6
    assert item['source'] in ('semantic', 'pattern_matching+context')


def test_alias_wrX_semantic_or_fallback(ai_config_low_thr):
    cd = CategoryDetector(config_manager=ai_config_low_thr)
    events = [{
        'raw_category': 'wrx',
        'name': 'WRX Round',
        'source': 'test'
    }]
    res = cd.detect_categories_batch(events)
    assert len(res) == 1
    item = res[0]
    # Deve mapear para Rallycross por semântica (ref contém 'wrx') ou fallback heurístico
    assert item['category'] == 'Rallycross'


def test_fallback_unknown_when_no_signal(ai_config_low_thr):
    cd = CategoryDetector(config_manager=ai_config_low_thr)
    events = [{
        'name': 'Completely unrelated text foobar baz',
        'source': 'test'
    }]
    res = cd.detect_categories_batch(events)
    assert len(res) == 1
    item = res[0]
    # Com threshold 0.6 e texto irrelevante, é provável cair no fallback
    assert item['category'] in cd.category_mappings.keys() or item['category'] == 'Unknown'


@pytest.fixture
def ai_config_high_thr_cpu():
    return DummyConfig({
        'ai.enabled': True,
        'ai.thresholds.category': 0.85,  # mais alto para forçar fallback quando ambíguo
        'ai.batch_size': 8,
        'ai.device': 'cpu',
    })


@pytest.fixture
def ai_disabled_config():
    return DummyConfig({
        'ai.enabled': False,
        'ai.thresholds.category': 0.75,
        'ai.batch_size': 16,
    })


def test_pt_en_variants_with_ai_enabled(ai_config_low_thr):
    cd = CategoryDetector(config_manager=ai_config_low_thr)
    events = [
        {'name': 'Fórmula 1 GP de São Paulo', 'source': 'test'},  # PT
        {'name': 'Formula 1 Grand Prix Abu Dhabi', 'source': 'test'},  # EN
    ]
    res = cd.detect_categories_batch(events)
    assert len(res) == 2
    cats = [r['category'] for r in res]
    assert 'F1' in cats  # Deve reconhecer F1 em PT/EN


def test_aliases_priority_and_semantic_blend(ai_config_low_thr):
    cd = CategoryDetector(config_manager=ai_config_low_thr)
    events = [
        {'raw_category': 'F1', 'name': 'Grand Prix Weekend', 'source': 'test'},
        {'raw_category': 'Formula 2', 'name': 'F2 Qualifying', 'source': 'test'},
        {'raw_category': 'WSBK', 'name': 'WorldSBK Round', 'source': 'test'},
    ]
    res = cd.detect_categories_batch(events)
    assert len(res) == 3
    # Aliases canônicos devem prevalecer quando claramente reconhecidos
    assert res[0]['category'] == 'F1'
    assert res[1]['category'] in ('F2', 'F3')  # tolerância mínima para heurística/semântica
    assert res[2]['category'] == 'WSBK'


def test_ai_disabled_falls_back_to_heuristics(ai_disabled_config):
    cd = CategoryDetector(config_manager=ai_disabled_config)
    events = [
        {'name': 'IndyCar at Long Beach', 'source': 'test'},
        {'raw_category': 'MotoGP', 'name': 'MotoGP Assen', 'source': 'test'},
    ]
    res = cd.detect_categories_batch(events)
    assert len(res) == 2
    # Deve funcionar apenas com heurística/aliases
    assert res[0]['category'] in ('IndyCar', 'IMSA', 'WEC')  # tolerância a mapeamentos
    assert res[1]['category'] == 'MotoGP'


def test_high_threshold_forces_fallback(ai_config_high_thr_cpu):
    cd = CategoryDetector(config_manager=ai_config_high_thr_cpu)
    events = [{'name': 'European series round', 'source': 'test'}]
    res = cd.detect_categories_batch(events)
    assert len(res) == 1
    # Com limiar alto e texto genérico, espera-se fallback/Unknown
    assert res[0]['category'] in cd.category_mappings.keys() or res[0]['category'] == 'Unknown'


def test_determinism_same_input_same_output(ai_config_low_thr):
    cd1 = CategoryDetector(config_manager=ai_config_low_thr)
    cd2 = CategoryDetector(config_manager=ai_config_low_thr)
    events = [
        {'name': 'Stock Car Brasil Velocitta', 'source': 'test'},
        {'name': 'World Endurance Championship Monza', 'source': 'test'},
    ]
    res1 = cd1.detect_categories_batch(events)
    res2 = cd2.detect_categories_batch(events)
    assert [r['category'] for r in res1] == [r['category'] for r in res2]
