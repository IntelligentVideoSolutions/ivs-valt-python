from __future__ import annotations

import pytest

RECORD = 512


@pytest.fixture
def client(valt_client, fake_valt_server):
    fake_valt_server.reset_requests()
    return valt_client


def test_cut_record_posts_time_range(client, fake_valt_server):
    fake_valt_server.set_route(
        f"records/{RECORD}/cut",
        {"data": {"clip_id": 900, "message": "Cut started"}},
    )

    assert client.cut_record(RECORD, 10, 45) == {"clip_id": 900, "message": "Cut started"}

    request = fake_valt_server.last_request(f"records/{RECORD}/cut")
    assert request["method"] == "POST"
    assert request["json"] == {"start_time": 10, "end_time": 45}
    assert request["query"]["access_token"] == client.accesstoken


def test_cut_record_failure_returns_zero(client, fake_valt_server):
    assert client.cut_record(RECORD, 10, 45) == 0
    assert client.errormsg is not None


def test_get_cut_status_returns_status_flag(client, fake_valt_server):
    fake_valt_server.set_route(f"records/900/cut/status", {"data": {"status": True}})

    assert client.get_cut_status(900) is True
    assert fake_valt_server.last_request("records/900/cut/status")["method"] == "GET"


def test_get_cut_status_defaults_to_false_when_absent(client, fake_valt_server):
    fake_valt_server.set_route("records/900/cut/status", {"data": {}})

    assert client.get_cut_status(900) is False


def test_delete_record_posts_to_delete_endpoint(client, fake_valt_server):
    fake_valt_server.set_route(f"records/{RECORD}/delete", {"data": {"id": RECORD}})

    assert client.delete_record(RECORD) == 1

    request = fake_valt_server.last_request(f"records/{RECORD}/delete")
    assert request["method"] == "POST"
    assert request["json"] == {}


def test_share_record_returns_url(client, fake_valt_server):
    share_url = "https://valt.test/share/abc123"
    fake_valt_server.set_route(f"records/{RECORD}/share", {"data": {"url": share_url}})

    assert client.share_record(RECORD) == share_url
    assert fake_valt_server.last_request(f"records/{RECORD}/share")["method"] == "POST"


def test_deactivate_share_returns_one(client, fake_valt_server):
    fake_valt_server.set_route(f"records/{RECORD}/share/deactivate", {"data": {"id": RECORD}})

    assert client.deactivate_share(RECORD) == 1


def test_get_records_posts_search_criteria(client, fake_valt_server):
    records = [{"id": RECORD, "name": "Intake Session"}]
    fake_valt_server.set_route("records", {"data": records})

    assert client.get_records(search="Intake") == records

    request = fake_valt_server.last_request("records")
    assert request["method"] == "POST"
    assert request["json"] == {"search": "Intake"}


def test_get_records_without_criteria_does_not_call_server(client, fake_valt_server):
    assert client.get_records() == 0
    assert fake_valt_server.requests == []


def test_record_calls_short_circuit_when_disconnected(client, fake_valt_server):
    client.accesstoken = 0
    fake_valt_server.reset_requests()

    assert client.share_record(RECORD) == 0
    assert fake_valt_server.requests == []
