from typing import Optional

from inquests.models import CauseOfDeath


def import_cause_of_death(data: dict) -> Optional[CauseOfDeath]:
    return CauseOfDeath.objects.create(
        name=data['2_Name_v'],
    )
