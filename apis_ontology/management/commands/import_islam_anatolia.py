import pandas as pd
from tqdm import tqdm
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Reads Islam Anatolia data from a CSV file using pandas.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file to read.')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        try:
            df = pd.read_csv(csv_path)
            self.stdout.write(self.style.SUCCESS(f'Successfully read CSV file: {csv_path}'))


            # Prepare a status matrix: same shape as df, filled with None, but move 'source' as first column
            columns = list(df.columns)
            if 'source' in columns:
                columns.remove('source')
                status_columns = ['source'] + columns
            else:
                status_columns = columns
            status_matrix = pd.DataFrame(None, index=df.index, columns=status_columns)

            for idx, row in tqdm(df.iterrows(), total=len(df), desc="Importing…"):
                # Copy 'source' value as-is if present
                if 'source' in df.columns:
                    status_matrix.at[idx, 'source'] = row['source']
                for col in df.columns:
                    if col == 'source':
                        continue
                    value = row[col]
                    if pd.isna(value) or (isinstance(value, str) and value.strip() == ""):
                        status_matrix.at[idx, col] = "EMPTY"
                    else:
                        try:
                            # Example processing: replace with your logic
                            # process_value(value)
                            pass
                        except Exception as cell_error:
                            status_matrix.at[idx, col] = str(cell_error)


            # Write the status matrix to a CSV file with a timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            status_filename = f"import_status_{timestamp}.csv"
            status_matrix.to_csv(status_filename, index=True)
            self.stdout.write(self.style.SUCCESS(f"Status matrix written to {status_filename}"))

        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')
