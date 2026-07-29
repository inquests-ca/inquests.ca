import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, DataError

from importdata.import_authority import import_authority
from importdata.import_cause_of_death import import_cause_of_death
from importdata.import_deceased import import_deceased
from importdata.import_inquest import import_inquest
from importdata.import_jurisdiction import import_jurisdiction
from importdata.import_keyword import import_keyword
from importdata.import_presiding_officer import import_presiding_officer


IMPORT_FUNCTIONS = {
    'authority': import_authority,
    'inquest': import_inquest,
    'deceased': import_deceased,
    'cause_of_death': import_cause_of_death,
    'jurisdiction': import_jurisdiction,
    'presiding_officer': import_presiding_officer,
    'keyword': import_keyword,
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file to import.')
        parser.add_argument('import_type', choices=IMPORT_FUNCTIONS.keys())

    def handle(self, *args, **options):
        import_type = options['import_type']
        import_function = IMPORT_FUNCTIONS[import_type]

        path = options['csv_path']
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
            f'Import complete: {created} created, {skipped} skipped, {errors} errors.'
        ))
