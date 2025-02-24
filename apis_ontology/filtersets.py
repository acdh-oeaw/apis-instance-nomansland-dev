from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_core.generic.filtersets import django_filters
from apis_core.relations.filtersets import RelationFilterSet
from django.db import models
from apis_ontology.forms import RelationFilterSetForm, EntityFilterSetForm


class NomanslandMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        form = EntityFilterSetForm
        exclude = AbstractEntityFilterSet.Meta.exclude + [
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
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }


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
        }
