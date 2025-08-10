import requests
import pytest
from datetime import datetime

from sources.base_source import BaseSource


class _LoggerStub:
    def __init__(self):
        self.saved_payloads = []
        self.errors = []
        self.debugs = []

    def debug(self, msg):
        self.debugs.append(msg)

    def save_payload(self, **kwargs):
        self.saved_payloads.append(kwargs)

    def log_source_error(self, source, message):
        self.errors.append((source, message))


class _DummySource(BaseSource):
    def get_display_name(self) -> str:
        return "Dummy"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: datetime | None = None):  # not used here
        return []


@pytest.mark.unit
def test_make_request_success(patch_requests_session, dummy_response):
    logger = _LoggerStub()

    resp = dummy_response(text="ok", status_code=200)
    setattr(resp, "headers", {})

    # Patch antes de instanciar a fonte (BaseSource cria Session no __init__)
    sess = patch_requests_session(response_or_callable=lambda url, **kw: resp)
    # BaseSource.make_request usa self.session.request(method, url, **kwargs)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    # BaseSource._setup_session exige headers e mount
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is resp
    assert src.stats["requests_made"] >= 1
    assert src.stats["successful_requests"] >= 1
    # save_payload chamado
    assert logger.saved_payloads, "payload não foi salvo via logger.save_payload"


@pytest.mark.unit
def test_make_request_timeout(patch_requests_session):
    logger = _LoggerStub()

    sess = patch_requests_session(exception_to_raise=requests.Timeout())
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is None
    assert src.stats["failed_requests"] == 1
    # deve registrar erros por tentativa
    assert len(src.stats["errors"]) == src.retry_attempts
    assert logger.errors, "log_source_error não foi chamado no erro final"


@pytest.mark.unit
def test_make_request_http_error(patch_requests_session, dummy_response):
    logger = _LoggerStub()

    bad = dummy_response(text="", status_code=500)
    setattr(bad, "headers", {})

    sess = patch_requests_session(response_or_callable=lambda url, **kw: bad)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is None
    assert src.stats["failed_requests"] == 1
    assert len(src.stats["errors"]) == src.retry_attempts
    assert logger.errors, "log_source_error não foi chamado"
