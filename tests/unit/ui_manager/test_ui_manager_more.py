import os
import time

import pytest

import ui_manager as ui_mod
from ui_manager import UIManager


class FakeConsole:
    def __init__(self):
        self.print_calls = []
        self.clear_calls = 0

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))

    def clear(self):
        self.clear_calls += 1


class DummyConfig:
    def __init__(self, mapping=None):
        self.mapping = mapping or {}

    def get(self, key, default=None):
        return self.mapping.get(key, default)


@pytest.fixture
def fake_console():
    return FakeConsole()


def test_show_config_summary_truncates_and_prints(fake_console):
    ui = UIManager()
    ui.console = fake_console

    cfg = {
        "sources": ["a", "b", "c", "d", "e"],
        "mode": "fast",
    }
    before = len(fake_console.print_calls)
    ui.show_config_summary(cfg)
    after = len(fake_console.print_calls)
    # prints table + blank line
    assert after - before == 2


def test_show_weekend_detection(fake_console):
    ui = UIManager()
    ui.console = fake_console

    data = {"start_date": "2025-08-01", "end_date": "2025-08-03", "total_events": 12}
    before = len(fake_console.print_calls)
    ui.show_weekend_detection(data)
    after = len(fake_console.print_calls)
    assert after - before == 1


def test_show_event_summary(fake_console):
    ui = UIManager()
    ui.console = fake_console

    events = [
        {"name": "Race A", "date": "2025-08-01", "location": "Track 1"},
        {"name": "Race B"},  # missing optional fields
    ]
    before = len(fake_console.print_calls)
    ui.show_event_summary(events)
    after = len(fake_console.print_calls)
    # show_event_summary imprime a tabela e uma linha em branco => 2 prints
    assert after - before == 2


def test_show_events_by_category(fake_console):
    ui = UIManager()
    ui.console = fake_console

    by_cat = {
        "F1": [{"name": "FP1"}, {"name": "Race"}],
        "MotoGP": [{"name": "Race"}],
    }
    before = len(fake_console.print_calls)
    ui.show_events_by_category(by_cat)
    after = len(fake_console.print_calls)
    # One header per category at minimum
    assert after - before >= 2


def test_step_progress_and_show_step(fake_console):
    ui = UIManager()
    ui.console = fake_console

    ui.start_step_progress(total_steps=3)
    ui.show_step("Download")
    ui.show_step("Parse", description="HTML")

    assert ui.total_steps == 3
    assert ui.current_step == 2
    assert len(fake_console.print_calls) >= 2


def test_success_error_warning_and_step_result(fake_console):
    ui = UIManager()
    ui.console = fake_console

    ui.show_success_message("ok")
    ui.show_error_message("fail")
    ui.show_warning_message("warn")
    ui.show_step_result("Collect", success=True, message="done")
    ui.show_step_result("Collect", success=False, message="timeout")

    # total 5 print calls
    assert len(fake_console.print_calls) == 5


def test_ical_generation_and_import_instructions(fake_console, monkeypatch):
    ui = UIManager()
    ui.console = fake_console

    # iCal generation panel
    ui.show_ical_generation("/tmp/events.ics", event_count=42)

    # import instructions prints multiple lines (expected 12)
    monkeypatch.setenv("TZ", "America/Sao_Paulo")
    before = len(fake_console.print_calls)
    ui.show_import_instructions("/tmp/events.ics")
    after = len(fake_console.print_calls)

    assert after - before == 12


def test_show_banner_prints_three_lines(fake_console):
    ui = UIManager()
    ui.console = fake_console

    before = len(fake_console.print_calls)
    ui.show_banner()
    after = len(fake_console.print_calls)
    # three prints: blank, panel, blank
    assert after - before == 3


