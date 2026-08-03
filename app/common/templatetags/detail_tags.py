from django import template

register = template.Library()


@register.inclusion_tag('common/_detail_paragraph.html')
def detail_paragraph(title, text):
    """Renders an optional `.detail-section` paragraph -- e.g. Overview,
    Summary -- hidden entirely when `text` is blank."""
    return {'title': title, 'text': text}


@register.inclusion_tag('common/_linked_tag_list.html')
def linked_tag_list(title, items, list_url_name, param_name='keywords'):
    """Renders an optional `.detail-section` of tag pills that link back to
    the filtered search page (e.g. Keywords), one `?param_name=item.id` per
    tag. Hidden entirely when `items` is empty."""
    return {'title': title, 'items': items, 'list_url_name': list_url_name, 'param_name': param_name}


@register.inclusion_tag('common/_plain_tag_list.html')
def plain_tag_list(title, items):
    """Renders an optional `.detail-section` of plain (unlinked) tag pills
    -- e.g. Related Groups. Hidden entirely when `items` is empty."""
    return {'title': title, 'items': items}
