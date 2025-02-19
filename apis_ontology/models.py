import logging

from apis_core.apis_entities.abc import E21_Person, E53_Place
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from apis_core.utils.helpers import create_object_from_uri
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_interval.fields import FuzzyDateParserField
from .date_utils import nomansland_dateparser

logger = logging.getLogger(__name__)


class NomanslandDateMixin(models.Model):
    class Meta:
        abstract = True

    start = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)
    end = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)


class NomanslandMixin(models.Model):
    class Meta:
        abstract = True

    pk_old = models.BigIntegerField(blank=True, null=True, editable=False)
    review = models.BooleanField(
        default=False,
        help_text="Should be set to True, if the "
        "data record holds up quality "
        "standards.",
    )
    alternative_names = models.TextField(blank=True, null=True)
    name_in_arabic = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    published = models.BooleanField(default=False)
    status = models.CharField(max_length=100, blank=True, null=True)
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


class Person(E21_Person, VersionMixin, NomanslandMixin, AbstractEntity):
    GENDERS = [
        ("male", "Male"),
        ("female", "Female"),
        ("any", "any"),
    ]
    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"
    title = models.ManyToManyField(Title, blank=True)
    laqab_kunya = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    grandfathers_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDERS)
    principal_role = models.ForeignKey(
        PrincipalRole, blank=True, null=True, on_delete=models.SET_NULL
    )
    profession = models.ManyToManyField(Profession, blank=True)
    bio = models.TextField(blank=True, null=True)  # ported from text
    date_of_birth = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )
    date_of_death = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )

    def __str__(self):
        return f"{self.forename} {self.surname} ({self.pk})"

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


class Place(
    E53_Place, VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity
):
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

    def __str__(self):
        return f"{self.label} ({self.pk})"


class InstitutionType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("institution type")
        verbose_name_plural = _("Institution types")


