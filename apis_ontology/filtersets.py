from apis_core.generic.filtersets import django_filters
from apis_core.relations.filtersets import RelationFilterSet
from django.db import models
from apis_ontology.forms import RelationFilterSetForm


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
