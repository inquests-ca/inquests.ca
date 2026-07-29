import re
from typing import Optional

from common.models import Jurisdiction
from importdata.helpers import clean_name, strip_html, parse_date, split_list
from inquests.models import (
    InquestDocument,
    Inquest,
    PresidingOfficer,
    RecommendationRecipient,
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
        presiding_officer=get_presiding_officer(data),
        import_metadata=clean_name(data["i_InqNameCalc"]).lower(),
    )

    # inquest.keywords.set(get_or_create_many(InquestKeyword, data.get('48_AllTxt_c')))
    # link_recommendation_recipients(inquest, data.get('RecRecipients'))

    # import_document(inquest, data)

    return inquest


def is_name_of_deceased(name: str) -> bool:
    name_re = re.compile(r'^[a-zA-Z\-.]+, [a-zA-Z\-.]+(\s[a-zA-Z\-.]+)?(\s+\[\w{2}-\d{4}])?$')
    return name_re.match(name) is not None


def remove_trailing_metadata(name: str) -> str:
    trailing_metadata_re = re.compile(r'\s+\[\w{2}-\d{4}]?$')
    return trailing_metadata_re.sub("", name)


def get_presiding_officer(data: dict) -> PresidingOfficer:
    presiding_officer = data.get('610_Inq_Presiding_v')
    if not presiding_officer:
        raise ValueError(f"No presiding officer provided.")

    name_parts = presiding_officer.split(',')
    if len(name_parts) != 2:
        raise ValueError(f"Unexpected presiding officer format: {presiding_officer}")

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


def link_recommendation_recipients(inquest, value):
    for name in split_list(value):
        recipient, _ = RecommendationRecipient.objects.get_or_create(name=name)
        recipient.inquests.add(inquest)


def import_document(inquest, row):
    doc_name = clean_name(row.get('101_Primary_Doc_e'))
    if not doc_name:
        return
    doc_date = parse_date(row.get('21_Date_c')) or parse_date(row.get('21a_AuthDate_c'))
    if doc_date is None:
        # InquestDocument.date is required; skip rather than guess.
        raise ValueError(f'Skipping document "{doc_name}" for "{inquest.first_name}": no usable date.')
    InquestDocument.objects.update_or_create(
        inquest=inquest,
        name=doc_name,
        defaults={
            'date': doc_date,
            'source': (row.get('12_Source_c') or '').strip(),
            'link': (row.get('10b_Permanent link') or '').strip(),
        },
    )
