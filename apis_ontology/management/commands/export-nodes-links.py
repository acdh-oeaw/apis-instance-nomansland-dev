"""
Management command to export nodes and links to CSV files
"""

from django.core.management.base import BaseCommand
from tqdm import tqdm
from apis_core.relations.models import Relation
import pandas as pd


class Command(BaseCommand):
    help = "Export nodes and links to CSV files"

    def handle(self, *args, **options):
        def remove_duplicates(data):
            unique_data = []
            seen = set()
            for d in data:
                t = tuple(sorted(d.items()))
                if t not in seen:
                    seen.add(t)
                    unique_data.append(d)

            return unique_data

        nodes = []
        links = []
        for rel in tqdm(Relation.objects.select_subclasses().all()):
            nodes.append(
                {
                    "id": rel.subj.pk,
                    "type": rel.subj.__class__.__name__,
                    "label": str(rel.subj),
                }
            )

            nodes.append(
                {
                    "id": rel.obj.pk,
                    "type": rel.obj.__class__.__name__,
                    "label": str(rel.obj),
                }
            )
            links.append(
                {
                    "id": rel.pk,
                    "source": rel.subj.pk,
                    "target": rel.obj.pk,
                    "type": rel.name(),
                }
            )

        nodes = remove_duplicates(nodes)
        # create unique filename for nodes with date and time
        filename_suffix = f"{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pd.DataFrame(nodes).to_csv(f"nodes_{filename_suffix}", index=False)
        pd.DataFrame(links).to_csv(f"links_{filename_suffix}", index=False)
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(nodes)} nodes and {len(links)} links to CSV files"
            )
        )
