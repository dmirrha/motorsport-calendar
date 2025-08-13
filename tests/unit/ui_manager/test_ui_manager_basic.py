import types
import time
import builtins

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


class FakeProgress:
    def __init__(self, *args, **kwargs):
        self.tasks = {}
        self.updated = []
        self.stopped = False

    def add_task(self, description, total=None):
        # Return a deterministic task id
        tid = len(self.tasks) + 1
        self.tasks[tid] = {"description": description, "total": total, "advance": 0}
        return tid

    def update(self, task_id, advance=0, description=None):
        # record updates and mutate internal state
        self.updated.append({"task_id": task_id, "advance": advance, "description": description})
        if task_id in self.tasks:
            self.tasks[task_id]["advance"] = self.tasks[task_id].get("advance", 0) + (advance or 0)
            if description is not None:
                self.tasks[task_id]["description"] = description

    def stop(self):
        self.stopped = True


@pytest.fixture
def fake_console():
    return FakeConsole()


@pytest.fixture
def patched_progress(monkeypatch):
    monkeypatch.setattr(ui_mod, "Progress", FakeProgress)
    return FakeProgress


def test_disabled_ui_no_ops(fake_console):
    ui = UIManager()
    ui.console = fake_console
    ui.enabled = False

    # Should early-return and not print
    ui.show_banner()
    assert len(fake_console.print_calls) == 0

    tid = ui.create_progress_bar("task", total=10)
    assert tid is None

    # update_progress should not fail or call anything
    ui.update_progress("task", advance=5)
    assert len(fake_console.print_calls) == 0

    # show_final_summary should not print
    ui.show_final_summary(events_collected=10)
    assert len(fake_console.print_calls) == 0

    # pause should not sleep when disabled
    called = {"slept": False}
    def _sleep(_):
        called["slept"] = True
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(time, "sleep", _sleep)
        ui.pause(0.01)
    finally:
        monkeypatch.undo()
    assert called["slept"] is False


def test_progress_create_update_and_close(fake_console, patched_progress, monkeypatch):
    ui = UIManager()
    ui.console = fake_console

    # create progress bar
    tid1 = ui.create_progress_bar("collect", total=100)
    assert isinstance(tid1, int)
    # same task name should reuse same id
    tid2 = ui.create_progress_bar("collect", total=100)
    assert tid2 == tid1

    # update progress without description
    ui.update_progress("collect", advance=10)
    # update progress with description
    ui.update_progress("collect", advance=5, description="phase 1")

    # inspect FakeProgress state
    progress = ui.progress_tasks["collect"]["progress"]
    assert progress.tasks[tid1]["advance"] == 15
    assert progress.tasks[tid1]["description"] == "phase 1"

    # close should stop and clear
    ui.close_progress_bars()
    assert progress.stopped is True
    assert ui.progress_tasks == {}


def test_separator_clear_and_pause(fake_console, monkeypatch):
    ui = UIManager()
    ui.console = fake_console

    # print_separator prints a line of separators
    ui.print_separator()
    assert len(fake_console.print_calls) >= 1
    last_args, last_kwargs = fake_console.print_calls[-1]
    assert isinstance(last_args[0], str)
    assert len(last_args[0]) == 80  # 80 characters line

    # clear_screen should call console.clear
    ui.clear_screen()
    assert fake_console.clear_calls == 1

    # pause should call time.sleep when enabled
    called = {"slept": 0}
    def _sleep(sec):
        called["slept"] += 1
        called["sec"] = sec
    monkeypatch.setattr(time, "sleep", _sleep)
    ui.pause(0.02)
    assert called["slept"] == 1
    assert abs(called["sec"] - 0.02) < 1e-9


def test_show_final_summary_prints(fake_console):
    ui = UIManager()
    ui.console = fake_console

    before = len(fake_console.print_calls)
    ui.show_final_summary(sources_successful=2, sources_total=3, events_collected=42, execution_time=1.23)
    after = len(fake_console.print_calls)
    # three prints: blank line, table, blank line
    assert after - before == 3


def test_show_source_result_success_and_error(fake_console):
    ui = UIManager()
    ui.console = fake_console

    ui.show_source_result("SRC", success=True, event_count=5)
    ui.show_source_result("SRC2", success=False, error_message="timeout")

    # two print calls expected
    assert len(fake_console.print_calls) == 2
    # the first contains a string with the source name
    first_args, _ = fake_console.print_calls[0]
    second_args, _ = fake_console.print_calls[1]
    assert "SRC" in str(first_args[0])
    assert "SRC2" in str(second_args[0])
