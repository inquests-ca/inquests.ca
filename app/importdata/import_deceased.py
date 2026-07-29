from typing import Optional

from importdata.helpers import parse_date
from inquests.models import Deceased, Inquest, CauseOfDeath


def import_deceased(data: dict) -> Optional[Deceased]:
    inquest_name = f"{data['2_Name_e : Last']}, {data['2_Name_e : First']} {data['2_Name_e : Middle']}".strip().lower()
    try:
        inquest = Inquest.objects.get(import_metadata=inquest_name)
    except Inquest.DoesNotExist:
        raise ValueError(f"No inquest found corresponding to deceased: {inquest_name}")
    except Inquest.MultipleObjectsReturned:
        raise ValueError(f"Multiple inquests found corresponding to deceased: {inquest_name}")

    cause_of_death_name = data["41_Cause_Code_e"]
    if not cause_of_death_name:
        cause_of_death = None
    else:
        cause_of_death = CauseOfDeath.objects.get(name=cause_of_death_name)

    return Deceased.objects.create(
        first_name=data['2_Name_e : First'],
        middle_name=data['2_Name_e : Middle'],
        last_name=data['2_Name_e : Last'].capitalize(),
        date_of_birth=parse_date(data['26_DateOfBirth_v']),
        date_of_death=parse_date(data['25_DateDied_v']),
        sex=data["22a_Sex_Code_c"],
        cause=cause_of_death,
        manner=data["44_Manner_e"].upper(),
        inquest=inquest,
    )
