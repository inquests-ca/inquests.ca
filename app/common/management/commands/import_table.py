import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, DataError

from common.management.commands.import_all import IMPORT_FUNCTIONS


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, required=False, help='Path to the CSV file to import.')
        parser.add_argument('import_type', choices=IMPORT_FUNCTIONS.keys())

    def handle(self, *args, **options):
        import_type = options['import_type']
        import_function, filename = IMPORT_FUNCTIONS[import_type]

        if options.get('csv_path'):
            path = options['csv_path']
        else:
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
            f'Import complete: {created} created, {skipped} skipped, {errors} errors.'
        ))
