import logging
from csv import DictWriter

from django.http import HttpRequest, HttpResponse

from core.models import CommuneProcedure, communes


def _format_perimetre(perimetre: dict) -> dict:
    perimetre["opposable"] = str(perimetre["opposable"]).lower()
    perimetre["created_at"] = perimetre["created_at"].isoformat()

    return perimetre


def perimetres(request: HttpRequest) -> HttpResponse:
    perimetres = CommuneProcedure.objects.all()
    if departement := request.GET.get("departement"):
        perimetres = perimetres.filter(departement=departement)

    response = HttpResponse(content_type="text/html;charset=utf-8")
    csv_writer = DictWriter(
        response,
        dialect="unix",
        fieldnames=[
            "created_at",
            "collectivite_code",
            "collectivite_type",
            "procedure_id",
            "opposable",
            "departement",
        ],
    )
    csv_writer.writeheader()
    csv_writer.writerows(
        _format_perimetre(perimetre)
        for perimetre in perimetres.values(*csv_writer.fieldnames).iterator()
    )

    return response
