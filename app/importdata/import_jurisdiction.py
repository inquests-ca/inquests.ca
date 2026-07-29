from typing import Optional

from common.models import Jurisdiction


def import_jurisdiction(data: dict) -> Optional[Jurisdiction]:
    return Jurisdiction.objects.create(
        name=data['Name'],
        code=data['Code'],
    )
