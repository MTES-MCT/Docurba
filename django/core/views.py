from csv import DictWriter
from operator import attrgetter

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from core.models import CommuneProcedure, communes


def _format_perimetre(perimetre: dict) -> dict:
    perimetre["opposable"] = str(perimetre["opposable"]).lower()
    perimetre["created_at"] = perimetre["created_at"].isoformat()

    return perimetre


# FIXME : Procédures secondaires ?
# FIXME : Procédures archivées ?


@require_safe
def perimetres(request: HttpRequest) -> HttpResponse:
    departement = request.GET.get("departement")
    perimetres = CommuneProcedure.objects.filter(
        procedure__is_principale=True
    ).departement(departement)

    response = HttpResponse(content_type="text/csv;charset=utf-8")
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
    for perimetre in perimetres[: int(request.GET.get("limit", -1))]:  # .iterator()
        a = {field: getattr(perimetre, field) for field in csv_writer.fieldnames}
        csv_writer.writerow(a)

    return response


@require_safe
def collectivite(
    request: HttpRequest, collectivite_code: str, collectivite_type: str = "COM"
) -> HttpResponse:
    communes_procedures = CommuneProcedure.objects.filter(
        procedure__is_principale=True
    ).collectivite(collectivite_code, collectivite_type)
    communes_procedures = sorted(
        communes_procedures,
        key=attrgetter("procedure.is_schema", "procedure.date_approbation"),
        reverse=True,
    )

    commune = communes[f"{collectivite_code}_{collectivite_type}"]
    return render(
        request,
        "collectivite.html",
        {"collectivite": commune, "cp": communes_procedures},
    )
