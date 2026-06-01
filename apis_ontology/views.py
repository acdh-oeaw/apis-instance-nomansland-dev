import json
import logging
import math
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

    def _show_unconnected_nodes(self):
        value = self.request.GET.get("show_unconnected", "1").strip().lower()
        return value not in {"0", "false", "no", "off"}

    def _apply_unconnected_visibility(self, nodes, links):
        if self._show_unconnected_nodes():
            return nodes, links

        linked_node_ids = {
            endpoint
            for link in links
            for endpoint in (link.get("source"), link.get("target"))
            if endpoint is not None
        }
        return [node for node in nodes if node.get("id") in linked_node_ids], links

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["graph_query"] = self.request.GET.get("q", "").strip()
        context["graph_show_unconnected"] = self._show_unconnected_nodes()
        return context

    def _filter_nodes_links(self, nodes, links):
        query = self.request.GET.get("q", "").strip().lower()
        if not query:
            return nodes, links

        def matches_query(value):
            if isinstance(value, dict):
                return any(matches_query(v) for v in value.values())
            if isinstance(value, (list, tuple, set)):
                return any(matches_query(v) for v in value)
            return query in str(value).lower()

        matching_nodes = [
            node
            for node in nodes
            if matches_query(node)
        ]

        matching_node_ids = {node.get("id") for node in matching_nodes}

        matching_links = [link for link in links if matches_query(link)]

        links_of_matching_nodes = [
            link
            for link in links
            if link.get("source") in matching_node_ids
            or link.get("target") in matching_node_ids
        ]

        if not matching_node_ids and not matching_links:
            return [], []

        # Include all links that match directly and all links connected to matching nodes.
        filtered_links = []
        seen_links = set()
        for link in matching_links + links_of_matching_nodes:
            key = json.dumps(link, sort_keys=True, default=str)
            if key in seen_links:
                continue
            seen_links.add(key)
            filtered_links.append(link)

        visible_node_ids = set()
        for link in filtered_links:
            visible_node_ids.add(link.get("source"))
            visible_node_ids.add(link.get("target"))

        # Keep all matched nodes, even if they have no incident links.
        filtered_nodes = list(matching_nodes)
        for node in nodes:
            if node.get("id") in visible_node_ids and node not in filtered_nodes:
                filtered_nodes.append(node)

        # Cosmograph can fail to place linkless nodes in a visible region.
        # Give them deterministic coordinates on a small circle as a fallback.
        linked_node_ids = {
            endpoint
            for link in filtered_links
            for endpoint in (link.get("source"), link.get("target"))
            if endpoint is not None
        }
        linkless_nodes = [n for n in filtered_nodes if n.get("id") not in linked_node_ids]
        if linkless_nodes:
            radius = max(20.0, len(linkless_nodes) * 3.0)
            for index, node in enumerate(linkless_nodes):
                if "x" in node and "y" in node:
                    continue
                angle = (2.0 * math.pi * index) / len(linkless_nodes)
                node["x"] = round(radius * math.cos(angle), 3)
                node["y"] = round(radius * math.sin(angle), 3)

        return filtered_nodes, filtered_links

    def get_nodes_links(self):
        cache_key = GraphSearchSnapshot.CACHE_KEY
        cached_data = cache.get(cache_key)
        if cached_data:
            nodes, links = json.loads(cached_data)
            nodes, links = self._filter_nodes_links(nodes, links)
            nodes, links = self._apply_unconnected_visibility(nodes, links)
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

        nodes, links = self._filter_nodes_links(nodes, links)
        return self._apply_unconnected_visibility(nodes, links)
