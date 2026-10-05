from __future__ import annotations

import io
import json
from unittest import mock
from urllib import error

import pytest

from valt.mixins.communication import ValtCommunication


class FakeResponse(io.BytesIO):
    def __init__(self, payload=b'{"data": {"ok": true}}', code=200, content_type="application/json"):
        super().__init__(payload)
        self._code = code
        self._content_type = content_type

    def getcode(self):
        return self._code

    def info(self):
        return {"Content-Type": self._content_type}


class CommunicationHarness(ValtCommunication):
    def __init__(self):
        self.logger = mock.MagicMock()
        self.httptimeout = 7
        self.handled_errors = []

    def handle_error(self, e):
        self.handled_errors.append(e)


@pytest.fixture
def comm():
    return CommunicationHarness()


@pytest.fixture
def urlopen():
    with mock.patch("valt.mixins.communication.request.urlopen") as patched:
        patched.return_value = FakeResponse()
        yield patched


def test_get_request_uses_url_and_timeout(comm, urlopen):
    result = comm.send_to_valt("http://valt.test/api/v3/rooms/info")

    assert result == {"data": {"ok": True}}
    req = urlopen.call_args.args[0]
    assert req.get_full_url() == "http://valt.test/api/v3/rooms/info"
    assert req.get_method() == "GET"
    assert req.data is None
    assert urlopen.call_args.kwargs["timeout"] == 7
    assert "context" in urlopen.call_args.kwargs


def test_explicit_method_is_passed_through(comm, urlopen):
    comm.send_to_valt("http://valt.test/api/v3/records/9", method="DELETE")

    req = urlopen.call_args.args[0]
    assert req.get_method() == "DELETE"


def test_json_body_is_encoded_and_content_type_set(comm, urlopen):
    values = {"username": "tester", "password": "s3cret"}

    comm.send_to_valt("http://valt.test/api/v3/login", values=values)

    req, params = urlopen.call_args.args[0], urlopen.call_args.args[1]
    assert json.loads(params.decode()) == values
    assert req.get_header("Content-type") == "application/json"
    assert urlopen.call_args.kwargs["timeout"] == 7


def test_multipart_body_for_file_upload(comm, urlopen, tmp_path):
    upload = tmp_path / "clip.mp4"
    upload.write_bytes(b"binary-video-bytes")

    comm.send_to_valt("http://valt.test/api/v3/upload", file_path=str(upload))

    req = urlopen.call_args.args[0]
    assert req.get_method() == "POST"
    content_type = req.get_header("Content-type")
    assert content_type.startswith("multipart/form-data; boundary=")
    boundary = content_type.split("boundary=")[1]
    assert req.get_header("Content-range") == "bytes 0-17/18"
    body = req.data
    assert body.startswith(f"--{boundary}".encode())
    assert b'Content-Disposition: form-data; name="file"; filename="clip.mp4"' in body
    assert b"Content-Type: application/octet-stream" in body
    assert b"binary-video-bytes" in body
    assert body.endswith(f"\r\n--{boundary}--\r\n".encode())
    # Uploads intentionally run without a timeout, so it must not inherit httptimeout.
    assert urlopen.call_args.kwargs["timeout"] is None


def test_missing_file_path_falls_back_to_plain_request(comm, urlopen, tmp_path):
    comm.send_to_valt("http://valt.test/api/v3/upload", file_path=str(tmp_path / "absent.mp4"))

    req = urlopen.call_args.args[0]
    assert req.get_method() == "GET"
    assert req.get_header("Content-range") is None


def test_http_error_is_routed_to_handle_error(comm, urlopen):
    http_error = error.HTTPError("http://valt.test/api/v3/login", 401, "Unauthorized", {}, None)
    urlopen.side_effect = http_error

    result = comm.send_to_valt("http://valt.test/api/v3/login", values={"username": "x"})

    assert result is None
    assert comm.handled_errors == [http_error]


def test_url_error_is_routed_to_handle_error(comm, urlopen):
    url_error = error.URLError("timed out")
    urlopen.side_effect = url_error

    result = comm.send_to_valt("http://valt.test/api/v3/rooms/info")

    assert result is None
    assert comm.handled_errors == [url_error]


def test_non_json_response_returns_none_without_error_handling(comm, urlopen):
    urlopen.return_value = FakeResponse(payload=b"<html>not json</html>", content_type="text/html")

    result = comm.send_to_valt("http://valt.test/api/v3/rooms/info")

    assert result is None
    assert comm.handled_errors == []
