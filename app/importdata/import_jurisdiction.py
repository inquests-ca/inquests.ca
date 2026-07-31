from typing import Optional

from common.models import Jurisdiction
from importdata.helpers import parse_yes_no


def import_jurisdiction(data: dict) -> Optional[Jurisdiction]:
    return Jurisdiction.objects.create(
        name=data['Name'],
        code=data['Code'],
        does_conduct_inquests=parse_yes_no(data.get('IsInqJur')),
        name_for_inquest=(data.get('InqOrFI') or '').strip(),
    )
