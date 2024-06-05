from apis_core.collections.models import SkosCollection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "import collections from vanilla apis_metainfo.collection to collections.skoscollection"

    def handle(self, *args, **options):
        collections = [
            "manually created entity",
            "Default import collection",
            "Manuscriptparts auto created",
            "Expression dates copied from Manuscript",
            "Manuscripts wrong end dates",
            "Expressions without manuscrripts",
            "Expression without lang",
            "Manuscripts with '/'",
            "Disconnected Manuscripts",
            "Completed libraries",
        ]
        parent_skoscol, _ = SkosCollection.objects.get_or_create(name="nomansland")
        for c in collections:
            skoscol, _ = SkosCollection.objects.get_or_create(
                name=c, parent=parent_skoscol
            )

        self.stdout.write(
            self.style.SUCCESS("Collections have been successfully imported.")
        )
