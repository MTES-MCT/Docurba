from urllib.request import Request

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def security_txt(request: Request) -> HttpResponse:
    # https://www.rfc-editor.org/rfc/rfc9116
    # https://securitytxt.org/ can be helpful in generating the document.
    return render(
        request,
        template_name="static/security/security.txt",
        content_type="text/plain; charset=utf-8",
    )
