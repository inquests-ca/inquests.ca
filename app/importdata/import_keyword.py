from typing import Optional, Union

from authorities.models import AuthorityKeyword
from inquests.models import InquestKeyword


def import_keyword(data: dict) -> Optional[Union[AuthorityKeyword, InquestKeyword]]:
    name = data["6_IssueSubtype"]
    if name == "Not_yet_classified":
        return None

    keyword_type = (data.get('2_InqOrAuth_e') or '').strip()
    category = data["5_IssueType_e"].upper()
    description = data["Description"]
    synonyms = data["Synonyms"]

    if keyword_type == 'Authority':
        return AuthorityKeyword.objects.create(
            name=name,
            category=category,
            description=description,
            synonyms=synonyms,
        )

    if keyword_type == 'Inquest':
        return InquestKeyword.objects.create(
            name=name,
            category=category,
            description=description,
            synonyms=synonyms,
        )

    raise ValueError(f'Unknown keyword type: {keyword_type}')
