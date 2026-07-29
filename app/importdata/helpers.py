import re
from datetime import datetime

DATE_FORMAT = '%m/%d/%Y'
HTML_TAG_RE = re.compile(r'<[^>]+>')
TRAILING_JUNK_RE = re.compile(r'[\[\-\s]+$')
GROUP_TOKEN_SPLIT_RE = re.compile(r',(?=(?:Inquests|Authorities) - )')


def parse_date(value):
    value = (value or '').strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        return None


def parse_yes_no(value):
    return (value or '').strip().lower() == 'yes'


def strip_html(value):
    return HTML_TAG_RE.sub('', value or '').strip()


def clean_name(value):
    """Strip stray trailing punctuation left over from truncated CSV
    fields, e.g. 'ABDI, Abdirhman Ali [' -> 'ABDI, Abdirhman Ali'."""
    return TRAILING_JUNK_RE.sub('', (value or '').strip()).strip()


def parse_case_keywords(value: str) -> list[tuple[str, str]]:
    if not value:
        return []
    pairs = []
    seen = set()
    for token in value.split(','):
        token = token.strip()
        if not token:
            continue
        category, _, name = token.partition('-')
        pair = (category.upper(), name)
        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    return pairs


def parse_case_groups(value: str, prefix: str) -> list[str]:
    if not value:
        return []
    names = []
    seen = set()
    for token in GROUP_TOKEN_SPLIT_RE.split(value):
        token = token.strip()
        if not token.startswith(prefix):
            continue
        name = token[len(prefix):].strip()
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names
