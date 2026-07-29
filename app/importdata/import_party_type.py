from typing import Optional

from inquests.models import PartyType


def import_party_type(data: dict) -> Optional[PartyType]:
    name = (data.get('InqPartyType Name') or '').strip()
    if not name:
        raise ValueError('Missing party type name.')

    return PartyType.objects.create(
        name=name,
        description=(data.get('Description') or '').strip(),
    )
