from __future__ import annotations

import json
from unittest import mock
from urllib import error

import pytest

from valt.mixins.auth import ValtAuth
from valt.mixins.errors import ValtErrors


class AuthHarness(ValtAuth, ValtErrors):
    def __init__(self, version="6.5.1"):
        self.logger = mock.MagicMock()
        self.baseurl = "http://valt.test/api/v3/"
        self.username = "tester"
        self.password = "s3cret"
        self.success_reauth_time = 28800
        self.failure_reauth_time = 30
        self._accesstoken = 0
        self._accesstoken_observers = []
        self._errormsg = None
        self._errormsg_observers = []
        self.send_to_valt = mock.MagicMock(return_value={"data": {"access_token": "token-abc"}})
        self.get_version = mock.MagicMock(return_value=version)


@pytest.fixture
def timer_cls():
    with mock.patch("valt.mixins.auth.threading.Timer") as patched:
        yield patched


def test_auth_posts_credentials_to_login_endpoint(timer_cls):
    harness = AuthHarness()

    harness.auth()

    harness.send_to_valt.assert_called_once_with(
        "http://valt.test/api/v3/login",
        values={"username": "tester", "password": "s3cret"},
    )


def test_successful_auth_sets_token_version_and_success_timer(timer_cls):
    harness = AuthHarness(version="6.5.1")

    harness.auth()

    assert harness.accesstoken == "token-abc"
    assert harness.connected is True
    assert harness.errormsg is None
    assert (harness.version, harness.major_version, harness.minor_version, harness.patch_level) == (
        "6.5.1",
        "6",
        "5",
        "1",
    )
    timer_cls.assert_called_once_with(28800, harness.auth)
    assert timer_cls.return_value.daemon is True
    timer_cls.return_value.start.assert_called_once_with()


def test_version_five_leaves_patch_level_at_zero(timer_cls):
    harness = AuthHarness(version="5.9")

    harness.auth()

    assert (harness.major_version, harness.minor_version, harness.patch_level) == ("5", "9", "0")


def test_unknown_version_falls_back_to_zeroes(timer_cls):
    harness = AuthHarness(version=0)

    harness.auth()

    assert harness.version == "0.0.0"
    assert (harness.major_version, harness.minor_version, harness.patch_level) == ("0", "0", "0")


def test_failed_auth_clears_token_and_schedules_fast_retry(timer_cls):
    harness = AuthHarness()
    harness.send_to_valt.return_value = None

    harness.auth()

    assert harness.accesstoken == 0
    assert harness.connected is False
    timer_cls.assert_called_once_with(30, harness.auth)


def test_auth_is_skipped_without_credentials(timer_cls):
    harness = AuthHarness()
    harness.username = ""

    harness.auth()

    harness.send_to_valt.assert_not_called()
    timer_cls.assert_not_called()


def test_auth_is_skipped_without_baseurl(timer_cls):
    harness = AuthHarness()
    harness.baseurl = None

    harness.auth()

    harness.send_to_valt.assert_not_called()


def test_reauthenticate_cancels_a_pending_timer(timer_cls):
    harness = AuthHarness()
    existing = mock.MagicMock()
    harness.reauth = existing

    harness.reauthenticate(60)

    existing.cancel.assert_called_once_with()
    timer_cls.assert_called_once_with(60, harness.auth)
    assert harness.reauth is timer_cls.return_value


def test_accesstoken_observers_are_notified(timer_cls):
    harness = AuthHarness()
    seen = []
    harness.bind_to_accesstoken(seen.append)

    harness.auth()

    assert seen == ["token-abc"]


def test_test_connection_returns_true_on_success():
    with mock.patch("valt.mixins.auth.request.urlopen") as urlopen:
        ok, message = ValtAuth.test_connection("valt.test", "tester", "s3cret")

    assert (ok, message) == (True, None)
    req, params = urlopen.call_args.args[0], urlopen.call_args.args[1]
    assert req.get_full_url() == "http://valt.test/api/v3/login"
    assert json.loads(params.decode()) == {"username": "tester", "password": "s3cret"}


def test_test_connection_reports_bad_credentials():
    http_error = error.HTTPError("http://valt.test/api/v3/login", 401, "Unauthorized", {}, None)
    with mock.patch("valt.mixins.auth.request.urlopen", side_effect=http_error):
        ok, message = ValtAuth.test_connection("valt.test", "tester", "wrong")

    assert (ok, message) == (False, "Invalid Username or Password")


def test_test_connection_reports_unreachable_server():
    with mock.patch("valt.mixins.auth.request.urlopen", side_effect=error.URLError("no route")):
        ok, message = ValtAuth.test_connection("https://valt.test", "tester", "s3cret")

    assert (ok, message) == (False, "Unable to Connect")
