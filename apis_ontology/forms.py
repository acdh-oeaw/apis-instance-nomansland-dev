from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm
from apis_core.apis_entities.forms import E53_PlaceForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class NomanslandEntityMixinForm(GenericModelForm):
    class Meta:
        exclude = ["published", "review", "pk_old"]


class EventForm(NomanslandEntityMixinForm):
    field_order = ["name", "start", "end", "kind", "status"]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "name_in_arabic",
            "notes",
            "references",
        ]


class ExpressionForm(NomanslandEntityMixinForm):
    field_order = [
        "title",
        "locus",
        "language",
        "start",
        "end",
        "script_type_title",
        "script_type_body",
        "name_in_arabic",
        "description",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "notes",
            "references",
            "status",
        ]


class InstitutionForm(NomanslandEntityMixinForm):
    field_order = [
        "name",
        "name_in_arabic",
        "alternative_names",
        "start",
        "end",
        "kind",
        "status",
        "references",
        "notes",
    ]


class ManuscriptForm(NomanslandEntityMixinForm):
    field_order = [
        "identifier",
        "name",
        "name_in_arabic",
        "start",
        "extent",
        "leaf_dimension",
        "written_dimension",
        "foliation_type",
        "foliation_note",
        "condition",
        "end",
        "status",
        "illustration_notes",
        "diagrams",
        "marginal_annotations",
        "additions",
        "seal_description",
        "description",
        "references",
        "notes",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + ["alternative_names"]


class ManuscriptPartForm(NomanslandEntityMixinForm):
    field_order = [
        "identifier",
        "name",
        "name_in_arabic",
        "alternative_names",
        "locus",
        "kind",
        "start",
        "end",
        "status",
        "description",
        "references",
        "notes",
    ]


class PersonForm(NomanslandEntityMixinForm):
    field_order = [
        "title",
        "forename",
        "surname",
        "name_in_arabic",
        "alternative_names",
        "gender",
        "date_of_birth",
        "date_of_death",
        "profession",
        "principal_role",
        "laqab_kunya",
        "fathers_name",
        "grandfathers_name",
        "status",
        "bio",
        "notes",
        "references",
    ]


class PlaceForm(E53_PlaceForm, NomanslandEntityMixinForm):
    field_order = [
        "place",
        "label",
        "name_in_arabic",
        "alternative_names",
        "latitude",
        "longitude",
        "status",
        "kind",
        "start",
        "end",
        "references",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "notes",
        ]


class WorkForm(NomanslandEntityMixinForm):
    field_order = [
        "name",
        "name_in_arabic",
        "alternative_names",
        "start",
        "end",
        "status",
        "kind",
        "subject_heading",
        "description",
        "references",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "notes",
        ]


class RelationFilterSetForm(GenericFilterSetForm):
    columns_exclude = [
        "subj_object_id",
        "obj_object_id",
        "subj_content_type",
        "obj_content_type",
        "start_date_sort",
        "end_date_sort",
        # useful to see interval date fields until they are corrected
        # "start_date_from",
        # "start_date_to",
        # "end_date_from",
        # "end_date_to",
        "relation_ptr",
        "pk_old",
    ]


class EntityFilterSetForm(GenericFilterSetForm):
    columns_exclude = GenericFilterSetForm.columns_exclude + [
        "start_date_sort",
        "end_date_sort",
        "date_of_birth_date_sort",
        "date_of_death_date_sort",
        # useful to see interval date fields until they are corrected
        # "start_date_from",
        # "start_date_to",
        # "end_date_from",
        # "end_date_to",
        "pk_old",
    ]


class SearchForm(forms.Form):
    search = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.add_input(Submit("submit", _("Search")))
