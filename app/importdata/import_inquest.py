import re
from typing import Optional

from common.models import Jurisdiction
from importdata.helpers import clean_name, strip_html, parse_date, parse_case_keywords, parse_case_groups
from inquests.models import (
    Inquest,
    InquestGroup,
    InquestKeyword,
    PresidingOfficer, Party, PartyType,
)


def import_inquest(data: dict) -> Optional[Inquest]:
    # The export mixes Authority and Inquest rows in one file/columns.
    record_type = (data.get('11_AuthOrInq_e') or '').strip()
    if record_type and record_type != 'Inquest':
        return None

    name = ""
    if not is_name_of_deceased(data['2_Case_Name_c']):
        name = remove_trailing_metadata(data['2_Case_Name_c'])

    overview = (data.get('041a_Overview_e') or '').strip()
    if overview.startswith('-'):
        overview = overview[1:]

    inquest = Inquest.objects.create(
        name=name,
        overview=overview,
        summary=strip_html(data.get('43a_Synopsis_e')),
        key_case_reason=(data.get('032_KeyCaseTxt_e') or '').strip(),
        start_date=parse_date(data.get('21b_InqStartDate_e')),
        end_date=parse_date(data.get('21c_InqEndDate_e')),
        jurisdiction=Jurisdiction.objects.get(name=data['12b_Jurisdiction_e']),
        presiding_officer=get_presiding_officer(name=data.get('610_Inq_Presiding_v')),
        import_metadata=clean_name(data["i_InqNameCalc"]).lower(),
    )

    inquest.keywords.set(get_keywords(data.get('51_CaseIssues_e')))
    inquest.groups.set(get_groups(data.get('116_RelatedCaseGroups_e')))
    inquest.recommendation_recipients.set(get_parties(data.get('RecRecipients')))

    return inquest


def is_name_of_deceased(name: str) -> bool:
    name_re = re.compile(r'^[a-zA-Z\-.]+, [a-zA-Z\-.]+(\s[a-zA-Z\-.]+)?(\s+\[\w{2}-\d{4}])?$')
    return name_re.match(name) is not None


def remove_trailing_metadata(name: str) -> str:
    trailing_metadata_re = re.compile(r'\s+\[\w{2}-\d{4}]?$')
    return trailing_metadata_re.sub("", name)


def get_presiding_officer(name: str) -> PresidingOfficer:
    if not name:
        raise ValueError(f"No presiding officer provided.")

    name_parts = name.split(',')
    if len(name_parts) != 2:
        raise ValueError(f"Unexpected presiding officer format: {name}")

    last_name, first_name = name_parts
    first_name = first_name.strip()
    last_name = last_name.strip()
    try:
        return PresidingOfficer.objects.get(
            first_name=first_name,
            last_name=last_name
        )
    except PresidingOfficer.DoesNotExist:
        raise ValueError(f"Presiding officer not found: {first_name} {last_name}")


def get_parties(value: str) -> list[Party]:
    parties = []
    for party_type_name, name in parse_case_recipients(value):
        try:
            party = Party.objects.get(party_type__name=party_type_name, name=name)
        except Party.DoesNotExist:
            raise ValueError(f'Inquest party not found: {party_type_name}-{name}')
        parties.append(party)
    return parties


def parse_case_recipients(value: str) -> list[tuple[str, str]]:
    if not value:
        return []

    party_type_names = sorted(
        PartyType.objects.values_list('name', flat=True),
        key=len,
        reverse=True,
    )
    alternation = '|'.join(re.escape(name) for name in party_type_names)
    split_re = re.compile(rf',(?=(?:{alternation})(?: - |,|$))')

    pairs = []
    seen = set()
    for token in split_re.split(value):
        token = token.strip()
        if not token:
            continue

        pair = None
        for party_type_name in party_type_names:
            prefix = f'{party_type_name} - '
            if token.startswith(prefix):
                pair = (party_type_name, token[len(prefix):].strip())
                break

        if pair is None:
            if token in party_type_names:
                pair = (token, '')
            else:
                raise ValueError(f'Unrecognized party: {token}')

        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    return pairs


def get_keywords(value: str) -> list[InquestKeyword]:
    keywords = []
    for category, name in parse_case_keywords(value):
        try:
            keywords.append(InquestKeyword.objects.get(category=category, name=name))
        except InquestKeyword.DoesNotExist:
            raise ValueError(f'Inquest keyword not found: {category}-{name}')
    return keywords


def get_groups(value: str) -> list[InquestGroup]:
    groups = []
    for name in parse_case_groups(value, 'Inquests - '):
        try:
            groups.append(InquestGroup.objects.get(name=name))
        except InquestGroup.DoesNotExist:
            raise ValueError(f'Inquest group not found: {name}')
    return groups
