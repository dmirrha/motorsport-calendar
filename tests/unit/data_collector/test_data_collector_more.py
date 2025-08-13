import types
from datetime import datetime
from pathlib import Path
import importlib

import pytest

from src.data_collector import DataCollector
from sources.base_source import BaseSource


class DummyLogger:
    def __init__(self):
        self.debug_calls = []
        self.step_calls = []
        self.err_calls = []
        self.success_calls = []

    def debug(self, msg: str):
        self.debug_calls.append(msg)

    def log_step(self, msg: str):
        self.step_calls.append(msg)

    def log_error(self, msg: str):
        self.err_calls.append(msg)

    def log_source_error(self, source_display: str, error_msg: str):
        self.err_calls.append((source_display, error_msg))

    def log_source_success(self, source_display: str, events_count: int):
        self.success_calls.append((source_display, events_count))


class DummyUI:
    def __init__(self):
        self.calls = []

    def show_step(self, title: str, message: str):
        self.calls.append((title, message))


class SimpleConfig:
    def __init__(self, max_concurrent_sources=1, excluded=None):
        self._data = {
            "max_concurrent_sources": max_concurrent_sources,
            "collection_timeout_seconds": 1,
            "retry_failed_sources": False,
            "priority_order": ["custom_a", "custom_b"],
            "excluded_sources": excluded or ["tomada_tempo"],
        }

    def get_data_sources_config(self):
        return self._data

    def get_streaming_providers(self, region: str):
        return {}


class OkSource(BaseSource):
    def get_display_name(self) -> str:
        return "OK"

    def get_base_url(self) -> str:
        return "https://ok.example"

    def collect_events(self, target_date: datetime | None = None):
        self.stats["requests_made"] += 1
        self.stats["successful_requests"] += 1
        self.stats["events_collected"] += 1
        self.stats["last_collection_time"] = datetime.now().isoformat()
        return [{"name": "X", "date": target_date or datetime.now()}]


class BadInitSource(BaseSource):
    def __init__(self, *a, **kw):  # type: ignore[override]
        raise RuntimeError("boom")

    def get_display_name(self) -> str:  # pragma: no cover (never reached)
        return "Bad"

    def get_base_url(self) -> str:  # pragma: no cover (never reached)
        return "https://bad.example"


class FailingSource(BaseSource):
    def get_display_name(self) -> str:
        return "FAIL"

    def get_base_url(self) -> str:
        return "https://fail.example"

    def collect_events(self, target_date: datetime | None = None):
        self.stats["requests_made"] += 1
        self.stats["failed_requests"] += 1
        self.stats["last_collection_time"] = datetime.now().isoformat()
        raise RuntimeError("fail-now")


def test__load_config_without_config_is_noop(monkeypatch):
    # Evita efeitos colaterais no __init__
    monkeypatch.setattr(DataCollector, "_discover_sources", lambda self: None)
    monkeypatch.setattr(DataCollector, "_initialize_sources", lambda self: None)

    dc = DataCollector(config_manager=None, logger=None, ui_manager=None)
    # Valores padrão mantidos
    assert dc.max_concurrent_sources == 3
    assert dc.collection_timeout == 300
    assert dc.retry_failed_sources is True


def test__discover_sources_handles_import_error_and_logs(monkeypatch):
    log = DummyLogger()

    # Cria instância neutralizando init pesado
    monkeypatch.setattr(DataCollector, "_load_config", lambda self: None)
    monkeypatch.setattr(DataCollector, "_initialize_sources", lambda self: None)
    dc = DataCollector(config_manager=SimpleConfig(excluded=["tomada_tempo"]), logger=log, ui_manager=None)

    # Força varredura retornando um arquivo de módulo fictício
    fake_file = Path("/tmp/fake_source.py")
    monkeypatch.setattr(Path, "glob", lambda self, pat: [fake_file] if str(self).endswith("/sources") else [])

    # Import de módulo inexistente deve falhar e ser logado
    monkeypatch.setattr(importlib, "import_module", lambda name: (_ for _ in ()).throw(ImportError("nope")))

    dc._discover_sources()

    # Mensagens de descoberta/erro presentes
    assert any("Failed to load source module" in m for m in log.debug_calls)
    assert any("Available sources" in m for m in log.debug_calls)


