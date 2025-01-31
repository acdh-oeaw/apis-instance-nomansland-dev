"""
Management command to import Zotero references
"""

import pandas as pd
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from apis_bibsonomy.models import Reference


class Command(BaseCommand):
    help = "import references from data dump."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dump",
            type=str,
            help="Path to the JSON file containing the data dump.",
        )

    def handle(self, *args, **kwargs):
        def match_content_type(cts: list):
            return ContentType.objects.get(
                app_label="apis_ontology",
                model=cts[-1],
            )

        try:
            df = pd.read_json(kwargs["dump"])
            refs = df[df.model == "apis_bibsonomy.reference"]
            for _, row in tqdm(refs.iterrows(), total=refs.shape[0]):
                try:
                    ct = match_content_type(row.fields["content_type"])
                    model_name = f"apis_ontology.{row.fields['content_type'][-1]}"
                    obj = apps.get_model(model_name).objects.get(
                        pk_old=row.fields["object_id"]
                    )
                    # get or create reference object if not already present
                    Reference.objects.get_or_create(
                        bibs_url=row.fields["bibs_url"],
                        content_type=ct,
                        object_id=obj.pk,
                        pages_start=row.fields["pages_start"],
                        pages_end=row.fields["pages_end"],
                        bibtex=row.fields["bibtex"],
                        attribute=row.fields["attribute"],
                    )
                except Exception as e:
                    print("Error while inserting", row)
                    print(repr(e))
        except Exception as e:
            print(repr(e))
