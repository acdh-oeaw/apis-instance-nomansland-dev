from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_core.generic.filtersets import GenericFilterSet, django_filters
from apis_core.relations.filtersets import RelationFilterSet
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CharField, Q, TextField
from django_interval.fields import FuzzyDateParserField
from django_interval.filters import YearIntervalRangeFilter

from apis_ontology.forms import EntityFilterSetForm, RelationFilterSetForm
from apis_ontology.models import AuthorOf, Work


def generic_search_filter(queryset, name, value, fields=None):
    """
    A generic filter that searches across specified fields using unaccent__icontains with OR logic.

    Priority for fields selection:
    1. Explicitly provided fields parameter
    2. _default_search_fields attribute on the model
    3. All CharField and TextField fields from the model

    Args:
        queryset: The queryset to filter
        name: The name of the filter (not used)
        value: The search value
        fields: Optional list of specific field names to search in

    Returns:
        Filtered queryset
    """
    if not value:
        return queryset

    # If no fields specified, check for _default_search_fields or use all text fields
    if fields is None:
        model = queryset.model

        # Check if model has _default_search_fields attribute
        if hasattr(model, "_default_search_fields"):
            fields = model._default_search_fields
        else:
            # Fall back to all CharField and TextField fields
            fields = []
            for field in model._meta.get_fields():
                if isinstance(field, (CharField, TextField)) and not field.primary_key:
                    fields.append(field.name)

    # Build Q objects for each field with OR logic
    q_objects = Q()
    for field in fields:
        q_objects |= Q(**{f"{field}__unaccent__icontains": value})

    return queryset.filter(q_objects)


class NomanslandMixinFilterSet(AbstractEntityFilterSet):
    class Meta(GenericFilterSet.Meta):
        form = EntityFilterSetForm
        exclude = [
            "date_of_birth_date_sort",
            "date_of_birth_date_from",
            "date_of_birth_date_to",
            "date_of_death_date_sort",
            "date_of_death_date_from",
            "date_of_death_date_to",
            "start_date_sort",
            "end_date_sort",
            "start_date_from",
            "start_date_to",
            "end_date_from",
            "end_date_to",
            "pk_old",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "unaccent__icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "unaccent__icontains",
                },
            },
            FuzzyDateParserField: {"filter_class": YearIntervalRangeFilter},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filter in self.filters.values():
            if (
                hasattr(filter, "label")
                and filter.label
                and "unaccent contains" in filter.label
            ):
                filter.label = filter.label.replace("unaccent contains", "")
        self.filters["search"] = django_filters.CharFilter(
            method=generic_search_filter, label="Search"
        )


class WorkFilterSet(NomanslandMixinFilterSet):
    """FilterSet for `Work` model with a 'without_authors' checkbox."""

    class Meta(NomanslandMixinFilterSet.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["without_authors"] = django_filters.BooleanFilter(
            method=self.filter_without_authors,
            label="Works without authors",
            widget=forms.CheckboxInput(),
            initial=False,
        )

    def filter_without_authors(self, queryset, name, value):
        """Return Works that have no related `AuthorOf` relation when checked."""
        if not value:
            return queryset

        ct = ContentType.objects.get_for_model(Work)
        subq = AuthorOf.objects.filter(
            obj_object_id=models.OuterRef("pk"), obj_content_type=ct
        )
        return queryset.annotate(_has_author=models.Exists(subq)).filter(
            _has_author=False
        )


class NomanslandRelationMixinFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        form = RelationFilterSetForm
        exclude = RelationFilterSet.Meta.exclude + [
            "start_date_sort",
            "end_date_sort",
            "start_date_from",
            "start_date_to",
            "end_date_from",
            "end_date_to",
            "pk_old",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            FuzzyDateParserField: {"filter_class": YearIntervalRangeFilter},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filter in self.filters.values():
            if hasattr(filter, "label") and filter.label and "contains" in filter.label:
                filter.label = filter.label.replace("contains", "")
        self.filters["search"] = django_filters.CharFilter(
            method=generic_search_filter, label="Search"
        )