def test__initialize_sources_skips_excluded_and_logs_error(monkeypatch):
    log = DummyLogger()

    # Neutraliza descoberta e configura fontes manualmente
    monkeypatch.setattr(DataCollector, "_load_config", lambda self: None)
    monkeypatch.setattr(DataCollector, "_discover_sources", lambda self: None)
    dc = DataCollector(config_manager=None, logger=log, ui_manager=None)
    dc.available_sources = {
        "tomada_tempo": OkSource,  # será excluída
        "bad": BadInitSource,      # irá falhar na criação
    }
    dc.excluded_sources = {"tomada_tempo"}

    dc._initialize_sources()

    # Excluída não adicionada; erro de inicialização logado
    assert all(s.source_name != "tomada_tempo" for s in dc.active_sources)
    assert any(isinstance(e, tuple) or "Failed to initialize" in str(e) for e in log.err_calls)


def test_collect_events_calls_ui_and_uses_target_weekend_when_none(monkeypatch):
    log = DummyLogger()
    ui = DummyUI()
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # força sequencial

    dc = DataCollector(config_manager=cfg, logger=log, ui_manager=ui)
    assert dc.add_source(OkSource, priority=80)

    # Sem target_date explicitado
    events = dc.collect_events(target_date=None)
    assert len(events) == 1
    # UI chamada
    assert ui.calls and ui.calls[0][0] == "Data Collection"
    # Log de alvo
    assert any("Target date for collection" in m for m in log.debug_calls)


def test_sequential_handles_exception_and_updates_stats():
    log = DummyLogger()
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # sequencial
    dc = DataCollector(config_manager=cfg, logger=log, ui_manager=None)

    assert dc.add_source(OkSource, priority=60)
    assert dc.add_source(FailingSource, priority=50)

    events = dc.collect_events(target_date=datetime(2025, 1, 3))
    assert len(events) == 1  # somente OkSource entrega
    assert dc.collection_stats["successful_sources"] == 1
    assert dc.collection_stats["failed_sources"] == 1
    assert any(isinstance(e, tuple) for e in log.err_calls)


def test_get_target_weekend_returns_friday():
    # Neutraliza init pesado
    dc = DataCollector(config_manager=SimpleConfig(excluded=["tomada_tempo"]), logger=None, ui_manager=None)
    friday = dc._get_target_weekend()
    assert friday.weekday() == 4


def test_log_collection_summary_outputs_multiple_lines():
    log = DummyLogger()
    dc = DataCollector(config_manager=SimpleConfig(excluded=["tomada_tempo"]), logger=log, ui_manager=None)

    # Prepara estatísticas e resultados por fonte
    dc.collection_stats.update({
        "total_sources_attempted": 2,
        "successful_sources": 1,
        "failed_sources": 1,
        "total_events_collected": 1,
        "collection_start_time": datetime.now().isoformat(),
        "collection_end_time": datetime.now().isoformat(),
        "source_results": {
            "ok": {"success": True, "events_count": 1, "source_display_name": "OK"},
            "bad": {"success": False, "error": "x", "source_display_name": "BAD"},
        },
    })

    dc._log_collection_summary()
    # Pelo menos um log de passo e alguns debugs
    assert log.step_calls
    assert any("Collection completed" in m for m in log.debug_calls)


def test_context_manager_and_cleanup_logs_errors(monkeypatch):
    log = DummyLogger()
    cfg = SimpleConfig(excluded=["tomada_tempo"])  # sem built-in
    dc = DataCollector(config_manager=cfg, logger=log, ui_manager=None)

    class DirtySource(BaseSource):
        def get_display_name(self) -> str:
            return "Dirty"

        def get_base_url(self) -> str:
            return "https://dirty.example"

        def collect_events(self, target_date: datetime | None = None):  # pragma: no cover
            return []

        def cleanup(self):
            raise RuntimeError("cannot clean")

    assert dc.add_source(OkSource, priority=80)
    # Injeta o DirtySource manualmente para acionar cleanup com erro
    dc.active_sources.append(DirtySource(config_manager=cfg, logger=log, ui_manager=None))

    with dc as ctx:
        assert ctx is dc

    # Erro de cleanup logado via debug
    assert any("Error cleaning up source" in m for m in log.debug_calls)


def test_add_source_respects_excluded_and_remove_unknown():
    cfg = SimpleConfig(excluded=["tomada_tempo"])  # default
    log = DummyLogger()
    dc = DataCollector(config_manager=cfg, logger=log, ui_manager=None)

    # Bloqueia por exclusão
    dc.excluded_sources.add("ok")  # OkSource -> "ok"
    assert dc.add_source(OkSource, priority=10) is False

    # Remoção inexistente retorna False
    assert dc.remove_source("does-not-exist") is False


def test_str_and_repr_have_expected_info():
    dc = DataCollector(config_manager=SimpleConfig(excluded=["tomada_tempo"]), logger=None, ui_manager=None)
    assert dc.add_source(OkSource, priority=80)

    s = str(dc)
    r = repr(dc)
    assert "DataCollector(" in s
    assert "ok" in r