def test_disabled_early_returns_for_multiple_methods(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False

    # Should all early-return without printing
    ui.show_config_summary({"a": 1})
    ui.show_step("X")
    ui.show_source_collection_start(["S1"])
    ui.show_source_result("SRC", success=True)
    ui.show_category_detection_results({"cat": {"type": "cars", "event_count": 1, "confidence": 0.9, "sources": ["s1"]}})
    ui.show_weekend_detection({"start_date": "2025-01-01", "end_date": "2025-01-03", "total_events": 0})
    ui.show_event_summary([{"name": "e"}])
    ui.show_ical_generation("/tmp/a.ics", 1)
    ui.show_error_message("err")
    ui.show_step_result("Step", True)
    ui.show_warning_message("warn")
    ui.show_final_summary(anything=1)
    ui.show_events_by_category({"Cat": [{"name": "E"}]})
    ui.show_import_instructions("/tmp/a.ics")

    assert len(fake_console.print_calls) == 0


def test_show_source_collection_start_prints_table(fake_console):
    ui = UIManager()
    ui.console = fake_console

    before = len(fake_console.print_calls)
    ui.show_source_collection_start(["A", "B"])
    after = len(fake_console.print_calls)
    assert after - before == 1


def test_show_category_detection_results_body(fake_console):
    ui = UIManager()
    ui.console = fake_console

    cats = {
        "F1": {"type": "cars", "event_count": 10, "confidence": 0.85, "sources": ["src1", "src2", "src3"]},
        "MotoGP": {"type": "motorcycles", "event_count": 5, "confidence": 0.7, "sources": ["m1"]},
    }
    before = len(fake_console.print_calls)
    ui.show_category_detection_results(cats)
    after = len(fake_console.print_calls)
    # prints table and a blank line
    assert after - before == 2

    # empty categories should early-return
    before2 = len(fake_console.print_calls)
    ui.show_category_detection_results({})
    after2 = len(fake_console.print_calls)
    assert after2 - before2 == 0


def test_show_deduplication_results_disabled(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False
    ui.show_deduplication_results(duplicates_removed=1, total_before=2)
    assert len(fake_console.print_calls) == 0


def test_show_completion_summary_disabled(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False
    ui.show_completion_summary({"events": 1})
    assert len(fake_console.print_calls) == 0


def test_event_summary_empty_and_many(fake_console):
    ui = UIManager()
    ui.console = fake_console

    # empty events -> no print
    before = len(fake_console.print_calls)
    ui.show_event_summary([])
    after = len(fake_console.print_calls)
    assert after - before == 0

    # >10 events triggers the ellipsis row branch
    many = [{"name": f"E{i}", "time": "10:00", "category": "C", "location": "Loc"} for i in range(12)]
    before2 = len(fake_console.print_calls)
    ui.show_event_summary(many)
    after2 = len(fake_console.print_calls)
    assert after2 - before2 == 2


def test_deduplication_results_branches(fake_console):
    ui = UIManager()
    ui.console = fake_console

    # duplicates removed branch
    before = len(fake_console.print_calls)
    ui.show_deduplication_results(duplicates_removed=3, total_before=10)
    after = len(fake_console.print_calls)
    assert after - before == 1

    # no duplicates branch
    before2 = len(fake_console.print_calls)
    ui.show_deduplication_results(duplicates_removed=0, total_before=10)
    after2 = len(fake_console.print_calls)
    assert after2 - before2 == 1


def test_ical_generation_disabled_early_return(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False
    ui.show_ical_generation("/tmp/f.ics", 1)
    assert len(fake_console.print_calls) == 0


def test_error_warning_step_result_disabled(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False
    ui.show_error_message("x")
    ui.show_warning_message("y")
    ui.show_step_result("Z", success=True)
    assert len(fake_console.print_calls) == 0


def test_show_final_summary_string_and_disabled(fake_console):
    ui = UIManager()
    ui.console = fake_console

    # includes string value branch for value_str
    before = len(fake_console.print_calls)
    ui.show_final_summary(output_file="/tmp/file.ics", events_collected=1, execution_time=1.0)
    after = len(fake_console.print_calls)
    assert after - before == 3

    # disabled early return
    ui.enabled = False
    before2 = len(fake_console.print_calls)
    ui.show_final_summary(any_value="x")
    after2 = len(fake_console.print_calls)
    assert after2 - before2 == 0


def test_events_by_category_empty_and_with_fields(fake_console):
    ui = UIManager()
    ui.console = fake_console

    # empty -> early return
    before = len(fake_console.print_calls)
    ui.show_events_by_category({})
    after = len(fake_console.print_calls)
    assert after - before == 0

    # with date and location fields to hit branches
    by_cat = {
        "GT": [{"name": "Race", "date": "2025-08-01", "location": "Spa"}],
    }
    before2 = len(fake_console.print_calls)
    ui.show_events_by_category(by_cat)
    after2 = len(fake_console.print_calls)
    assert after2 - before2 >= 2


def test_import_instructions_disabled(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False
    ui.show_import_instructions("/tmp/x.ics")
    assert len(fake_console.print_calls) == 0


def test_close_progress_bars_handles_exception(fake_console):
    ui = UIManager()
    ui.console = fake_console

    class BadProgress:
        def stop(self):
            raise RuntimeError("boom")

    ui.progress_tasks["bad"] = {"progress": BadProgress(), "task_id": 1}
    # should not raise and should clear tasks
    ui.close_progress_bars()
    assert ui.progress_tasks == {}


def test_show_completion_summary_prints(fake_console):
    ui = UIManager()
    ui.console = fake_console

    summary = {"events": 10, "sources": 3}
    before = len(fake_console.print_calls)
    ui.show_completion_summary(summary)
    after = len(fake_console.print_calls)
    # blank, panel, blank
    assert after - before == 3


def test_config_disables_visuals_and_icons(fake_console):
    cfg = DummyConfig({
        "general.visual_interface.enabled": True,
        "general.visual_interface.colors": True,
        "general.visual_interface.icons": False,  # disable icons
    })
    ui = UIManager(config_manager=cfg)
    ui.console = fake_console

    # if icons disabled, methods still print but without icon glyphs
    ui.show_success_message("ok")
    (args, _kwargs) = fake_console.print_calls[-1]
    s = str(args[0])
    assert "✅" not in s  # icon suppressed

    # when disabled entirely, no output
    cfg2 = DummyConfig({"general.visual_interface.enabled": False})
    ui2 = UIManager(config_manager=cfg2)
    ui2.console = fake_console
    before = len(fake_console.print_calls)
    ui2.show_success_message("won't print")
    assert len(fake_console.print_calls) == before
