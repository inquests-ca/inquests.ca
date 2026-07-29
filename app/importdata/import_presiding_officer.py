from typing import Optional

from inquests.models import PresidingOfficer


def import_presiding_officer(data: dict) -> Optional[PresidingOfficer]:
    if data['Role'] != 'POI' or data['Name : Last'] == 'zz_UNSPECIFIED':
        return None

    return PresidingOfficer.objects.create(
        first_name=data['Name : First'],
        last_name=data['Name : Last'],
    )
