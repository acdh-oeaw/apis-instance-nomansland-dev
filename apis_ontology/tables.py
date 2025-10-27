from datetime import datetime
from apis_core.generic.tables import GenericTable
from django.utils.html import format_html
from django_tables2.tables import Column

from apis_ontology.models import (
    Event,
    Expression,
    Institution,
    Manuscript,
    ManuscriptPart,
    Person,
    Place,
    Work,
)


class NomanslandMixinTable(GenericTable):
    paginate_by = 100

    class Meta(GenericTable.Meta):
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


class InstitutionTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Institution
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


class PlaceTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Place
        fields = ["label", "latitude", "longitude"]

    label = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_label(self, record):
        return getattr(record, "label", "")


class WorkTable(NomanslandMixinTable):
    class Meta(NomanslandMixinTable.Meta):
        model = Work
        fields = ["name"]

    name = Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def value_name(self, record):
        return getattr(record, "place", "")


class NomanslandRelationMixinTable(GenericTable):
    paginate_by = 100
    export_filename = (
        f"nomansland_relations_export_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    class Meta(GenericTable.Meta):
        fields = ["subj", "obj"]
        exclude = ["desc", "delete"]
        sequence = ("subj", "obj", "...", "view", "edit")

    subj = Column(verbose_name="Subject", orderable=False)
    obj = Column(verbose_name="Object", orderable=False)

    def render_subj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def value_subj(self, value):
        return str(value)

    def render_obj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def value_obj(self, value):
        return str(value)

    def order_start(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date_sort")
        return queryset, True

    def order_end(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "end_date_sort")
        return queryset, True
