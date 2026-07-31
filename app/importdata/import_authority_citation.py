from typing import Optional

from authorities.models import Authority
from importdata.import_authority import remove_trailing_year


def import_authority_citation(data: dict) -> Optional[Authority]:
    citer_name = remove_trailing_year((data.get('2_Citer') or '').strip())
    cited_name = remove_trailing_year((data.get('3_Cited') or '').strip())

    if not cited_name:
        return None

    try:
        citer = Authority.objects.get(name=citer_name)
    except Authority.DoesNotExist:
        raise ValueError(f'Citing authority not found: {citer_name}')

    try:
        cited = Authority.objects.get(name=cited_name)
    except Authority.DoesNotExist:
        raise ValueError(f'Cited authority not found: {cited_name}')

    citer.citations.add(cited)

    return citer
