import json

from apis_core.apis_entities.models import RootObject
from apis_core.relations.models import Relation
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic.edit import FormView
from django_cosmograph.utils import assign_node_sizes
from django_cosmograph.views import CosmographView

from apis_ontology.forms import SearchForm
from apis_ontology.search_utils import search


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
            return nodes, links

        nodes = []
        for obj in RootObject.objects_inheritance.select_subclasses():
            nodes.append(
                {"id": obj.id, "label": str(obj), "group": obj.__class__.__name__}
            )
        links = []
        for rel in Relation.objects.all():
            links.append(
                {
                    "source": rel.subj.id,
                    "target": rel.obj.id,
                }
            )
        nodes = assign_node_sizes(nodes, links)

        # Cache nodes and links as a JSON string for 1 hour
        cache.set(cache_key, json.dumps((nodes, links)), 3600)

        return nodes, links
