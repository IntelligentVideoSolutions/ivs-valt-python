from __future__ import annotations

from unittest import mock

import pytest

from valt.mixins.upload import _UPLOAD_VERIFY_DELAYS_SECONDS

RECORD = "1bc87bea-0000-4000-8000-000000000001"
VIDEO = "198016d2-0000-4000-8000-000000000002"
CREATE = "records/create-upload"
UPLOAD = f"records/{RECORD}/videos/{VIDEO}"
INFO = f"records/{RECORD}"


@pytest.fixture
def client(valt_client, fake_valt_server):
    fake_valt_server.reset_requests()
    return valt_client


@pytest.fixture
def sleeps():
    # upload_video() waits up to ~48s in total between verification attempts.
    with mock.patch("valt.mixins.upload.time.sleep") as sleep:
        yield sleep


@pytest.fixture
def video_file(tmp_path):
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"not really an mp4")
    return path


def _install_upload_routes(server, info_videos):
    # create-upload returns its payload at the top level (no "data" wrapper), and the
    # file POST answers with an empty body, per the VALT record upload docs.
    server.set_route(CREATE, {"id": RECORD, "videos": [VIDEO]})
    server.set_route(UPLOAD, status=201, raw=b"")
    server.set_route(INFO, lambda request: {"data": {"id": RECORD, "videos": info_videos()}})


def _video(status_type):
    return [{"id": VIDEO, "status": {"type": status_type}}]


def test_upload_returns_record_id_when_video_is_ready(client, fake_valt_server, sleeps, video_file):
    _install_upload_routes(fake_valt_server, lambda: _video("ready"))

    assert client.upload_video(str(video_file), "Lecture 1") == RECORD

    create = fake_valt_server.last_request(CREATE)
    assert create["method"] == "POST"
    assert create["json"] == {"name": "Lecture 1"}
    upload = fake_valt_server.last_request(UPLOAD)
    assert upload["method"] == "POST"
    assert upload["headers"]["Content-Type"].startswith("multipart/form-data")
    assert b"not really an mp4" in upload["body"]
    assert len(fake_valt_server.requests_for(INFO)) == 1
    sleeps.assert_not_called()


def test_upload_keeps_polling_while_video_is_still_processing(client, fake_valt_server, sleeps, video_file):
    states = iter(["created", "created", "ready"])
    _install_upload_routes(fake_valt_server, lambda: _video(next(states)))

    assert client.upload_video(str(video_file), "Lecture 1") == RECORD

    assert len(fake_valt_server.requests_for(INFO)) == 3
    assert [c.args[0] for c in sleeps.call_args_list] == list(_UPLOAD_VERIFY_DELAYS_SECONDS[:2])


def test_upload_fails_when_file_never_lands(client, fake_valt_server, sleeps, video_file):
    # A record whose file was never actually uploaded reports "videos": null.
    _install_upload_routes(fake_valt_server, lambda: None)

    assert client.upload_video(str(video_file), "Lecture 1") == 0

    assert client.errormsg == "Upload Could Not Be Verified"
    assert len(fake_valt_server.requests_for(INFO)) == len(_UPLOAD_VERIFY_DELAYS_SECONDS) + 1
    assert [c.args[0] for c in sleeps.call_args_list] == list(_UPLOAD_VERIFY_DELAYS_SECONDS)
    # A failed verification is not an auth problem, so the session must survive it.
    assert client.connected


def test_upload_fails_when_video_never_finishes_processing(client, fake_valt_server, sleeps, video_file):
    _install_upload_routes(fake_valt_server, lambda: _video("created"))

    assert client.upload_video(str(video_file), "Lecture 1") == 0
    assert client.errormsg == "Upload Could Not Be Verified"


def test_upload_fails_when_create_upload_returns_no_video_slot(client, fake_valt_server, sleeps, video_file):
    fake_valt_server.set_route(CREATE, {"id": RECORD, "videos": []})

    assert client.upload_video(str(video_file), "Lecture 1") == 0

    assert client.errormsg == "Upload Failed"
    assert fake_valt_server.requests_for(UPLOAD) == []
    assert fake_valt_server.requests_for(INFO) == []


def test_upload_fails_when_file_is_missing(client, fake_valt_server, sleeps, tmp_path):
    assert client.upload_video(str(tmp_path / "missing.mp4"), "Lecture 1") == 0

    assert client.errormsg == "File Not Found"
    assert fake_valt_server.requests == []


def test_upload_refuses_when_not_authenticated(client, fake_valt_server, sleeps, video_file):
    client.accesstoken = 0

    assert client.upload_video(str(video_file), "Lecture 1") == 0
    assert fake_valt_server.requests == []
