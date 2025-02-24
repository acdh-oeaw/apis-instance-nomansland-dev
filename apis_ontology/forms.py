from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm
from django import forms


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
        "end",
        "script_type_title",
        "script_type_body",
        "description",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "name_in_arabic",
            "notes",
            "references",
            "start",
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


class PlaceForm(NomanslandEntityMixinForm):
    field_order = [
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
