import logging
import re
from os import environ
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

ORIGIN = "http://localhost:3000"
ROOT_DIR = Path(__file__).parent

load_dotenv(ROOT_DIR / ".env.pytest")


@pytest.fixture
def page(new_context):
    logging.warning(Path(__file__).parent)

    storage_state = Path(ROOT_DIR / "playwright_state.json")

    if storage_state.exists():
        logging.warning("Reusing login state")
        page = new_context(storage_state=storage_state).new_page()
        # page.set_default_timeout(5_000)
        yield page
    else:
        logging.warning("Generating login state")
        context = new_context()
        page = context.new_page()
        login(page)
        yield page
        context.storage_state(path=storage_state)


def login(page: Page):
    page.goto(ORIGIN + "/login/ddt/signin")
    page.get_by_role("button", name="Refuser").click()
    page.get_by_label("Email").fill(environ["ADMIN_EMAIL"])
    page.get_by_label("Mot de passe").fill(environ["ADMIN_PASSWORD"])
    page.get_by_role("button", name="Se connecter").click()


class ProcedurePage:
    def __init__(self, page: Page):
        self.page = page
        self.titre = page.locator("h1")

    @classmethod
    def navigate(cls, page: Page, uuid):
        page.goto(ORIGIN + "/frise/" + uuid)
        return cls(page)


class CommonCollectivitePage:
    def __init__(self, page: Page):
        self.page = page
        self.onglet_du_communaux = page.get_by_role("tab", name="DU communaux")
        self.onglet_scot = page.get_by_role("tab", name="SCoT")

    def expect_procedure_intercommunale(self, titre, uuid):
        expect(self.page.get_by_text(re.compile(rf"{titre}\s+{uuid}"))).to_be_visible()

    def expect_procedure_communale(self, titre, code_intercommunalite, uuid):
        self.onglet_du_communaux.click()
        expect(
            self.page.get_by_text(
                re.compile(rf"{titre}\s+\({code_intercommunalite}\)\s+{uuid}")
            )
        ).to_be_visible()

    def expect_scot(self, titre, uuid):
        self.onglet_scot.click()
        expect(self.page.get_by_text(re.compile(rf"{titre}\s+{uuid}"))).to_be_visible()

    def expect_procedure_secondaire_intercommunale(self, titre, uuid):
        procedures_secondaires_buttons = self.page.get_by_role(
            "button", name="Procédures secondaires"
        )

        expect(self.page.get_by_role("progressbar")).to_have_count(0)

        procedures_secondaires_buttons.first.wait_for()
        for button in procedures_secondaires_buttons.all():
            button.click()
        expect(self.page.get_by_text(re.compile(rf"{titre}\s+{uuid}"))).to_be_visible()

    def expect_procedure_secondaire_communale(self, titre, uuid):
        self.onglet_du_communaux.click()
        procedures_secondaires_buttons = self.page.get_by_role(
            "button", name="Procédures secondaires"
        )

        expect(self.page.get_by_role("progressbar")).to_have_count(0)

        procedures_secondaires_buttons.first.wait_for()
        for button in procedures_secondaires_buttons.all():
            button.click()
        expect(self.page.get_by_text(re.compile(rf"{titre}\s+{uuid}"))).to_be_visible()


class CollectivitePage(CommonCollectivitePage):
    @classmethod
    def navigate(cls, page: Page, code_collectivite):
        page.goto(ORIGIN + f"/collectivites/{code_collectivite}/")
        return cls(page)


class DDTCommunePage(CommonCollectivitePage):
    @classmethod
    def navigate(cls, page: Page, code_departement, code_commune):
        page.goto(
            ORIGIN + f"/ddt/{code_departement}/collectivites/{code_commune}/commune/"
        )
        return cls(page)

    def goto_ajouter_procedure(self):
        self.page.get_by_role("link", name="Ajouter une procédure").click()
        return AjoutProcedurePage(self.page)


class AjoutProcedurePage:
    def __init__(self, page):
        self.page = page

    def expect_procedure_parent(self, titre):
        self.page.get_by_role("tab", name="Procédure secondaire").click()
        self.page.get_by_label("Procédure parente").click()

        self.page.get_by_role("option", name=titre, exact=True).click()
        expect(self.page.get_by_role("button", name=titre)).to_be_visible()


