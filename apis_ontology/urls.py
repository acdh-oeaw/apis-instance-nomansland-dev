from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apis_core.apis_entities.api_views import GetEntityGeneric

from apis_ontology.views import SearchView, map_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("apis/", include("apis_core.urls", namespace="apis")),
    path("apis/collections/", include("apis_core.collections.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("entity/<int:pk>/", GetEntityGeneric.as_view(), name="GetEntityGenericRoot"),
    path("", TemplateView.as_view(template_name="base.html")),
    path("apis_bibsonomy/", include("apis_bibsonomy.urls", namespace="bibsonomy")),
    path("search", SearchView.as_view(), name="search"),
    path("map", map_view, name="map"),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += [
    path("", include("apis_acdhch_django_auditlog.urls")),
]
