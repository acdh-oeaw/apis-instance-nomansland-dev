from django.core.management.base import BaseCommand

from apis_ontology.models import GraphSearchSnapshot


class Command(BaseCommand):
    help = "Rebuild the denormalized graph snapshot used by GraphView"

    def handle(self, *args, **options):
        snapshot = GraphSearchSnapshot.rebuild()
        self.stdout.write(
            self.style.SUCCESS(
                f"Rebuilt graph snapshot with {snapshot.node_count} nodes and {snapshot.link_count} links"
            )
        )