class Institution(VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(
        InstitutionType, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("institution")
        verbose_name_plural = _("Institutions")

    def __str__(self):
        return f"{self.name} ({self.pk})"


class EventType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("event type")
        verbose_name_plural = _("Event types")


class Event(VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(
        EventType, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.name} ({self.pk})"

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


class Work(VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255)
    kind = models.ForeignKey(WorkType, blank=True, null=True, on_delete=models.SET_NULL)
    subject_heading = models.ManyToManyField(SubjectHeading, blank=True)
    description = models.TextField(blank=True, null=True)  # ported from text

    def __str__(self):
        return f"{self.name} ({self.pk})"

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


class ScriptType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("script type")
        verbose_name_plural = _("Script type")


class Expression(VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity):
    title = models.CharField(max_length=255, blank=True, null=True)
    locus = models.CharField(max_length=255, blank=True, null=True)
    script_type_title = models.ForeignKey(
        ScriptType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="script_type_title",
    )
    script_type_body = models.ForeignKey(
        ScriptType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="script_type_body",
    )
    language = models.ManyToManyField(Language, blank=True)
    description = models.TextField(blank=True, null=True)  # ported from text

    def __str__(self):
        return f"{self.title} ({self.pk})"

    class Meta:
        verbose_name = _("expression")
        verbose_name_plural = _("expressions")


class ManuscriptCondition(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("manuscript condition")
        verbose_name_plural = _("manuscript conditions")


class Manuscript(VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity):
    name = models.CharField(max_length=255, blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=True, null=True)
    extent = models.CharField(max_length=255, blank=True, null=True)
    leaf_dimension = models.CharField(max_length=255, blank=True, null=True)
    written_dimension = models.CharField(max_length=255, blank=True, null=True)
    foliation_type = models.CharField(max_length=255, blank=True, null=True)
    foliation_note = models.CharField(max_length=255, blank=True, null=True)
    condition = models.ManyToManyField(ManuscriptCondition, blank=True)
    illustration_notes = models.TextField(blank=True, null=True)  # ported from text
    diagrams = models.TextField(blank=True, null=True)  # ported from text
    marginal_annotations = models.TextField(blank=True, null=True)  # ported from text
    additions = models.TextField(blank=True, null=True)  # ported from text
    seal_description = models.TextField(blank=True, null=True)  # ported from text
    description = models.TextField(blank=True, null=True)  # ported from text

    def __str__(self):
        return f"{self.name} ({self.pk})"

    class Meta:
        verbose_name = _("manuscript")
        verbose_name_plural = _("Manuscripts")


class ManuscriptPartType(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("manuscript part type ")
        verbose_name_plural = _("manuscript part types")


class ManuscriptPart(
    VersionMixin, NomanslandDateMixin, NomanslandMixin, AbstractEntity
):
    name = models.CharField(max_length=255, blank=True)
    identifier = models.CharField(max_length=255)
    locus = models.CharField(max_length=255, blank=True)
    kind = models.ForeignKey(
        ManuscriptPartType, blank=True, null=True, on_delete=models.SET_NULL
    )
    description = models.TextField(blank=True, null=True)  # ported from text

    def __str__(self):
        return f"{self.name} ({self.pk})"

    class Meta:
        verbose_name = _("manuscript part")
        verbose_name_plural = _("Manuscript parts")


class NomanslandRelationMixin(
    models.Model,
    GenericModel,
):
    CERTAINTY = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
        ("unknown", "unknown"),
    ]
    certainty = models.CharField(max_length=7, choices=CERTAINTY, default="unknown")
    pk_old = models.BigIntegerField(blank=True, null=True, editable=False)

    class Meta:
        abstract = True


class ACopyOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [15]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "original work of"


class AncestralCountryOf(Relation, NomanslandRelationMixin, VersionMixin):
    relation_type_old = [98]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "ancestral country of [REVERSE]"


class AnnotatedBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [282]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "annotation in"


class AttributedTo(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [297]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "attributed to [REVERSE]"


class AuthorOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [1]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "authored by"


class AuthorOfContent(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [242]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "text in the note by"


class AuthoredBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [122]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "author of"


class BiographerOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [244]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "described by"


class BornIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [6]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of birth of"


class BoughtIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [4]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of buying of"


class BrotherOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [143]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "brother of [REVERSE]"


class BuriedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [102]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of bereavement of"


class CaptorOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [272]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Captured by"


class CertificateFor(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [299]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Certified by"


class ClassificationOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [198]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Classified in"


class ColleagueOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [14]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "colleague of"


class CommanderOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [24]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "under the command of"


class CommentaryOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [196]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "commentated in"


class CommentatorOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [112]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "commented by"


class CommentedTheWorkOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [265]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "commented work by"


class CommissionerOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [268]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "commissioned for"


class ConnectedTo(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [216]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Event]

    @classmethod
    def reverse_name(cls) -> str:
        return "connected to [REVERSE]"


class Contains(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [52, 155]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Expression, ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "Contains [REVERSE]"


class ContainsCopyOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [16]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "contains copy of [REVERSE]"


class CopiedBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [113]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "copyist of"


class CopiedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [3, 275]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Institution, Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of copy of"


class CopyistOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [248]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Copyist of [REVERSE]"


class CousinOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [292]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "cousin of"


class DedicateeOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [91]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "dedicated to"


class DescendantOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [190]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "predecessor of"


class DescribedBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [245]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "biographer of"


class DiedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [9]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of death of"


class EditedBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [188]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "editor of"


class Eulogized(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [178]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "eulogized [REVERSE]"


class ExecutedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [103]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of execution of"


class ExiledFrom(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [226]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Exile place of"


class ExplanationOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [197]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Explained in"


class FollowerOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [50]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Master of"


class FounderOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [271]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "founded by"


class GrandNephewOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [189]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "grand-uncle of"


class GrandfatherOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [99]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "grandson of"


class GreatGrandFatherOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [278]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Great grand-son of"


class HeldIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [5]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "holding place of"


class ImprisonedIn(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [105]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of imprisonment of"


class InTheLibraryOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [259]  # pk of Property in apis_relations
    subj_model = [Expression]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "In the library of [REVERSE]"


class JudgeIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [307]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Judge in [REVERSE]"


class KilledIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [104]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of assassination of"


class LivedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [8]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of resicence of"


class LocatedAt(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [38]  # pk of Property in apis_relations
    subj_model = [Institution]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Location place of"


class LocatedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [28, 95]  # pk of Property in apis_relations
    subj_model = [Institution, Place]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "located in [REVERSE]"


class MadePilgrimageTo(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [144]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of pilgrimage of"


class MentionedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [211, 301]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [ManuscriptPart, Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "a mention of"


class MetWith(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [140]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "met with [REVERSE]"


class MurdererOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [294]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "murderered by"


class NephewOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [181]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "uncle of"


class OwnedBy(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [58]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "owner of"


class OwnerOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [2]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Ownered by"


class PartOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [314]  # pk of Property in apis_relations
    subj_model = [Institution]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class ParticipatedInTheConquestOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [222]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place conquered by"


class ParticipatedInTheFoundingOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [223]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "participated in the founding of [REVERSE]"


class PatronOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [11]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "patronised by"


class PlaceMentionedIn(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [302]  # pk of Property in apis_relations
    subj_model = [Place]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Place mentioned in [REVERSE]"


class PlaceOfAcquisition(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [231]  # pk of Property in apis_relations
    subj_model = [Place]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "purchased in"


class PlaceOfBirth(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [78]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Place of Birth [REVERSE]"


class PlaceOfCompositionOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [55, 274]  # pk of Property in apis_relations
    subj_model = [Institution, Place]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Composed in"


class PlaceOfCopyOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [195]  # pk of Property in apis_relations
    subj_model = [Place]
    obj_model = [Expression]

    @classmethod
    def reverse_name(cls) -> str:
        return "Copied in"


class PurchaserOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [230]  # pk of Property in apis_relations
    subj_model = [Institution]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "Purchased by"


class RivalOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [295]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Rival of [REVERSE]"


class RuledOver(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [49]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Ruled by"


class RulerOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [185]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "rulerd by"


class SonOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [10]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "father of"


class SpouseOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [177]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "spouse of"


class StudiedAt(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [41]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of study of"


class StudiedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [7]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of study of"


class StudiedWith(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [13]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "teacher of"


class SubjectOfWork(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [214]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "work about"


class SuccessorOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [293]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "Succeeded by"


class SummaryOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [158]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "summary of [REVERSE]"


class SupplementTo(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [184]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "Supplemented by"


class TaughtIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [42]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "Place of teaching of"


class TeacherAt(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [40]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of teaching of"


class TeacherOf(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [257]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "thaught by"


class Testrel(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [151]  # pk of Property in apis_relations
    subj_model = [Manuscript]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "testrel [REVERSE]"


class TranslationOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [291]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "translated in"


class UsedIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [142]  # pk of Property in apis_relations
    subj_model = [Place]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "used in [REVERSE]"


class Visited(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [80]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "visited by"


class WorkIn(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [100]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Place]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of work of"


class WorkedAt(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [90]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Institution]

    @classmethod
    def reverse_name(cls) -> str:
        return "place of work of"


class WorkedFor(Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin):
    relation_type_old = [12]  # pk of Property in apis_relations
    subj_model = [Person]
    obj_model = [Person]

    @classmethod
    def reverse_name(cls) -> str:
        return "boss of"


class PlaceOfAnnotationOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [325]  # pk of Property in apis_relations
    subj_model = [Institution]
    obj_model = [ManuscriptPart]

    @classmethod
    def reverse_name(cls) -> str:
        return "annotated in"


class RefutationOf(
    Relation, NomanslandRelationMixin, NomanslandDateMixin, VersionMixin
):
    relation_type_old = [337]  # pk of Property in apis_relations
    subj_model = [Work]
    obj_model = [Work]

    @classmethod
    def reverse_name(cls) -> str:
        return "refuted by"