class DDTIntercommunalitePage(CommonCollectivitePage):
    @classmethod
    def navigate(cls, page: Page, code_departement, code_intercommunalite):
        page.goto(
            ORIGIN
            + f"/ddt/{code_departement}/collectivites/{code_intercommunalite}/epci/"
        )
        return cls(page)


class DDTCollectivitesPage:
    def __init__(self, page: Page):
        self.page = page

    @classmethod
    def navigate(cls, page: Page, code_departement):
        page.goto(ORIGIN + f"/ddt/{code_departement}/collectivites")
        return cls(page)

    def show_all_procedures(self):
        self.page.get_by_role("button", name="10", exact=True).click()
        self.page.get_by_role("option", name="Tous").click()

    def expect_procedure(self, uuid, titre):
        all_procedures = self.page.locator(f"[href='/frise/{uuid}']")
        all_procedures.first.wait_for()
        for procedure in all_procedures.all():
            expect(procedure).to_have_text(titre)


class DDTProceduresPage:
    def __init__(self, page: Page):
        self.page = page

    @classmethod
    def navigate(cls, page: Page, code_departement):
        page.goto(ORIGIN + f"/ddt/{code_departement}/procedures")
        return cls(page)

    def show_all_procedures(self):
        self.page.get_by_role("button", name="10", exact=True).click()
        self.page.get_by_role("option", name="Tous").click()

    def expect_procedure(self, titre):
        self.page.get_by_label("Rechercher une procédure...").fill(titre)
        expect(self.page.get_by_role("row", name=titre).first).to_be_visible()

    def expect_dialog(self, titre):
        self.page.get_by_role("row", name=titre).first.get_by_role(
            "button", name="commune"
        ).click()
        expect(
            self.page.get_by_role("dialog").get_by_text(f"Périmètre de {titre}")
        ).to_be_visible()


