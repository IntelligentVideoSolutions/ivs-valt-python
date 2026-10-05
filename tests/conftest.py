from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest

API_PREFIX = "/api/v3/"

DEFAULT_ACCESS_TOKEN = "test-access-token"
DEFAULT_VERSION = "6.5.1"


class FakeValtServerState:
    def __init__(self):
        self.routes = {}
        self.requests = []
        self.host = "127.0.0.1"
        self.port = 0

    @property
    def address(self):
        return f"http://{self.host}:{self.port}"

    @staticmethod
    def _normalize(path):
        return path.strip("/")

    def set_route(self, path, body=None, status=200, content_type="application/json", raw=None):
        self.routes[self._normalize(path)] = {
            "body": body,
            "status": status,
            "content_type": content_type,
            "raw": raw,
        }

    def clear_route(self, path):
        self.routes.pop(self._normalize(path), None)

    def get_route(self, path):
        return self.routes.get(self._normalize(path))

    def reset_requests(self):
        self.requests.clear()

    def requests_for(self, path):
        normalized = self._normalize(path)
        return [r for r in self.requests if r["path"] == normalized]

    def last_request(self, path=None):
        candidates = self.requests if path is None else self.requests_for(path)
        return candidates[-1] if candidates else None

    def install_default_routes(self):
        self.set_route("login", {"data": {"access_token": DEFAULT_ACCESS_TOKEN}})
        self.set_route("admin/general", {"data": {"version": DEFAULT_VERSION}})


def _build_handler(state: FakeValtServerState):
    class _Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def _record(self):
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            path = parsed.path
            if path.startswith(API_PREFIX):
                path = path[len(API_PREFIX):]
            try:
                parsed_body = json.loads(body) if body else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed_body = None
            record = {
                "method": self.command,
                "path": path.strip("/"),
                "full_path": self.path,
                "query": {k: v[0] for k, v in parse_qs(parsed.query).items()},
                "headers": dict(self.headers),
                "body": body,
                "json": parsed_body,
            }
            state.requests.append(record)
            return record

        def _respond(self):
            record = self._record()
            route = state.get_route(record["path"])
            if route is None:
                payload = json.dumps({"error": "route not configured", "path": record["path"]}).encode()
                status, content_type = 404, "application/json"
            else:
                status = route["status"]
                content_type = route["content_type"]
                if route["raw"] is not None:
                    payload = route["raw"]
                elif callable(route["body"]):
                    payload = json.dumps(route["body"](record)).encode()
                else:
                    payload = json.dumps(route["body"]).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = _respond
        do_POST = _respond
        do_PUT = _respond
        do_DELETE = _respond

    return _Handler


@pytest.fixture
def fake_valt_server():
    state = FakeValtServerState()
    state.install_default_routes()
    server = HTTPServer(("127.0.0.1", 0), _build_handler(state))
    state.host, state.port = server.server_address[0], server.server_address[1]
    # Single-threaded HTTPServer on purpose: valt_client patches threading.Thread, which a
    # ThreadingHTTPServer would try to use while serving requests. Short poll keeps shutdown snappy.
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()
        # Bounded join: a wedged serve_forever must not hang the whole suite.
        thread.join(timeout=5)


@pytest.fixture
def valt_client(fake_valt_server, tmp_path):
    from valt.valt import VALT

    with mock.patch("valt.mixins.auth.threading.Timer") as timer_cls, \
            mock.patch("valt.mixins.monitor.threading.Thread") as thread_cls:
        client = VALT(
            fake_valt_server.address,
            "tester",
            "s3cret",
            timeout=5,
            logpath=str(tmp_path / "valt-test.log"),
        )
        client.fake_timer_cls = timer_cls
        client.fake_thread_cls = thread_cls
        try:
            yield client
        finally:
            client.disconnect()
