from __future__ import annotations

import os
import time

import pytest

from valt.valt import VALT

pytestmark = pytest.mark.live


def _required_env():
    host = os.environ.get("VALT_LIVE_HOST")
    user = os.environ.get("VALT_LIVE_USER")
    password = os.environ.get("VALT_LIVE_PASSWORD")
    missing = [
        name
        for name, value in (
            ("VALT_LIVE_HOST", host),
            ("VALT_LIVE_USER", user),
            ("VALT_LIVE_PASSWORD", password),
        )
        if not value
    ]
    if missing:
        pytest.skip("Live VALT server not configured; missing: " + ", ".join(missing))
    return host, user, password


def _live_room():
    room = os.environ.get("VALT_LIVE_ROOM")
    if not room:
        pytest.skip("VALT_LIVE_ROOM not set; skipping room-control smoke test")
    return int(room)


@pytest.fixture(scope="module")
def live_client():
    host, user, password = _required_env()
    client = VALT(host, user, password, timeout=int(os.environ.get("VALT_LIVE_TIMEOUT", "15")))
    try:
        yield client
    finally:
        client.disconnect()


def test_authenticates(live_client):
    assert live_client.connected is True
    assert live_client.accesstoken != 0


def test_reports_server_version(live_client):
    version = live_client.get_version()
    assert version not in (0, "0.0.0")
    assert live_client.major_version in ("5", "6")


def test_lists_rooms(live_client):
    rooms = live_client.get_rooms()
    assert isinstance(rooms, list)
    assert rooms


def test_room_status_is_known(live_client):
    room = _live_room()
    status = live_client.get_room_status(room)
    assert status in (1, 2, 3, 4, 5)


def test_room_name_is_returned(live_client):
    room = _live_room()
    assert isinstance(live_client.get_room_name(room), str)


def test_recording_start_and_stop(live_client):
    room = _live_room()
    if live_client.is_recording(room) is not False:
        pytest.skip(f"Room {room} is not idle; refusing to disturb an active recording")

    name = f"pytest-live-smoke-{int(time.time())}"
    record_id = live_client.start_recording(room, name)
    assert record_id != 0
    try:
        assert live_client.is_recording(room) is True
        assert live_client.get_recording_id(room) == record_id
    finally:
        assert live_client.stop_recording(room) != 0

    assert live_client.is_recording(room) is False


def test_search_records(live_client):
    records = live_client.get_records(search="pytest-live-smoke")
    assert records == 0 or isinstance(records, list)
