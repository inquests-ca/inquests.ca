import re
from typing import Optional

from authorities.models import Authority, AuthorityGroup, AuthorityKeyword, AuthorityLevel
from common.models import Jurisdiction
from importdata.helpers import clean_name, strip_html, parse_yes_no, parse_case_keywords, parse_case_groups


def import_authority(data: dict) -> Optional[Authority]:
    # The export mixes Authority and Inquest rows in one file/columns.
    record_type = (data.get('11_AuthOrInq_e') or '').strip()
    if record_type and record_type != 'Authority':
        return None

    name = clean_name(data.get('2a_Auth_Name_e'))
    if not name:
        raise ValueError('Missing authority name.')

    authority = Authority.objects.create(
        name=name,
        overview=(data.get('041a_Overview_e') or '').strip(),
        summary=strip_html(data.get('43a_Synopsis_e')),
        notes=strip_html(data.get('44_Interpretation_Notes_e')),
        quotes=strip_html(data.get('45_Quotes_e')),
        key_case_reason=(data.get('032_KeyCaseTxt_e') or '').strip(),
        is_judicial_review=parse_yes_no(data.get('031_IsJR_e')),
        jurisdiction=get_jurisdiction(data.get('12b_Jurisdiction_e')),
    )

    authority.keywords.set(get_keywords(data.get('51_CaseIssues_e')))
    authority.groups.set(get_groups(data.get('116_RelatedCaseGroups_e')))

    return authority


def get_keywords(value: str) -> list[AuthorityKeyword]:
    keywords = []
    for category, name in parse_case_keywords(value):
        try:
            keywords.append(AuthorityKeyword.objects.get(category=category, name=name))
        except AuthorityKeyword.DoesNotExist:
            raise ValueError(f'Authority keyword not found: {category}-{name}')
    return keywords


def get_groups(value: str) -> list[AuthorityGroup]:
    groups = []
    for name in parse_case_groups(value, 'Authorities - '):
        try:
            groups.append(AuthorityGroup.objects.get(name=name))
        except AuthorityGroup.DoesNotExist:
            raise ValueError(f'Authority group not found: {name}')
    return groups


def get_level(value: str) -> Optional[AuthorityLevel]:
    rank = (value or '').strip()
    if not rank or rank == '0':
        return None

    try:
        return AuthorityLevel.objects.get(rank=int(rank))
    except AuthorityLevel.DoesNotExist:
        raise ValueError(f'Authority level not found for rank: {rank}')


def get_jurisdiction(value: str) -> Optional[Jurisdiction]:
    jurisdiction_name = (value or '').strip()
    if not jurisdiction_name:
        return None

    try:
        return Jurisdiction.objects.get(name=jurisdiction_name)
    except Jurisdiction.DoesNotExist:
        raise ValueError(f'Jurisdiction not found: {jurisdiction_name}')


def remove_trailing_year(name: str) -> str:
    trailing_year_re = re.compile(r'\s+\[[^\]]+]$')
    return trailing_year_re.sub("", name)