def common_principale(page, uuid, titre, code_departement):
    # Frise
    procedure_page = ProcedurePage.navigate(page, uuid)
    expect(procedure_page.titre).to_contain_text(titre)

    # DDT Collectivités
    ddt_collectivites = DDTCollectivitesPage.navigate(page, code_departement)
    ddt_collectivites.show_all_procedures()
    ddt_collectivites.expect_procedure(uuid, titre)

    # DDT Procédures
    ddt_procedures = DDTProceduresPage.navigate(page, code_departement)
    ddt_procedures.expect_procedure(titre)
    ddt_procedures.expect_dialog(titre)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune,code_intercommunalite",
    [
        (
            "de58f2e2-6da7-40e6-9aad-79f9ee83687b",
            "Révision n°3 de PLU Pénestin Second arrêt",  # Titre dans la base
            "56",
            "56155",
            "244400610",
        ),
        (
            "7dc65fd3-2ad3-41fb-bec7-d0fa9c16f2fa",
            "Révision PLU Bulgnéville",  # Pas de titre dans la base
            "88",
            "88079",
            "200068682",
        ),
    ],
)
def test_procedure_principale_communale(
    page: Page,
    uuid: str,
    titre: str,
    code_departement: str,
    code_commune: str,
    code_intercommunalite: str,
) -> None:
    common_principale(page, uuid, titre, code_departement)

    # Collectivité
    commune_page = CollectivitePage.navigate(page, code_commune)
    commune_page.expect_procedure_communale(titre, code_commune, uuid)
    intercommunalite_page = CollectivitePage.navigate(page, code_intercommunalite)
    intercommunalite_page.expect_procedure_communale(titre, code_commune, uuid)

    # DDT Commune
    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ddt_commune_page.expect_procedure_communale(titre, code_commune, uuid)

    # DDT EPCI
    ddt_intercommunalite_page = DDTIntercommunalitePage.navigate(
        page, code_departement, code_intercommunalite
    )
    ddt_intercommunalite_page.expect_procedure_communale(titre, code_commune, uuid)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune,code_intercommunalite",
    [
        (
            "6f7a90f7-084b-4b1f-9e91-1df0cdefef09",
            "Elaboration PLUiH CC du Pays Bigouden Sud",  # Pas de titre dans la base
            "29",
            "29284",
            "242900702",
        ),
        (
            "6abdd4cd-f1a0-49d6-9f17-186ac0ba640c",
            "Elaboration de PLUiH CC du Val de l'Aisne",  # Titre dans la base
            "02",
            "02758",
            "240200501",
        ),
    ],
)
def test_procedure_principale_intercommunale(
    page: Page,
    uuid: str,
    titre: str,
    code_departement: str,
    code_commune: str,
    code_intercommunalite: str,
) -> None:
    common_principale(page, uuid, titre, code_departement)

    # Collectivité
    commune_page = CollectivitePage.navigate(page, code_commune)
    commune_page.expect_procedure_intercommunale(titre, uuid)
    intercommunalite_page = CollectivitePage.navigate(page, code_intercommunalite)
    intercommunalite_page.expect_procedure_intercommunale(titre, uuid)

    # DDT Commune
    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ddt_commune_page.expect_procedure_intercommunale(titre, uuid)

    # DDT EPCI
    ddt_intercommunalite_page = DDTIntercommunalitePage.navigate(
        page, code_departement, code_intercommunalite
    )
    ddt_intercommunalite_page.expect_procedure_intercommunale(titre, uuid)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune,code_intercommunalite",
    [
        (
            "ed9fa567-04bc-47fa-9eec-1f9e5bbe52bb",
            "SCOT DU PAYS DE SAINT-LOUIS  ET DES TROIS FRONTIERES",
            "68",
            "68120",
            "200066058",
        ),
        (
            "40c3428e-dae0-4b00-85ea-127005ca6d59",
            "SCOT DU PAYS DE REDON ET VILAINE",
            "35",
            "35236",
            "243500741",
        ),
        (
            "40c3428e-dae0-4b00-85ea-127005ca6d59",
            "SCOT DU PAYS DE REDON ET VILAINE",
            "56",
            "56001",
            "243500741",
        ),
        (
            "40c3428e-dae0-4b00-85ea-127005ca6d59",
            "SCOT DU PAYS DE REDON ET VILAINE",
            "44",
            "44067",
            "243500741",
        ),
    ],
)
def test_scot(
    page: Page,
    uuid: str,
    titre: str,
    code_departement: str,
    code_commune: str,
    code_intercommunalite: str,
) -> None:
    common_principale(page, uuid, titre, code_departement)

    # Collectivité
    commune_page = CollectivitePage.navigate(page, code_commune)
    commune_page.expect_scot(titre, uuid)
    intercommunalite_page = CollectivitePage.navigate(page, code_intercommunalite)
    intercommunalite_page.expect_scot(titre, uuid)

    # # DDT Commune
    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ddt_commune_page.expect_scot(titre, uuid)

    # # DDT EPCI
    ddt_intercommunalite_page = DDTIntercommunalitePage.navigate(
        page, code_departement, code_intercommunalite
    )
    ddt_intercommunalite_page.expect_scot(titre, uuid)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune,code_intercommunalite",
    [
        (
            "d8ac57c3-20bc-4af3-9225-1431f54ac5fc",
            "Modification 4 PLU Douarnenez",  # Pas de titre en base
            "29",
            "29046",
            "242900645",
        ),
        (
            "d6a24592-d969-4ad0-b244-6e0f224a1ba1",
            "Modification 2 de PLU Goudargues",  # Titre en base
            "30",
            "30131",
            "200034692",
        ),
    ],
)
def test_procedure_secondaire_communale(
    page: Page,
    uuid: str,
    titre: str,
    code_departement: str,
    code_commune: str,
    code_intercommunalite: str,
):
    procedure_page = ProcedurePage.navigate(page, uuid)
    expect(procedure_page.titre).to_contain_text(titre)

    # DDT Procédures
    ddt_procedures = DDTProceduresPage.navigate(page, code_departement)
    ddt_procedures.expect_procedure(titre)
    ddt_procedures.expect_dialog(titre)

    # Collectivité
    commune_page = CollectivitePage.navigate(page, code_commune)
    commune_page.expect_procedure_secondaire_communale(titre, uuid)
    intercommunalite_page = CollectivitePage.navigate(page, code_intercommunalite)
    intercommunalite_page.expect_procedure_secondaire_communale(titre, uuid)

    # DDT Commune
    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ddt_commune_page.expect_procedure_secondaire_communale(titre, uuid)

    # DDT EPCI
    ddt_intercommunalite_page = DDTIntercommunalitePage.navigate(
        page, code_departement, code_intercommunalite
    )
    ddt_intercommunalite_page.expect_procedure_secondaire_communale(titre, uuid)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune,code_intercommunalite",
    [
        (
            "192283b5-a3ad-421a-b265-e20e23c45746",
            "Modification simplifiée n°1 de PLU CC du Lautrécois et du Pays d'Agout",  # Titre en base
            "81",
            "81078",
            "200034056",
        ),
        (
            "e97ce703-9f52-4fb9-b784-0caa7c322431",
            'Modification simplifiée 4 de PLUS CC Sidobre Vals et Plateaux Secteur "Vals et Plateaux et Monts de Lacaune"',  # Titre en base
            "81",
            "81305",
            "200066561",
        ),
        (
            "bdf8be09-6c0d-4fc5-b15e-594a562fa974",
            "Modification 1 PLUi CC Somme Sud-Ouest",  # Pas de titre en base
            "80",
            "80114",
            "200071181",
        ),
    ],
)
def test_procedure_secondaire_intercommunale(
    page: Page,
    uuid: str,
    titre: str,
    code_departement: str,
    code_commune: str,
    code_intercommunalite: str,
):
    procedure_page = ProcedurePage.navigate(page, uuid)
    expect(procedure_page.titre).to_contain_text(titre)

    # DDT Procédures
    ddt_procedures = DDTProceduresPage.navigate(page, code_departement)
    ddt_procedures.expect_procedure(titre)
    ddt_procedures.expect_dialog(titre)

    # Collectivité
    commune_page = CollectivitePage.navigate(page, code_commune)
    commune_page.expect_procedure_secondaire_intercommunale(titre, uuid)
    intercommunalite_page = CollectivitePage.navigate(page, code_intercommunalite)
    intercommunalite_page.expect_procedure_secondaire_intercommunale(titre, uuid)

    # DDT Commune
    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ddt_commune_page.expect_procedure_secondaire_intercommunale(titre, uuid)

    # DDT EPCI
    ddt_intercommunalite_page = DDTIntercommunalitePage.navigate(
        page, code_departement, code_intercommunalite
    )
    ddt_intercommunalite_page.expect_procedure_secondaire_intercommunale(titre, uuid)


