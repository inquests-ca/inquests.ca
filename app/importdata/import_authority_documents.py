from typing import Optional

from authorities.models import Authority, AuthorityDocument
from importdata.helpers import clean_name, parse_date
from importdata.import_authority import remove_trailing_year


DOCUMENT_TYPE_BY_CODE = {
    'Auth_Case_Law': AuthorityDocument.DocumentType.CASE_LAW,
    'Auth_Reference': AuthorityDocument.DocumentType.REFERENCE,
    'Auth_Commission_Report': AuthorityDocument.DocumentType.COMMISSION_REPORT,
    'Auth_Statute': AuthorityDocument.DocumentType.STATUTE,
    'Media-Authority': AuthorityDocument.DocumentType.MEDIA,
    'Auth_Summary': AuthorityDocument.DocumentType.SUMMARY,
}


def import_authority_document(data: dict) -> Optional[AuthorityDocument]:
    # The export mixes Inquest and Authority documents in one file/columns.
    case_type = (data.get('014_Doc_Case_Type') or '').strip()
    if case_type != 'Authority':
        return None

    name = clean_name(data.get('2_Name_e'))

    date = parse_date(data.get('021_DocDate_e'))

    doc_type_code = (data.get('4_DocType_c') or '').strip()
    try:
        document_type = DOCUMENT_TYPE_BY_CODE[doc_type_code]
    except KeyError:
        raise ValueError(f'Document "{name}" has unrecognized document type: "{doc_type_code}".')

    authority_name = remove_trailing_year((data.get('AuthInqNameCalc') or '').strip())
    try:
        authority = Authority.objects.get(name=authority_name)
    except Authority.DoesNotExist:
        raise ValueError(f'Document "{name}": no authority found matching "{authority_name}".')
    except Authority.MultipleObjectsReturned:
        raise ValueError(f'Document "{name}": multiple authorities found matching "{authority_name}".')

    return AuthorityDocument.objects.create(
        name=name,
        document_type=document_type,
        date=date,
        source=(data.get('050_Source_c') or '').strip(),
        link=(data.get('81d_PublicLinkURL_c') or '').strip(),
        authority=authority,
    )
