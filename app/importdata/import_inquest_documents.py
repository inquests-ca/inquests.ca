from typing import Optional

from importdata.helpers import clean_name, parse_date
from inquests.models import Inquest, InquestDocument

DOCUMENT_TYPE_BY_CODE = {
    'Inq_Verdict_and_Report': InquestDocument.DocumentType.VERDICT_AND_EXPLANATION,
    'Inq_Responses': InquestDocument.DocumentType.RESPONSE_TO_RECOMMENDATIONS,
    'Inq_StandingRuling': InquestDocument.DocumentType.STANDING_RULING,
    'Inq_Scope': InquestDocument.DocumentType.SCOPE,
    'Inq_Media': InquestDocument.DocumentType.MEDIA,
}


def import_inquest_document(data: dict) -> Optional[InquestDocument]:
    # The export mixes Inquest and Authority documents in one file/columns.
    case_type = (data.get('014_Doc_Case_Type') or '').strip()
    if case_type != 'Inquest':
        return None

    name = clean_name(data.get('2_Name_e'))

    doc_type_code = (data.get('4_DocType_c') or '').strip()
    try:
        document_type = DOCUMENT_TYPE_BY_CODE[doc_type_code]
    except KeyError:
        raise ValueError(f'Document "{name}" has unrecognized document type: "{doc_type_code}".')

    inquest_key = (data.get('InqNameCalc') or '').strip().lower()
    try:
        inquest = Inquest.objects.get(import_metadata=inquest_key)
    except Inquest.DoesNotExist:
        raise ValueError(f'Document "{name}": no inquest found matching "{inquest_key}".')
    except Inquest.MultipleObjectsReturned:
        raise ValueError(f'Document "{name}": multiple inquests found matching "{inquest_key}".')

    return InquestDocument.objects.create(
        name=name,
        document_type=document_type,
        date=parse_date(data.get('021_DocDate_e')),
        source=(data.get('050_Source_c') or '').strip(),
        link=(data.get('81d_PublicLinkURL_c') or '').strip(),
        inquest=inquest,
    )
