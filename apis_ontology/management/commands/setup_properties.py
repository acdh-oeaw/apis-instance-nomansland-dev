from django.core.management.base import BaseCommand
import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_relations.models import Property


class Command(BaseCommand):
    help = "import relationships from vanilla APIS in data/properties.csv"

    def handle(self, *args, **options):
        for i, row in pd.read_csv("data/properties.csv").iterrows():
            p, _ = Property.objects.get_or_create(
                name_forward=row.name_forward, name_reverse=row.name_reverse
            )
            p.subj_class.add(
                ContentType.objects.get_for_model(apps.get_model(row.subj_class))
            )
            p.obj_class.add(
                ContentType.objects.get_for_model(apps.get_model(row.obj_class))
            )

        self.stdout.write(
            self.style.SUCCESS("Properties have been successfully imported.")
        )
