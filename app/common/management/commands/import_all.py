import csv
import os
from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, DataError

from importdata.import_authority import import_authority
from importdata.import_authority_citation import import_authority_citation
from importdata.import_authority_document import import_authority_document
from importdata.import_authority_level import import_authority_level
from importdata.import_cause_of_death import import_cause_of_death
from importdata.import_deceased import import_deceased
from importdata.import_group import import_group
from importdata.import_inquest import import_inquest
from importdata.import_inquest_documents import import_inquest_document
from importdata.import_jurisdiction import import_jurisdiction
from importdata.import_keyword import import_keyword
from importdata.import_participant import import_participant
from importdata.import_party import import_party
from importdata.import_party_type import import_party_type


# Ordered such that imports can be executed in descending order
# (e.g., 'inquest_document' relies on 'inquest').
IMPORT_FUNCTIONS = OrderedDict([
    ('jurisdiction', (import_jurisdiction, "l_jurisdictions.csv")),
    ('keyword', (import_keyword, "l_caseissues.csv")),
    ('group', (import_group, "relatedcasegroup.csv")),
    ('cause_of_death', (import_cause_of_death, "l_dcsdcausecodes.csv")),
    ('party_type', (import_party_type, "l_inqpartytype.csv")),
    ('party', (import_party, "l_inqrecipients.csv")),
    ('participant', (import_participant, "persons.csv")),
    ('authority_level', (import_authority_level, "l_authlevels.csv")),
    ('authority', (import_authority, "cases.csv")),
    ('authority_document', (import_authority_document, "documents.csv")),
    ('authority_citation', (import_authority_citation, "citations.csv")),
    ('inquest', (import_inquest, "cases.csv")),
    ('inquest_document', (import_inquest_document, "documents.csv")),
    ('deceased', (import_deceased, "deceased.csv")),
])


class Command(BaseCommand):
    def handle(self, *args, **options):
        for import_type, (import_function, filename) in IMPORT_FUNCTIONS.items():
            path = os.path.join("/usr/src/data", filename)
            try:
                fh = open(path, newline='', encoding='utf-8-sig')
            except OSError as exc:
                raise CommandError(f'Could not open {path}: {exc}')

            created = skipped = errors = 0
            with fh:
                reader = csv.DictReader(fh)
                for i, row in enumerate(reader):
                    with transaction.atomic():
                        try:
                            result = import_function(row)
                        except (ValueError, DataError) as exc:
                            self.stdout.write(self.style.WARNING(f"Row {i + 1}: {exc}"))
                            errors += 1
                            continue

                        if result is None:
                            skipped += 1
                        else:
                            created += 1

            self.stdout.write(self.style.SUCCESS(
                f'Imported {import_type}: {created} created, {skipped} skipped, {errors} errors.'
            ))
