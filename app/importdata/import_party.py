from typing import Optional

from inquests.models import PartyType, Party


def import_party(data: dict) -> Optional[Party]:
    party_type_name = (data.get('3_InqRecptType_e') or '').strip()
    try:
        party_type = PartyType.objects.get(name=party_type_name)
    except PartyType.DoesNotExist:
        raise ValueError(f'Party type not found: {party_type_name}')

    return Party.objects.create(
        name=(data.get('4_Recpt_Name_e') or '').strip(),
        also_known_as=(data.get('6_AlsoKnownAs_e') or '').strip(),
        notes=(data.get('Remarks') or '').strip(),
        party_type=party_type,
    )
