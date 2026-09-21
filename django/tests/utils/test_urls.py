from docurba.utils.urls import get_absolute_url


def test_get_absolute_url() -> None:
    assert get_absolute_url() == "http://localhost:8000/"
    assert get_absolute_url(path="/frise/ID") == "http://localhost:8000/frise/ID"
    assert get_absolute_url(path="frise/ID") == "http://localhost:8000/frise/ID"
    assert get_absolute_url("frise/ID") == "http://localhost:8000/frise/ID"
