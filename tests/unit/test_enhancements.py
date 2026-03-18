from __future__ import annotations

import unittest.mock as mock

from warera._batch import BatchSession
from warera.client import WareraClient
from warera.models.common import CursorPage, WareraModel
from warera.models.user import User


def test_warera_model_str():
    user = User(_id="123", username="testuser")
    assert str(user) == "<User testuser>"

    # Test fallback to ID
    class SimpleModel(WareraModel):
        pass

    m = SimpleModel(_id="999")
    assert str(m) == "<SimpleModel 999>"


def test_cursor_page_iter_and_len():
    items = [User(_id=str(i), username=f"u{i}") for i in range(3)]
    page = CursorPage(items=items, has_more=False)

    assert len(page) == 3
    collected = list(page)
    assert len(collected) == 3
    assert collected[0].username == "u0"


def test_base_resource_str():
    # BaseResource is usually instantiated for a namespace
    client = WareraClient(api_key="test")
    assert str(client.user) == "<UserResource>"


def test_warera_client_str():
    client = WareraClient(api_key="test")
    assert "WareraClient(authenticated=True" in str(client)


def test_batch_str():
    http = mock.MagicMock()
    session = BatchSession(http)
    item = session.add("user.get", {"userId": "1"})

    assert str(session) == "<BatchSession queued=1>"
    assert len(session) == 1
    assert str(item) == "<BatchItem user.get (pending)>"

    item._resolve({"id": "1"})
    assert str(item) == "<BatchItem user.get (resolved)>"
