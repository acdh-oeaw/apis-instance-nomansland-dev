from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.tables import Column

from apis_ontology.models import Event, Expression, Manuscript, ManuscriptPart, Person


class NomanslandMixinTable(AbstractEntityTable):
    paginate_by = 100

    class Meta(AbstractEntityTable.Meta):
        exclude = [
            "id",
            "desc",
            "delete",
            "noduplicate",
        ]
        fields = []
        sequence = fields + ["...", "view", "edit"]

    id = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_id(self, record):
        return getattr(record, "id", "")

    def order_start(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date_sort")
        return queryset, True

    def order_end(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "end_date_sort")
        return queryset, True


class EventTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Event
        fields = ["name"]

    name = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_name(self, record):
        return getattr(record, "name", "")


class ExpressionTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Expression
        exclude = ["desc"]
        fields = ["title", "locus", "language"]

    title = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_title(self, record):
        return getattr(record, "title", "")


class ManuscriptTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Manuscript
        fields = ["identifier", "name", "start", "extent"]

    identifier = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_identifier(self, record):
        return getattr(record, "identifier", "")


class ManuscriptPartTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = ManuscriptPart
        fields = ["identifier", "name", "locus", "kind"]


class PersonTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Person
        fields = ["surname", "forename", "date_of_birth", "date_of_death"]

    surname = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_surname(self, record):
        return getattr(record, "surname", "")

    def order_date_of_birth(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "date_of_birth_date_sort"
        )
        return queryset, True

    def order_date_of_death(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "date_of_death_date_sort"
        )
        return queryset, True
