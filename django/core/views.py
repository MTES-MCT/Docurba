from csv import DictWriter
from datetime import date
from itertools import groupby
from operator import attrgetter

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_safe

from core.models import Commune


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

    communes = Commune.objects.with_procedures_principales(avant=avant)
    if departement:
        communes = communes.filter(departement__code_insee=departement)

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
        {
            "collectivite_code": commune.code_insee,
            "collectivite_type": commune.type,
            "procedure_id": procedure.id,
            "opposable": commune.is_opposable(procedure),
        }
        for commune in communes
        for procedure in commune.procedures_principales
    )

    return response


@require_safe
def collectivite(
    request: HttpRequest, collectivite_code: str, collectivite_type: str = "COM"
) -> HttpResponse:
    commune = (
        Commune.objects.with_procedures_principales()
        .filter(id=f"{collectivite_code}_{collectivite_type}")
        .first()
    )
    is_schema = attrgetter("is_schema")
    procedures_principales_by_schema = {
        schema: [
            (procedure, commune.is_opposable(procedure)) for procedure in procedures
        ]
        for schema, procedures in groupby(
            sorted(commune.procedures_principales, key=is_schema),
            key=is_schema,
        )
    }

    return render(
        request,
        "collectivite.html",
        {
            "collectivite": commune,
            "procedures_principales_by_schema": procedures_principales_by_schema,
        },
    )
