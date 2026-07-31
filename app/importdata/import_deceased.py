from typing import Optional

from importdata.helpers import parse_date
from inquests.models import Deceased, Inquest, CauseOfDeath


INQUEST_REASON_BY_CODE = {
    'Mandatory inquest-Psychiatric Restraint' : Deceased.ReasonForInquest.PSYCHIATRIC_RESTRAINT,
    'Mandatory inquest-Custody-Inmate' : Deceased.ReasonForInquest.CUSTODY_INMATE,
    'Mandatory inquest-Custody-Police' : Deceased.ReasonForInquest.CUSTODY_POLICE,
    'Mandatory inquest-Construction' : Deceased.ReasonForInquest.CONSTRUCTION,
    'Mandatory inquest-Mining' : Deceased.ReasonForInquest.MINING,
    'Mandatory inquest-Child CYFSA': Deceased.ReasonForInquest.CHILD_CYFSA,
    'Discretionary inquest' : Deceased.ReasonForInquest.DISCRETIONARY,
    'Pending inquest' : Deceased.ReasonForInquest.PENDING,
}


def import_deceased(data: dict) -> Optional[Deceased]:
    inquest_key = data["4_Case_e"].lower()
    if not inquest_key:
        inquest = None
    else:
        try:
            inquest = Inquest.objects.get(import_metadata=inquest_key)
        except Inquest.DoesNotExist:
            raise ValueError(f"No inquest found for key: {inquest_key}")
        except Inquest.MultipleObjectsReturned:
            raise ValueError(f"Multiple inquests found for key: {inquest_key}")

    cause_of_death_name = data["41_Cause_Code_e"]
    if not cause_of_death_name:
        cause_of_death = None
    else:
        cause_of_death = CauseOfDeath.objects.get(name=cause_of_death_name)

    age_string = data['21_Age_v']
    if not age_string:
        age = None
    else:
        age = int(age_string)

    return Deceased.objects.create(
        first_name=data['2_Name_e : First'],
        middle_name=data['2_Name_e : Middle'],
        last_name=data['2_Name_e : Last'].capitalize(),
        age=age,
        date_of_birth=parse_date(data['26_DateOfBirth_v']),
        date_of_death=parse_date(data['25_DateDied_v']),
        sex=data["22a_Sex_Code_c"],
        manner=data["44_Manner_e"].upper(),
        reason_for_inquest=data["31_InqReason_e"],
        cause_description=data["43_DeathCauseText_e"],
        cause=cause_of_death,
        inquest=inquest,
    )
