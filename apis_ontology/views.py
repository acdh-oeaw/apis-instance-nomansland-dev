import json
import logging
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic.edit import FormView
from django_cosmograph.views import CosmographView

from apis_ontology.forms import SearchForm
from apis_ontology.models import GraphSearchSnapshot
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
        cache_key = GraphSearchSnapshot.CACHE_KEY
        cached_data = cache.get(cache_key)
        if cached_data:
            nodes, links = json.loads(cached_data)
            logger.debug(
                f"Loaded graph from cache with {len(nodes)} nodes and {len(links)} links"
            )
            return nodes, links

        snapshot = GraphSearchSnapshot.objects.filter(
            key=GraphSearchSnapshot.DEFAULT_KEY
        ).first()
        if snapshot is None:
            logger.debug("Graph snapshot missing - rebuilding from source models")
            snapshot = GraphSearchSnapshot.rebuild()

        nodes = snapshot.nodes
        links = snapshot.links

        logger.debug(f"Generated graph with {len(nodes)} nodes and {len(links)} links")
        # Cache nodes and links as a JSON string for 24 hours
        cache.set(cache_key, json.dumps((nodes, links)), 86400)

        return nodes, links
