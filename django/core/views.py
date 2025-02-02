from csv import DictWriter
from dataclasses import field

from django.http import HttpRequest, HttpResponse

from core.models import ProceduresPerimetres


def perimetres(request: HttpRequest) -> HttpResponse:
    perimetres = ProceduresPerimetres.objects.all()
    response = HttpResponse(content_type="text/html;charset=utf-8")
    csv_writer = DictWriter(response, dialect="unix", fieldnames=["id", "lol"])
    csv_writer.writeheader()
    # csv_writer.writerows(perimetres)
    response.write("</body>")
    return response
