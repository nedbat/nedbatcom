import pytest
from django.test import RequestFactory, override_settings

from ..debug_toolbar import show_toolbar_behind_proxy

@override_settings(INTERNAL_IPS=["1.2.3.4"])
@pytest.mark.parametrize("forwarded, shown", [
    (None, False),
    ("", False),
    ("1.2.3.4", True),
    ("9.9.9.9", False),
    ("9.9.9.9, 1.2.3.4", True),
    ("9.9.9.9,1.2.3.4", True),
    # A client can't get the toolbar by forging an earlier entry.
    ("1.2.3.4, 9.9.9.9", False),
])
def test_show_toolbar_behind_proxy(forwarded, shown):
    headers = {} if forwarded is None else {"X-Forwarded-For": forwarded}
    request = RequestFactory().get("/blog/", headers=headers, REMOTE_ADDR="1.2.3.4")
    assert show_toolbar_behind_proxy(request) == shown
