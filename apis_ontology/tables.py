from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.tables import Column

from apis_ontology.models import Expression, Manuscript


class NomanslandMixinTable(AbstractEntityTable):
    paginate_by = 100

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

    def order_start(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date_sort")
        return queryset, True

    def order_end(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "end_date_sort")
        return queryset, True


class ExpressionTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Expression
        exclude = NomanslandMixinTable.Meta.exclude + ["desc"]
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
        return getattr(record, "title", "")


class ManuscriptTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Manuscript
        exclude = NomanslandMixinTable.Meta.exclude + ["desc"]
        fields = ["identifier", "name", "start", "extent"]
        sequence = fields + ["..."]

    identifier = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_identifier(self, record):
        return getattr(record, "identifier", "")
