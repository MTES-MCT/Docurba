from csv import DictWriter

from django.http import HttpRequest, HttpResponse

from core.models import CommuneProcedure


def _format_perimetre(perimetre: dict) -> dict:
    perimetre["opposable"] = str(perimetre["opposable"]).lower()
    perimetre["created_at"] = perimetre["created_at"].isoformat()

    return perimetre


# FIXME : Procédures secondaires ?
# FIXME : Procédures archivées ?


def perimetres(request: HttpRequest) -> HttpResponse:
    departement = request.GET.get("departement")
    perimetres = CommuneProcedure.objects.filter(
        procedure__is_principale=True
    ).departement(departement)

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
    for perimetre in perimetres[: int(request.GET.get("limit", -1))]:  # .iterator()
        a = {field: getattr(perimetre, field) for field in csv_writer.fieldnames}
        csv_writer.writerow(a)

    return response
