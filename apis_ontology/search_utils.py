from apis_core.apis_entities.utils import get_entity_classes
from apis_core.apis_metainfo.models import RootObject
from apis_core.generic.helpers import default_search_fields
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import CharField, F, Model, OuterRef, Q, QuerySet, Value
from django.db.models.functions import Concat


def annotate_qs(qs: QuerySet, model: type[Model], fields: list[str]) -> QuerySet:
    field_exprs = [item for field in fields for item in [F(field.name), Value(" ")]][
        :-1
    ]
    m = model.objects.filter(pk=OuterRef("pk")).annotate(
        search_obj=Concat(*field_exprs, output_field=CharField())
        if len(field_exprs) > 1
        else F(fields[0].name)
    )
    annotation = {
        f"gs_{model.__name__.lower()}": m.values_list("search_obj", flat=True)
    }
    qs = qs.annotate(**annotation)
    return qs


def search(query: str, user: object):
    # search in entities:
    entities = get_entity_classes()
    qs = RootObject.objects_inheritance.all()
    entities_search_vector = []
    for entity in entities:
        if user.has_perm(entity.get_view_permission()):
            qs = annotate_qs(qs, entity, default_search_fields(entity))
            entities_search_vector.append(entity)
    if not entities_search_vector:
        return qs.none()
    search_vector = SearchVector(
        *[
            f"gs_{entity.__name__.lower()}"
            for entity in entities
            if entity in entities_search_vector
        ]
    )
    qs = qs.annotate(
        search_vector=search_vector,
        rank=SearchRank(search_vector, query),
    )
    search_query = SearchQuery(
        query,
        search_type="websearch",
    )
    res = qs.filter(search_vector=search_query).order_by("-rank")
    return res.select_subclasses()
