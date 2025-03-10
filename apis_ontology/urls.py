from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apis_core.apis_entities.api_views import GetEntityGeneric


urlpatterns = [
    path("admin/", admin.site.urls),
    path("apis/", include("apis_core.urls", namespace="apis")),
    path("apis/collections/", include("apis_core.collections.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("entity/<int:pk>/", GetEntityGeneric.as_view(), name="GetEntityGenericRoot"),
    path("", TemplateView.as_view(template_name="base.html")),
    path("highlighter/", include("apis_highlighter.urls", namespace="highlighter")),
    path("apis_bibsonomy/", include("apis_bibsonomy.urls", namespace="bibsonomy")),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [
    path("", include("django_acdhch_functions.urls")),
]

urlpatterns += [path("", include("django_interval.urls"))]
