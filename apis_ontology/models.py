import logging

from apis_core.apis_entities.abc import E21_Person, E53_Place
from apis_core.apis_entities.models import AbstractEntity
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_core.core.models import LegacyDateMixin
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from apis_core.utils.helpers import create_object_from_uri
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class NomanslandMixin(models.Model):
    class Meta:
        abstract = True

    review = models.BooleanField(
        default=False,
        help_text="Should be set to True, if the "
        "data record holds up quality "
        "standards.",
    )

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

    @classmethod
    def get_or_create_uri(cls, uri):
        logger.info(f"using custom get_or_create_uri with %s", uri)
        return create_object_from_uri(uri, cls) or cls.objects.get(pk=uri)

    @property
    def uri(self):
        contenttype = ContentType.objects.get_for_model(self)
        uri = reverse("apis_core:generic:detail", args=[contenttype, self.pk])
        return uri


class PrincipalRole(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("principal role")
        verbose_name_plural = _("Principal roles")


class Profession(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("profession")
        verbose_name_plural = _("professions")


class Title(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("title")
        verbose_name_plural = _("titles")


class Person(
    E21_Person, VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity
):
    GENDERS = [
        ("male", "Male"),
        ("female", "Female"),
        ("any", "any"),
    ]
    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"
    title = models.ManyToManyField(Title, blank=True, null=True)
    alternative_names = models.TextField(blank=True, null=True)
    name_in_arabic = models.CharField(max_length=255, blank=True, null=True)
    laqab_kunya = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    grandfathers_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDERS)
    principal_role = models.ForeignKey(
        PrincipalRole, blank=True, null=True, on_delete=models.SET_NULL
    )
    profession = models.ManyToManyField(Profession, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)  # ported from text

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("Persons")

    # TODO AH date filter


class PlaceType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("place type")
        verbose_name_plural = _("Place types")


class Place(E53_Place, VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"
    kind = models.ForeignKey(
        PlaceType, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("Places")

    def save(self, *args, **kwargs):
        if isinstance(self.latitude, float) and isinstance(self.longitude, float):
            self.status = "distinct"
        super(Place, self).save(*args, **kwargs)
        return self


class InstitutionType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("institution type")
        verbose_name_plural = _("Institution types")


class Institution(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(
        InstitutionType, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("institution")
        verbose_name_plural = _("Institutions")


class EventType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("event type")
        verbose_name_plural = _("Event types")


class Event(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(
        EventType, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("Events")


class WorkType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("work type")
        verbose_name_plural = _("Work types")


class SubjectHeading(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("subject heading")
        verbose_name_plural = _("Subject headings")


class Work(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(WorkType, blank=True, null=True, on_delete=models.SET_NULL)
    subject_heading = models.ManyToManyField(SubjectHeading, blank=True)
    description = models.TextField(blank=True, null=True)  # ported from text

    class Meta:
        verbose_name = _("work")
        verbose_name_plural = _("Works")


class Language(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("Languages")


class Expression(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    title = models.CharField(max_length=255, blank=True, null=True)
    locus = models.CharField(max_length=255, blank=True, null=True)
    script_title = models.CharField(max_length=255, blank=True, null=True)
    script_body = models.CharField(max_length=255, blank=True, null=True)
    language = models.ManyToManyField(Language, blank=True, null=True)
    # TODO: language of expression text?
    description = models.TextField(blank=True, null=True)  # ported from text

    class Meta:
        verbose_name = _("work")
        verbose_name_plural = _("Works")


class ManuscriptCondition(GenericModel, models.Model):
    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("manuscript condition")
        verbose_name_plural = _("manuscript conditions")


class Manuscript(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255, blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=True, null=True)
    extent = models.CharField(max_length=255, blank=True, null=True)
    leaf_dimension = models.CharField(max_length=255, blank=True, null=True)
    written_dimension = models.CharField(max_length=255, blank=True, null=True)
    foliation_type = models.CharField(max_length=255, blank=True, null=True)
    condition = models.ManyToManyField(ManuscriptCondition, blank=True, null=True)
    # TODO: are the following fields from apis_metainfo - one to one or one to many?
    illustration_notes = models.TextField(blank=True, null=True)  # ported from text
    diagrams = models.TextField(blank=True, null=True)  # ported from text
    marginal_annotations = models.TextField(blank=True, null=True)  # ported from text
    additions = models.TextField(blank=True, null=True)  # ported from text
    seal_description = models.TextField(blank=True, null=True)  # ported from text
    description = models.TextField(blank=True, null=True)  # ported from text

    class Meta:
        verbose_name = _("manuscript")
        verbose_name_plural = _("Manuscripts")


class ManuscriptPartType(GenericModel, models.Model):
    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("manuscript part type ")
        verbose_name_plural = _("manuscript part types")


class ManuscriptPart(VersionMixin, LegacyDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255, blank=True)
    identifier = models.CharField(max_length=255)
    locus = models.CharField(max_length=255, blank=True)
    kind = models.ForeignKey(
        ManuscriptPartType, blank=True, null=True, on_delete=models.SET_NULL
    )
    description = models.TextField(blank=True, null=True)  # ported from text

    class Meta:
        verbose_name = _("manuscript part")
        verbose_name_plural = _("Manuscript parts")
