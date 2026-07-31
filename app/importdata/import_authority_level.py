from typing import Optional

from authorities.models import AuthorityLevel


def import_authority_level(data: dict) -> Optional[AuthorityLevel]:
    return AuthorityLevel.objects.create(
        name=data['Levels Name'].strip(),
        rank=int(data['Rank']),
    )