@pytest.mark.parametrize(
    "uuid,titre,code_departement,code_commune",
    [
        (
            "e45a53d6-1c09-412a-8dab-3cb2d29c6971",
            "Révision PLU Bulgnéville",  # Pas de titre en base
            "88",
            "88079",
        ),
        (
            "0fe7e354-a655-42da-822b-5b8cb915ea75",
            "Elaboration 001 PLUi CC Touraine Val de Vienne",  # Pas de titre en base
            "37",
            "37005",
        ),
    ],
)
def test_ajout_procedure(page: Page, uuid, titre, code_departement, code_commune):
    procedure_page = ProcedurePage.navigate(page, uuid)
    expect(procedure_page.titre).to_contain_text(titre)

    ddt_commune_page = DDTCommunePage.navigate(page, code_departement, code_commune)
    ajout_procedure_page = ddt_commune_page.goto_ajouter_procedure()
    ajout_procedure_page.expect_procedure_parent(titre)


@pytest.mark.parametrize(
    "uuid,titre,code_departement",
    [
        (
            "ca5074d4-8ab5-43f4-9276-36a3042f0acc",
            "Elaboration PLUi CC Côtes de Meuse Woëvre",
            "55",
        ),
        (
            "0bb59a5a-a979-485a-9c8a-201ba063a086",
            "Elaboration PLUi CC de l'Aire à l'Argonne",
            "55",
        ),
        (
            "a4d2feee-5a0e-47fe-b8d0-b7eefcaea52b",
            "Elaboration PLUi CC Levroux Boischaut Champagne",
            "36",
        ),
        (
            "78d1bd1b-ae45-403d-85c6-2dda56f3a110",
            "Elaboration PLUi CC du Châtillonnais en Berry",
            "36",
        ),
    ],
)
def test_mes_collectivites_collectivite_porteuse_est_un_membre(
    page: Page, uuid, titre, code_departement
):
    procedure_page = ProcedurePage.navigate(page, uuid)
    expect(procedure_page.titre).to_contain_text(titre)

    ddt_collectivites = DDTCollectivitesPage.navigate(page, code_departement)
    ddt_collectivites.show_all_procedures()
    ddt_collectivites.expect_procedure(uuid, titre)
