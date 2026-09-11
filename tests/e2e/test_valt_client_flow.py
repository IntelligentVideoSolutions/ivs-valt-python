from __future__ import annotations

ROOM = 3


def test_full_recording_lifecycle_against_fake_server(valt_client, fake_valt_server):
    client = valt_client

    login = fake_valt_server.last_request("login")
    assert login["method"] == "POST"
    assert login["json"] == {"username": "tester", "password": "s3cret"}
    assert client.connected is True
    assert client.accesstoken == "test-access-token"
    assert client.version == "6.5.1"
    assert fake_valt_server.requests_for("admin/general")

    fake_valt_server.reset_requests()

    rooms = [{"id": 3, "name": "Exam 1"}, {"id": 4, "name": "Exam 2"}]
    fake_valt_server.set_route("rooms/info", {"data": {"rooms": rooms}})
    assert client.get_rooms() == rooms

    fake_valt_server.set_route(f"rooms/{ROOM}/status", {"data": {"status": "available"}})
    assert client.get_room_status(ROOM) == 1

    fake_valt_server.set_route(f"rooms/info/{ROOM}", {"data": {"name": "Exam 1", "has_recording": False}})
    fake_valt_server.set_route(f"rooms/{ROOM}/record/start", {"data": {"id": 4242}})
    assert client.start_recording(ROOM, "Clinical Skills Check") == 4242

    fake_valt_server.set_route(
        f"rooms/info/{ROOM}",
        {"data": {"name": "Exam 1", "has_recording": True, "recording": {"id": 4242, "time": 61}}},
    )
    fake_valt_server.set_route(f"rooms/{ROOM}/status", {"data": {"status": "recording"}})
    assert client.get_room_status(ROOM) == 2
    assert client.is_recording(ROOM) is True
    assert client.get_recording_id(ROOM) == 4242
    assert client.get_recording_time(ROOM) == 61

    fake_valt_server.set_route(f"rooms/{ROOM}/record/stop", {"data": {"id": 4242}})
    assert client.stop_recording(ROOM) == 4242

    fake_valt_server.set_route(
        "records",
        {"data": [{"id": 4242, "name": "Clinical Skills Check", "room": "Exam 1"}]},
    )
    records = client.get_records(search="Clinical Skills Check")
    assert records[0]["id"] == 4242

    start_request = fake_valt_server.last_request(f"rooms/{ROOM}/record/start")
    assert start_request["method"] == "POST"
    assert start_request["json"] == {"name": "Clinical Skills Check"}
    assert start_request["query"]["access_token"] == "test-access-token"

    stop_request = fake_valt_server.last_request(f"rooms/{ROOM}/record/stop")
    assert stop_request["method"] == "POST"
    assert stop_request["json"] == {"nothing": "nothing"}

    search_request = fake_valt_server.last_request("records")
    assert search_request["method"] == "POST"
    assert search_request["json"] == {"search": "Clinical Skills Check"}

    observed = [(r["method"], r["path"]) for r in fake_valt_server.requests]
    assert ("GET", "rooms/info") in observed
    assert observed.index(("POST", f"rooms/{ROOM}/record/start")) < observed.index(
        ("POST", f"rooms/{ROOM}/record/stop")
    )
    assert all(r["query"].get("access_token") == "test-access-token" for r in fake_valt_server.requests)


def test_failed_login_leaves_client_disconnected(fake_valt_server, tmp_path):
    from unittest import mock

    from valt.valt import VALT

    fake_valt_server.set_route("login", {"error": "Unauthorized"}, status=401)

    with mock.patch("valt.mixins.auth.threading.Timer"), \
            mock.patch("valt.mixins.monitor.threading.Thread"):
        client = VALT(
            fake_valt_server.address,
            "tester",
            "wrong-password",
            timeout=5,
            logpath=str(tmp_path / "valt-test.log"),
        )
        try:
            assert client.connected is False
            assert client.accesstoken == 0
            assert client.errormsg == "Invalid Username or Password"
            assert client.get_rooms() == 0
        finally:
            client.disconnect()
