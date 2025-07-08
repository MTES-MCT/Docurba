from csv import DictWriter
from datetime import date
from itertools import groupby
from operator import attrgetter

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_safe

from core.models import Collectivite, Commune, Procedure


def _avant(request: HttpRequest) -> date | None:
    return (
        date.fromisoformat(request.GET.get("avant"))
        if request.GET.get("avant")
        else None
    )


@require_safe
def api_perimetres(request: HttpRequest) -> HttpResponse:
    try:
        avant = _avant(request)
    except ValueError:
        return HttpResponseBadRequest(
            "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )

    communes = Commune.objects.with_procedures_principales(avant=avant)
    if departement := request.GET.get("departement"):
        communes = communes.filter(departement__code_insee=departement)

    response = HttpResponse(content_type="text/csv;charset=utf-8")

    csv_writer = DictWriter(
        response,
        dialect="unix",
        fieldnames=[
            "annee_cog",
            "collectivite_code",
            "collectivite_type",
            "procedure_id",
            "type_document",
            "opposable",
        ],
    )
    csv_writer.writeheader()
    csv_writer.writerows(
        {
            "annee_cog": "2024",
            "collectivite_code": commune.code_insee,
            "collectivite_type": commune.type,
            "procedure_id": procedure.id,
            "type_document": procedure.type_document,
            "opposable": commune.is_opposable(procedure),
        }
        for commune in communes.iterator(chunk_size=1000)
        for procedure in commune.procedures_principales
    )
    return response


@require_safe
def api_scots(request: HttpRequest) -> HttpResponse:
    try:
        avant = _avant(request)
    except ValueError:
        return HttpResponseBadRequest(
            "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )

    collectivites = Collectivite.objects.portant_scot(avant=avant)
    if departement := request.GET.get("departement"):
        collectivites = collectivites.filter(departement__code_insee=departement)

    response = HttpResponse(content_type="text/csv;charset=utf-8")
    csv_writer = DictWriter(
        response,
        dialect="unix",
        fieldnames=[
            "annee_cog",
            # Collectivité
            "scot_code_region",
            "scot_libelle_region",
            "scot_code_departement",
            "scot_lib_departement",
            "scot_codecollectivite",
            "scot_code_type_collectivite",
            "scot_nom_collectivite",
            # Approuvée
            "pa_id",
            "pa_nom_schema",
            "pa_noserie_procedure",
            "pa_scot_interdepartement",
            "pa_date_publication_perimetre",
            "pa_date_prescription",
            "pa_date_arret_projet",
            "pa_date_approbation",
            "pa_annee_approbation",
            "pa_date_fin_echeance",
            "pa_nombre_communes",
            # En cours
            "pc_id",
            "pc_nom_schema",
            "pc_noserie_procedure",
            "pc_proc_elaboration_revision",
            "pc_scot_interdepartement",
            "pc_date_publication_perimetre",
            "pc_date_prescription",
            "pc_date_arret_projet",
            "pc_nombre_communes",
        ],
    )

    def format_row(
        collectivite: Collectivite,
        scot_opposable: Procedure | None,
        scot_en_cours: Procedure | None,
    ) -> dict[str, str]:
        champs_groupement = {
            "annee_cog": "2024",
            "scot_code_region": collectivite.departement.region.code_insee,
            "scot_libelle_region": collectivite.departement.region.nom,
            "scot_code_departement": collectivite.departement.code_insee,
            "scot_lib_departement": collectivite.departement.nom,
            "scot_codecollectivite": collectivite.code_insee,
            "scot_code_type_collectivite": collectivite.type,
            "scot_nom_collectivite": collectivite.nom,
        }

        champs_opposable = {}
        if scot_opposable:
            champs_opposable = {
                "pa_id": scot_opposable.id,
                "pa_nom_schema": scot_opposable.name,
                "pa_noserie_procedure": scot_opposable.from_sudocuh,
                "pa_scot_interdepartement": scot_opposable.is_interdepartemental,
                "pa_date_publication_perimetre": scot_opposable.date_publication_perimetre,
                "pa_date_prescription": scot_opposable.date_prescription,
                "pa_date_arret_projet": scot_opposable.date_arret_projet,
                "pa_date_approbation": scot_opposable.date_approbation,
                "pa_annee_approbation": scot_opposable.date_approbation.year,
                "pa_date_fin_echeance": scot_opposable.date_fin_echeance,
                "pa_nombre_communes": len(scot_opposable.communes),
            }

        champs_en_cours = {}
        if scot_en_cours:
            champs_en_cours = {
                "pc_id": scot_en_cours.id,
                "pc_nom_schema": scot_en_cours.name,
                "pc_noserie_procedure": scot_en_cours.from_sudocuh,
                "pc_proc_elaboration_revision": scot_en_cours.type,
                "pc_scot_interdepartement": scot_en_cours.is_interdepartemental,
                "pc_date_publication_perimetre": scot_en_cours.date_publication_perimetre,
                "pc_date_prescription": scot_en_cours.date_prescription,
                "pc_date_arret_projet": scot_en_cours.date_arret_projet,
                "pc_nombre_communes": len(scot_en_cours.communes),
            }

        return champs_groupement | champs_opposable | champs_en_cours

    csv_writer.writeheader()
    csv_writer.writerows(
        format_row(collectivite, scot_opposable, scot_en_cours)
        for collectivite in collectivites.iterator(chunk_size=1000)
        for scot_opposable, scot_en_cours in collectivite.scots_pour_csv
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
