from django import template

register = template.Library()


@register.inclusion_tag('common/_form_field.html')
def render_field(field, label=None):
    """Renders a bound form field as a labeled `.field` block: label, the
    widget itself, and any validation errors."""
    return {'field': field, 'label': label or field.label}


@register.inclusion_tag('common/_form_checkbox_field.html')
def render_checkbox_field(field, label=None):
    """Renders a bound checkbox field with the label wrapping the input,
    matching the edit-form checkbox layout (e.g. Judicial Review)."""
    return {'field': field, 'label': label or field.label}


@register.inclusion_tag('common/_form_section.html')
def form_section(title, field):
    """Renders a `.detail-section` containing a single form field, used for
    the free-text and multi-select fields on edit pages (e.g. Overview,
    Keywords) where the section heading itself doubles as the field label."""
    return {'title': title, 'field': field}
