from csv import DictWriter
from datetime import date
from operator import attrgetter

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_safe

from core.models import CommuneProcedure, communes


@require_safe
def api_perimetres(request: HttpRequest) -> HttpResponse:
    departement = request.GET.get("departement")

    try:
        avant = (
            date.fromisoformat(request.GET.get("avant"))
            if request.GET.get("avant")
            else None
        )
    except ValueError:
        return HttpResponseBadRequest(
            "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )

    communes_procedures = CommuneProcedure.objects.with_opposabilite(
        departement=departement, avant=avant
    )

    response = HttpResponse(content_type="text/csv;charset=utf-8")
    csv_writer = DictWriter(
        response,
        dialect="unix",
        fieldnames=[
            "collectivite_code",
            "collectivite_type",
            "procedure_id",
            "opposable",
        ],
    )
    csv_writer.writeheader()
    csv_writer.writerows(
        {field: getattr(commune_procedure, field) for field in csv_writer.fieldnames}
        for commune_procedure in communes_procedures
    )

    return response


@require_safe
def collectivite(
    request: HttpRequest, collectivite_code: str, collectivite_type: str = "COM"
) -> HttpResponse:
    communes_procedures = CommuneProcedure.objects.with_opposabilite(
        collectivite_code=collectivite_code, collectivite_type=collectivite_type
    )
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
