from typing import Optional

from inquests.models import Participant, Role

CATEGORY_BY_LABEL = {
    'Inquest Counsel': Role.Category.INQUEST_COUNSEL,
    'Other': Role.Category.OTHER,
    'POI': Role.Category.POI,
    'Party Counsel': Role.Category.PARTY_COUNSEL,
    'Police': Role.Category.POLICE,
    'Program Administrator': Role.Category.PROGRAM_ADMINISTRATOR,
    'Support': Role.Category.SUPPORT,
}


def import_participant(data: dict) -> Optional[Participant]:
    last_name = (data.get('Name : Last') or '').strip()
    if not last_name or last_name == 'zz_UNSPECIFIED':
        return None

    participant = Participant.objects.create(
        first_name=(data.get('Name : First') or '').strip(),
        last_name=last_name,
    )

    participant.roles.set(get_roles(data.get('Role'), data.get('RoleSuppl')))

    return participant


def get_roles(role_value: str, role_suppl_value: str) -> list[Role]:
    # 'RoleSuppl' holds comma-separated 'Category-Detail' tokens (e.g.
    # 'POI-Physician'), but doesn't always have an entry for every category
    # listed in 'Role' (e.g. Role='POI, Party Counsel' but
    # RoleSuppl='POI-Lawyer' only) -- those categories just get a role with
    # no further detail.
    names_by_category = {}
    for token in (role_suppl_value or '').split(','):
        token = token.strip()
        if not token or token == 'None':
            continue
        category_label, _, name = token.partition('-')
        names_by_category.setdefault(category_label.strip(), []).append(name.strip())

    roles = []
    for category_label in (role_value or '').split(','):
        category_label = category_label.strip()
        if not category_label:
            continue

        try:
            category = CATEGORY_BY_LABEL[category_label]
        except KeyError:
            raise ValueError(f'Unrecognized role category: {category_label}')

        for name in names_by_category.get(category_label) or ['']:
            role, _ = Role.objects.get_or_create(category=category, name=name)
            roles.append(role)

    return roles
