from core.models import Collectivite, Departement, Region
from users.enums import PosteType, ProfileSideType
from users.models import Profile, User

region = Region.objects.get(code_insee="76")
departements = Departement.objects.filter(
    code_insee__in=[
        "09",
        "11",
        "12",
        "30",
        "31",
        "32",
        "34",
        "46",
        "48",
        "65",
        "66",
        "81",
        "82",
    ]
).order_by("code_insee")
departements_as_list = list(departements.values_list("code_insee", flat=True))
departement = departements.first()
# Collectivite
user_collectivite_side = User.objects.get(email="test-collectivite@truc.com")
collectivite = Collectivite.objects.filter(departement=departement).first()
Profile.objects.get_or_create(
    user=user_collectivite_side,
    firstname="Georges-Eugène",
    lastname="Haussmann",
    email=user_collectivite_side.email,
    poste=PosteType.EMPLOYE_MAIRIE,
    departement=departement.code_insee,
    collectivite_id=collectivite.code_insee_unique,
    tel="0600000000",
    verified=True,
    side=ProfileSideType.COLLECTIVITE,
    region=region.code_insee,
    is_admin=False,
    is_staff=False,
)

# PPA
user_ppa_side = User.objects.get(email="test-ppa@truc.com")
Profile.objects.get_or_create(
    user=user_ppa_side,
    firstname="Charles-Édouard",
    lastname="Jeanneret",
    email=user_ppa_side.email,
    poste=PosteType.REGION,
    departement=departement.code_insee,
    departements=departements_as_list,
    tel="0600000000",
    verified=True,
    side=ProfileSideType.PPA,
    region=region.code_insee,
    is_admin=False,
    is_staff=False,
)

user_ddt_side = User.objects.get(email="test-ddt@truc.com")
Profile.objects.get_or_create(
    user=user_ddt_side,
    firstname="Oscar",
    lastname="Niemeyer",
    email=user_ddt_side.email,
    poste=PosteType.DDT,
    departement=departement.code_insee,
    tel="0600000000",
    verified=True,
    side=ProfileSideType.ETAT,
    region=region.code_insee,
    is_admin=False,
    is_staff=False,
)
