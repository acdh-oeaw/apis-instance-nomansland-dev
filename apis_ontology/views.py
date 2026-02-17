import json
import math
import logging
from apis_core.relations.models import Relation
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic.edit import FormView
from django_cosmograph.views import CosmographView

from apis_ontology.forms import SearchForm
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
from apis_ontology.search_utils import search

logger = logging.getLogger(__name__)


class SearchView(FormView):
    form_class = SearchForm
    template_name = "search.html"

    def get_form_kwargs(self, *args, **kwargs):
        return {"initial": self.request.GET}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if query := self.request.GET.get("search"):
            context["objects"] = search(query, self.request.user)
        return context


def map_view(request):
    return render(request, "apis_ontology/mapviz.html")


class GraphView(CosmographView):
    # TODO: How do I restrict the view based on user permissions

    def get_nodes_links(self):
        cache_key = "graph_nodes_links"
        cached_data = cache.get(cache_key)
        if cached_data:
            # Load nodes and links from cached JSON string
            nodes, links = json.loads(cached_data)
            logging.debug(
                f"Loaded graph from cache with {len(nodes)} nodes and {len(links)} links"
            )
            return nodes, links

        nodes = []

        def add_nodes(qs, group):
            for obj in qs.only("id"):
                nodes.append(
                    {
                        "id": obj.id,
                        "label": str(obj),
                        "group": group,
                    }
                )

        add_nodes(Person.objects.only("id"), "person")
        add_nodes(Place.objects.only("id"), "place")
        add_nodes(Work.objects.only("id"), "work")
        add_nodes(Institution.objects.only("id"), "institution")
        add_nodes(Manuscript.objects.only("id"), "manuscript")
        add_nodes(ManuscriptPart.objects.only("id"), "manuscriptpart")
        add_nodes(Expression.objects.only("id"), "expression")
        add_nodes(Event.objects.only("id"), "event")

        node_ids = {n["id"] for n in nodes}
        batch_size = 5000
        qs = (
            Relation.objects.exclude(
                subj_object_id__isnull=True, obj_object_id__isnull=True
            )
            .filter(subj_object_id__in=node_ids, obj_object_id__in=node_ids)
            .values_list("subj_object_id", "obj_object_id")
        )

        links = []
        for start in range(0, qs.count(), batch_size):
            batch = qs[start : start + batch_size]
            links.extend({"source": s, "target": t} for s, t in batch)

        def assign_node_sizes(nodes, links, max_size=6, base_size=4, scale=10):
            degree = {}

            for link in links:
                s = link.get("source")
                t = link.get("target")
                if s:
                    degree[s] = degree.get(s, 0) + 1
                if t:
                    degree[t] = degree.get(t, 0) + 1

            for node in nodes:
                d = degree.get(node["id"], 0)
                size = base_size + max_size * (math.atan(d / scale) / (math.pi / 2))
                node["size"] = round(size, 2)

            return nodes

        nodes = assign_node_sizes(nodes, links)

        logger.debug(f"Generated graph with {len(nodes)} nodes and {len(links)} links")
        # Cache nodes and links as a JSON string for 1 hour
        cache.set(cache_key, json.dumps((nodes, links)), 86400)

        return nodes, links
