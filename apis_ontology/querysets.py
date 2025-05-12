from apis_ontology.filtersets import generic_search_filter


def NomanslandMixinAutocompleteQueryset(model, query):
    """
    Autocomplete queryset for Nomansland models,
    making use of generic_search_filter
    to provide unaccented search results
    """
    return generic_search_filter(model.objects.all(), None, query)
