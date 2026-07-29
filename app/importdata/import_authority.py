from typing import Optional

from authorities.models import Authority
from common.models import Jurisdiction
from importdata.helpers import clean_name, strip_html, parse_yes_no


def import_authority(data: dict) -> Optional[Authority]:
    # The export mixes Authority and Inquest rows in one file/columns.
    record_type = (data.get('11_AuthOrInq_e') or '').strip()
    if record_type and record_type != 'Authority':
        return None

    name = clean_name(data.get('2a_Auth_Name_e'))
    if not name:
        raise ValueError('Missing authority name.')

    jurisdiction = None
    jurisdiction_name = data['12b_Jurisdiction_e']
    if jurisdiction_name:
        jurisdiction = Jurisdiction.objects.get(name=jurisdiction_name)

    authority = Authority.objects.create(
        name=name,
        overview=(data.get('041a_Overview_e') or '').strip(),
        summary=strip_html(data.get('43a_Synopsis_e')),
        notes=strip_html(data.get('44_Interpretation_Notes_e')),
        quotes=strip_html(data.get('45_Quotes_e')),
        key_case_reason=(data.get('032_KeyCaseTxt_e') or '').strip(),
        is_judicial_review=parse_yes_no(data.get('031_IsJR_e')),
        jurisdiction=jurisdiction,
    )

    return authority
