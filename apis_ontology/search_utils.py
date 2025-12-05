from itertools import chain

from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.utils import get_entity_classes
from apis_core.generic.helpers import default_search_fields, generate_search_filter
from apis_core.relations.models import Relation
from django.db.models import F, Model, OuterRef, Q, QuerySet, Value
from django.db.models.functions import Concat


def annotate_qs(qs: QuerySet, model: type[Model], fields: list[str]) -> QuerySet:
    field_exprs = [item for field in fields for item in [F(field), Value(" ")]][:-1]
    m = model.objects.filter(pk=OuterRef("pk")).annotate(
        search_obj=Concat(*field_exprs)
    )
    annotation = {
        f"gs_{model.__name__.lower()}": m.values_list("search_obj", flat=True)
    }
    qs = qs.annotate(**annotation)
    return qs


def search(query: str, user: object):
    # search in entities:
    entities = get_entity_classes()
    qs = AbstractEntity.objects.all()
    for entity in entities:
        qs = annotate_qs(qs, entity, default_search_fields(entity))
    return qs
