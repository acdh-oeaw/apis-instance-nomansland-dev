from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.tables import Column

from apis_ontology.models import Expression


class NomanslandMixinTable(AbstractEntityTable):
    class Meta(AbstractEntityTable.Meta):
        exclude = [
            "id",
            "view",
            "edit",
            "delete",
            "noduplicate",
        ]
        sequence = [
            "desc",
            "...",
        ]

    paginate_by = 100


class ExpressionTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Expression
        fields = ["title", "locus", "language"]
        sequence = [
            "title",
            "locus",
            "language",
            "...",
        ]

    title = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_title(self, record):
        return getattr(record, "title", getattr(record, "title", ""))
