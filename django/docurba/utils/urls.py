from django.conf import settings


def get_absolute_url(path: str = "") -> str:
    path = path.removeprefix("/")
    return f"{settings.DOCURBA_PROTOCOL}://{settings.DOCURBA_FQDN}/{path}"
