from csv import DictWriter
from datetime import date
from itertools import groupby
from operator import attrgetter

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_safe

from core.models import Collectivite, Commune, Procedure, TypeCollectivite


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
def api_communes(request: HttpRequest) -> HttpResponse:
    try:
        avant = _avant(request)
    except ValueError:
        return HttpResponseBadRequest(
            "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )

    communes = (
        Commune.objects.filter(type=TypeCollectivite.COM)
        .with_procedures_principales(avant=avant)
        .csv_prefetch()
    )
    if departement := request.GET.get("departement"):
        communes = communes.filter(departement__code_insee=departement)

    response = HttpResponse(content_type="text/csv;charset=utf-8")
    csv_writer = DictWriter(
        response,
        dialect="unix",
        fieldnames=[
            "annee_cog",
            # Commune
            "code_insee",
            "com_nom",
            "com_code_departement",
            "com_nom_departement",
            "com_code_region",
            "com_nom_region",
            "com_nouvelle",
            "epci_reg",
            "epci_region",
            "epci_dept",
            "epci_departement",
            "epci_type",
            "epci_nom",
            "epci_siren",
            # Collectivité Porteuse
            "collectivite_porteuse",
            "cp_type",
            "cp_code_region",
            "cp_lib_region",
            "cp_code_departement",
            "cp_nom_departement",
            "cp_nom",
            "cp_siren",
            "cp_code_insee",
            # "plan_code_etat_simplifie",
            # "plan_libelle_code_etat_simplifie",
            # "plan_code_etat_complet",
            # "plan_libelle_code_etat_complet",
            # "types_pc",
            # En cours
            "pc_docurba_id",
            "pc_num_procedure_sudocuh",
            "pc_nb_communes",
            "pc_type_document",
            "pc_type_procedure",
            "pc_date_prescription",
            "pc_date_arret_projet",
            "pc_date_pac",
            "pc_date_pac_comp",
            "pc_plui_valant_scot",
            # "pc_pluih",
            # "pc_sectoriel",
            # "pc_pdu_tient_lieu",
            "pc_pdu_obligatoire",
            "pc_nom_sst",
            "pc_cout_sst_ht",
            "pc_cout_sst_ttc",
            # Approuvée
            "pa_docurba_id",
            "pa_num_procedure_sudocuh",
            "pa_nb_communes",
            "pa_type_document",
            "pa_type_procedure",
            # "pa_sectoriel",
            "pa_date_prescription",
            "pa_date_arret_projet",
            "pa_date_pac",
            "pa_date_pac_comp",
            "pa_date_approbation",
            "pa_annee_prescription",
            "pa_annee_approbation",
            "pa_date_executoire",
            "pa_delai_approbation",
            "pa_plui_valant_scot",
            # "pa_pluih",
            # "pa_pdu_tient_lieu",
            "pa_pdu_obligatoire",
            "pa_nom_sst",
            "pa_cout_sst_ht",
            "pa_cout_sst_ttc",
        ],
    )

    def format_row(commune: Commune) -> dict[str, str]:
        champs_commune = {
            "annee_cog": "2024",
            "code_insee": commune.code_insee_unique,
            "com_nom": commune.nom,
            "com_code_departement": commune.departement.code_insee,
            "com_nom_departement": commune.departement.nom,
            "com_code_region": commune.departement.region.code_insee,
            "com_nom_region": commune.departement.region.nom,
            "com_nouvelle": commune.is_nouvelle,
            "collectivite_porteuse": commune.collectivite_porteuse.code_insee,
            "cp_type": commune.collectivite_porteuse.type,
            "cp_code_region": commune.collectivite_porteuse.departement.region.code_insee,
            "cp_lib_region": commune.collectivite_porteuse.departement.region.nom,
            "cp_code_departement": commune.collectivite_porteuse.departement.code_insee,
            "cp_nom_departement": commune.collectivite_porteuse.departement.nom,
            "cp_nom": commune.collectivite_porteuse.nom,
            "cp_siren": commune.collectivite_porteuse.code_insee
            if not commune.collectivite_porteuse.is_commune
            else "",
            "cp_code_insee": commune.collectivite_porteuse.code_insee
            if commune.collectivite_porteuse.is_commune
            else "",
            # "plan_code_etat_simplifie": "sudocuhCodes.etat.code",  # noqa: ERA001
            # "plan_libelle_code_etat_simplifie": "sudocuhCodes.etat.label",  # noqa: ERA001
            # "plan_code_etat_complet": "sudocuhCodes.bcsi.code",  # noqa: ERA001
            # "plan_libelle_code_etat_complet": "sudocuhCodes.bcsi.label",  # noqa: ERA001
            # "types_pc": "currentsDocTypes",  # noqa: ERA001
        }

        champs_intercommunalite = {}
        if intercommunalite := commune.intercommunalite:
            champs_intercommunalite = {
                "epci_reg": intercommunalite.departement.region.code_insee,
                "epci_region": intercommunalite.departement.region.nom,
                "epci_dept": intercommunalite.departement.code_insee,
                "epci_departement": intercommunalite.departement.nom,
                "epci_type": intercommunalite.type,
                "epci_nom": intercommunalite.nom,
                "epci_siren": intercommunalite.code_insee,
            }

        champs_en_cours = {}
        if plan_en_cours := commune.plan_en_cours:
            champs_en_cours = {
                "pc_docurba_id": plan_en_cours.id,
                "pc_num_procedure_sudocuh": plan_en_cours.from_sudocuh,
                "pc_nb_communes": len(plan_en_cours.perimetre_prefetched),
                "pc_type_document": plan_en_cours.type_document,
                "pc_type_procedure": plan_en_cours.type,
                "pc_date_prescription": plan_en_cours.date_prescription,
                "pc_date_arret_projet": plan_en_cours.date_arret_projet,
                "pc_date_pac": plan_en_cours.date_porter_a_connaissance,
                "pc_date_pac_comp": plan_en_cours.date_porter_a_connaissance_complementaire,
                "pc_plui_valant_scot": plan_en_cours.vaut_SCoT,
                # "pc_pluih": "planCurrent.is_pluih",  # noqa: ERA001
                # "pc_sectoriel": "planCurrent.isSectoriel",  # noqa: ERA001
                # "pc_pdu_tient_lieu": "planCurrent.is_pdu",  # noqa: ERA001
                "pc_pdu_obligatoire": plan_en_cours.obligation_PDU,
                "pc_nom_sst": plan_en_cours.maitrise_d_oeuvre
                and plan_en_cours.maitrise_d_oeuvre["nomprestaexterne"],
                "pc_cout_sst_ht": plan_en_cours.maitrise_d_oeuvre
                and plan_en_cours.maitrise_d_oeuvre["coutplanht"],
                "pc_cout_sst_ttc": plan_en_cours.maitrise_d_oeuvre
                and plan_en_cours.maitrise_d_oeuvre["coutplanttc"],
            }

        champs_opposable = {}
        if plan_opposable := commune.plan_opposable:
            champs_opposable = {
                "pa_docurba_id": plan_opposable.id,
                "pa_num_procedure_sudocuh": plan_opposable.from_sudocuh,
                "pa_nb_communes": len(plan_opposable.perimetre_prefetched),
                "pa_type_document": plan_opposable.type_document,
                "pa_type_procedure": plan_opposable.type,
                # "pa_sectoriel": plan_opposable.is_sectoriel,  # noqa: ERA001
                "pa_date_prescription": plan_opposable.date_prescription,
                "pa_date_arret_projet": plan_opposable.date_arret_projet,
                "pa_date_pac": plan_opposable.date_porter_a_connaissance,
                "pa_date_pac_comp": plan_opposable.date_porter_a_connaissance_complementaire,
                "pa_date_approbation": plan_opposable.date_approbation,
                "pa_annee_prescription": plan_opposable.date_prescription
                and plan_opposable.date_prescription.year,
                "pa_annee_approbation": plan_opposable.date_approbation.year,
                "pa_date_executoire": plan_opposable.date_caractere_executoire,
                "pa_delai_approbation": plan_opposable.delai_d_approbation,
                "pa_plui_valant_scot": plan_opposable.vaut_SCoT,
                # "pa_pluih": "planOpposable.is_pluih",  # noqa: ERA001
                # "pa_pdu_tient_lieu": "planOpposable.is_pdu",  # noqa: ERA001
                "pa_pdu_obligatoire": plan_opposable.obligation_PDU,
                "pa_nom_sst": plan_opposable.maitrise_d_oeuvre
                and plan_opposable.maitrise_d_oeuvre["nomprestaexterne"],
                "pa_cout_sst_ht": plan_opposable.maitrise_d_oeuvre
                and plan_opposable.maitrise_d_oeuvre["coutplanht"],
                "pa_cout_sst_ttc": plan_opposable.maitrise_d_oeuvre
                and plan_opposable.maitrise_d_oeuvre["coutplanttc"],
            }
        return (
            champs_commune
            | champs_intercommunalite
            | champs_opposable
            | champs_en_cours
        )

    csv_writer.writeheader()
    csv_writer.writerows(
        format_row(commune) for commune in communes.iterator(chunk_size=1000)
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
