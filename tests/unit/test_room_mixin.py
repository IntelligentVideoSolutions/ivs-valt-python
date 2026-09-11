from __future__ import annotations

import pytest

ROOM = 3


@pytest.fixture
def client(valt_client, fake_valt_server):
    fake_valt_server.reset_requests()
    return valt_client


def test_is_recording_reads_room_info(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": True}})

    assert client.is_recording(ROOM) is True

    request = fake_valt_server.last_request(f"rooms/info/{ROOM}")
    assert request["method"] == "GET"
    assert request["query"]["access_token"] == client.accesstoken


def test_get_room_status_maps_status_strings(client, fake_valt_server):
    for status, expected in (
        ("available", 1),
        ("recording", 2),
        ("paused", 3),
        ("locked", 4),
        ("prepared", 5),
    ):
        fake_valt_server.set_route(f"rooms/{ROOM}/status", {"data": {"status": status}})
        assert client.get_room_status(ROOM) == expected


def test_get_room_status_handles_unknown_status(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/{ROOM}/status", {"data": {"status": "melted"}})

    assert client.get_room_status(ROOM) == 0
    assert client.errormsg == "Room Status Unknown"


def test_start_recording_posts_name_and_returns_id(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": False}})
    fake_valt_server.set_route(f"rooms/{ROOM}/record/start", {"data": {"id": 4242}})

    assert client.start_recording(ROOM, "Intake Session") == 4242

    request = fake_valt_server.last_request(f"rooms/{ROOM}/record/start")
    assert request["method"] == "POST"
    assert request["json"] == {"name": "Intake Session"}
    assert request["headers"]["Content-Type"] == "application/json"


def test_start_recording_includes_author_when_given(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": False}})
    fake_valt_server.set_route(f"rooms/{ROOM}/record/start", {"data": {"id": 7}})
    fake_valt_server.set_route("admin/users/11", {"data": {"id": 11, "name": "clinician"}})

    assert client.start_recording(ROOM, "Intake", author=11) == 7

    assert fake_valt_server.last_request(f"rooms/{ROOM}/record/start")["json"] == {
        "name": "Intake",
        "author": 11,
    }


def test_start_recording_refuses_when_already_recording(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": True}})

    assert client.start_recording(ROOM, "Duplicate") == 0
    assert client.errormsg == "Unable to Start Recording in a Room that is Already Recording"
    assert fake_valt_server.requests_for(f"rooms/{ROOM}/record/start") == []


def test_stop_recording_posts_and_returns_id(client, fake_valt_server):
    fake_valt_server.set_route(
        f"rooms/info/{ROOM}",
        {"data": {"name": "Exam 1", "has_recording": True, "recording": {"id": 4242, "time": 30}}},
    )
    fake_valt_server.set_route(f"rooms/{ROOM}/record/stop", {"data": {"id": 4242}})

    assert client.stop_recording(ROOM) == 4242

    request = fake_valt_server.last_request(f"rooms/{ROOM}/record/stop")
    assert request["method"] == "POST"
    assert request["json"] == {"nothing": "nothing"}


def test_stop_recording_without_active_recording(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": False}})

    assert client.stop_recording(ROOM) == 0
    assert client.errormsg == "Room is Not Currently Recording"


def test_get_room_name_returns_name(client, fake_valt_server):
    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Simulation Suite"}})

    assert client.get_room_name(ROOM) == "Simulation Suite"


def test_get_cameras_returns_camera_list(client, fake_valt_server):
    cameras = [{"id": 1, "name": "Cam A"}, {"id": 2, "name": "Cam B"}]
    fake_valt_server.set_route(f"admin/rooms/{ROOM}/cameras", {"data": {"cameras": cameras}})

    assert client.get_cameras(ROOM) == cameras


def test_room_calls_short_circuit_when_disconnected(client, fake_valt_server):
    client.accesstoken = 0
    fake_valt_server.reset_requests()

    assert client.get_room_status(ROOM) == 0
    assert fake_valt_server.requests == []
