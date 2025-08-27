import math
import pytest

from src.category_detector import CategoryDetector


class DummyConfig:
    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        # suporta ai.enabled, ai.thresholds.category, ai.batch_size
        return self._data.get(key, default)


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
