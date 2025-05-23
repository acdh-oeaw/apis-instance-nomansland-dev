"""
Management command to export nodes and links to CSV files
"""

from django.core.management.base import BaseCommand
from tqdm import tqdm
from apis_core.relations.models import Relation
import pandas as pd
from apis_core.apis_entities.models import RootObject
import re


class Command(BaseCommand):
    help = "Export nodes and links to CSV files"

    def handle(self, *args, **options):
        entities = []
        relations = []
        filename_suffix = f"{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"

        def prettify_class_name(name):
            return re.sub(r"(?<!^)(?=[A-Z])", " ", name).strip()

        for obj in RootObject.objects_inheritance.select_subclasses():
            entities.append(
                {
                    "pk": obj.pk,
                    "model": prettify_class_name(obj.__class__.__name__),
                    "label": str(obj).replace(f"({obj.pk})", "").strip(),
                    "start": getattr(obj, "start", getattr(obj, "date_of_birth", None)),
                    "end": getattr(obj, "end", getattr(obj, "date_of_death", None)),
                    "start_date": getattr(
                        obj,
                        "start_date_sort",
                        getattr(obj, "date_of_birth_date_sort", None),
                    ),
                    "end_date": getattr(
                        obj,
                        "end_date_sort",
                        getattr(obj, "date_of_death_date_sort", None),
                    ),
                }
            )

        for rel in Relation.objects.all().select_subclasses():
            try:
                relations.append(
                    {
                        "pk": rel.pk,
                        "name": rel.name(),
                        "name_reverse": rel.reverse_name(),
                        "source": rel.subj_object_id,
                        "source_type": prettify_class_name(rel.subj.__class__.__name__),
                        "target": rel.obj_object_id,
                        "target_type": prettify_class_name(rel.obj.__class__.__name__),
                        "start": rel.start,
                        "end": rel.end,
                        "start_date": rel.start_date_sort,
                        "end_date": rel.end_date_sort,
                        "certainty": rel.certainty,
                    }
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing relation {rel}: {e}")
                )
                continue

        pd.DataFrame(entities).to_csv(f"entities.csv", index=False)
        pd.DataFrame(relations).to_csv(f"relations.csv", index=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(entities)} nodes and {len(relations)} links to CSV files"
            )
        )
