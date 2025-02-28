"""
Management command to check if there are any dates
in a FuzzyDateParser field that are not valid dates.
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from django_interval.fields import FuzzyDateParserField
from tqdm import tqdm


class Command(BaseCommand):
    help = "Check for bad dates in FuzzyDateParser fields"

    def handle(self, *args, **options):
        BASE_URL = "https://nomansland-dev.acdh-ch-dev.oeaw.ac.at"
        bad_dates = []
        app_models = [
            m
            for m in apps.get_app_config("apis_ontology").get_models()
            if not m.__name__.startswith("Version")
        ]
        for model in tqdm(app_models):
            for obj in model.objects.all():
                for f in obj.__class__._meta.get_fields():
                    if isinstance(f, FuzzyDateParserField):
                        if getattr(obj, f.name) and not getattr(
                            obj, f.name + "_date_sort"
                        ):
                            bad_dates.append(
                                {
                                    "object": f"[{str(obj)}]({BASE_URL + obj.get_edit_url()})",
                                    "field": f.name,
                                    "value": getattr(obj, f.name),
                                }
                            )

        if bad_dates:
            import pandas as pd

            pd.DataFrame(bad_dates).to_markdown("bad_dates.md", index=False)
            print(f"{len(bad_dates)} bad dates found. See bad_dates.md for details.")

        else:
            print("No bad dates found.")
