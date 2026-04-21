from django.db.models import Index


class OversizedIndex(Index):
    max_name_length = 90
