from __future__ import annotations

import pytest


@pytest.fixture
def client(valt_client, fake_valt_server):
    fake_valt_server.reset_requests()
    return valt_client


def test_get_users_returns_user_list(client, fake_valt_server):
    users = [{"id": 1, "name": "admin"}, {"id": 2, "name": "clinician"}]
    fake_valt_server.set_route("admin/users", {"data": users})

    assert client.get_users() == users

    request = fake_valt_server.last_request("admin/users")
    assert request["method"] == "GET"
    assert request["query"]["access_token"] == client.accesstoken


def test_get_users_handles_empty_response(client, fake_valt_server):
    fake_valt_server.set_route("admin/users", {"error": "boom"}, status=500)

    assert client.get_users() == 0


def test_get_user_returns_user_dict(client, fake_valt_server):
    user = {"id": 5, "name": "clinician", "display_name": "Dr. Smith"}
    fake_valt_server.set_route("admin/users/5", {"data": user})

    assert client.get_user(5) == user
    assert fake_valt_server.last_request("admin/users/5")["method"] == "GET"


def test_create_user_posts_payload_and_returns_id(client, fake_valt_server):
    fake_valt_server.set_route("admin/users", {"data": {"id": 91}})

    assert client.create_user("newuser", "pw123", display_name="New User", user_group=4) == 91

    request = fake_valt_server.last_request("admin/users")
    assert request["method"] == "POST"
    assert request["json"] == {
        "name": "newuser",
        "password": "pw123",
        "display_name": "New User",
        "user_group": 4,
    }


def test_create_user_ignores_unknown_kwargs(client, fake_valt_server):
    fake_valt_server.set_route("admin/users", {"data": {"id": 92}})

    client.create_user("newuser", "pw123", nonsense="dropped")

    assert fake_valt_server.last_request("admin/users")["json"] == {"name": "newuser", "password": "pw123"}


def test_update_user_posts_to_edit_endpoint(client, fake_valt_server):
    fake_valt_server.set_route("admin/users/5/edit", {"data": {"id": 5, "display_name": "Renamed"}})

    assert client.update_user(5, display_name="Renamed") == {"id": 5, "display_name": "Renamed"}

    request = fake_valt_server.last_request("admin/users/5/edit")
    assert request["method"] == "POST"
    assert request["json"] == {"display_name": "Renamed"}


def test_delete_user_returns_one_on_success(client, fake_valt_server):
    fake_valt_server.set_route("admin/users/5/delete", {"data": {"id": 5}})

    assert client.delete_user(5) == 1

    request = fake_valt_server.last_request("admin/users/5/delete")
    assert request["method"] == "POST"
    assert request["json"] == {}


def test_get_user_by_card_number_uses_v6_query(client, fake_valt_server):
    assert client.major_version == "6"
    fake_valt_server.set_route("admin/users", {"data": [{"id": 33, "card_number": "ABC123"}]})

    assert client.get_user_by_card_number("ABC123") == 33

    request = fake_valt_server.last_request("admin/users")
    assert request["query"]["cardNumber"] == "ABC123"


def test_get_user_by_card_number_v5_scans_user_list(client, fake_valt_server):
    fake_valt_server.set_route(
        "admin/users",
        {"data": [{"id": 1, "card_number": "AAA"}, {"id": 2, "card_number": "BBB"}]},
    )

    assert client.get_user_by_card_number_v5("BBB") == 2
    assert client.get_user_by_card_number_v5("ZZZ") == 0
