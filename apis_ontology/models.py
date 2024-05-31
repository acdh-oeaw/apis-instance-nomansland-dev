import logging

from apis_core.apis_entities.abc import E53_Place
from apis_core.apis_entities.models import AbstractEntity
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_core.history.models import VersionMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from apis_core.core.models import LegacyDateMixin
from apis_core.generic.abc import GenericModel
from django.contrib.contenttypes.fields import GenericForeignKey

logger = logging.getLogger(__name__)


class Source(GenericModel, models.Model):
    orig_filename = models.CharField(max_length=255, blank=True)
    indexed = models.BooleanField(default=False)
    pubinfo = models.CharField(max_length=400, blank=True)
    author = models.CharField(max_length=255, blank=True)
    orig_id = models.PositiveIntegerField(blank=True, null=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        if retstr := self.orig_filename:
            if self.author:
                retstr += f" stored by {self.author}"
            return retstr
        return f"(ID: {self.id})".format(self.id)


class NomanslandMixin(models.Model):
    class Meta:
        abstract = True

    review = models.BooleanField(
        default=False,
        help_text="Should be set to True, if the "
        "data record holds up quality "
        "standards.",
    )
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.SET_NULL)

    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    published = models.BooleanField(default=False)
    status = models.CharField(max_length=100)
    references = models.TextField(blank=True, null=True)

    def nomansland_collections(self):
        parent = SkosCollection.objects.get(name="nomansland")
        content_type = ContentType.objects.get_for_model(self)
        sccos = SkosCollectionContentObject.objects.filter(
            collection__parent=parent, content_type=content_type, object_id=self.pk
        ).values_list("collection")
        return SkosCollection.objects.filter(id__in=sccos)


class PlaceType(GenericModel, models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Title")
        verbose_name_plural = _("Titles")


class Place(E53_Place, VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("Places")

    def save(self, *args, **kwargs):
        if isinstance(self.lat, float) and isinstance(self.lng, float):
            self.status = "distinct"
        super(Place, self).save(*args, **kwargs)
        return self
