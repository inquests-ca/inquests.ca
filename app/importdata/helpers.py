import re
from datetime import datetime

DATE_FORMAT = '%m/%d/%Y'
HTML_TAG_RE = re.compile(r'<[^>]+>')
TRAILING_JUNK_RE = re.compile(r'[\[\-\s]+$')


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


def split_list(value):
    """Split a comma-separated CSV cell into a clean, de-duplicated list."""
    if not value:
        return []
    items = []
    seen = set()
    for raw in value.split(','):
        item = clean_name(raw)
        if item and item not in seen:
            seen.add(item)
            items.append(item)
    return items