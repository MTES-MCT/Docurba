import datetime as dt
import re

from django.test import Client
from django.urls import reverse


def test_security_txt_is_valid(client: Client) -> None:
    response = client.get(reverse("security-txt"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain; charset=utf-8"

    expire_re = re.compile(r"^Expires: (?P<expires>.*)$")
    for line in response.content.decode().splitlines():
        if match := expire_re.match(line):
            expiry = match.group("expires")
            expiry = dt.datetime.fromisoformat(expiry)
            break

    assert expiry - dt.datetime.now(tz=dt.UTC) >= dt.timedelta(days=14)
