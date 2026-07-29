from typing import Optional, Union

from authorities.models import AuthorityGroup
from importdata.helpers import strip_html
from inquests.models import InquestGroup


def import_group(data: dict) -> Optional[Union[AuthorityGroup, InquestGroup]]:
    group_type = (data.get('3_GroupType') or '').strip()
    name = data["2a_RelatedCaseGroupName_e"]
    notes = strip_html(data["4a_Remarks_e"])

    if group_type == 'Authorities':
        return AuthorityGroup.objects.create(
            name=name,
            notes=notes,
        )

    if group_type == 'Inquests':
        return InquestGroup.objects.create(
            name=name,
            notes=notes,
        )

    raise ValueError(f'Unknown group type: {group_type}')
