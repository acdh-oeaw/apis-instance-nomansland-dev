from apis_core.generic.forms import GenericModelForm
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
    field_order = ["name", "start", "end", "kind", "status"]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "name_in_arabic",
            "notes",
            "references",
        ]


class ManuscriptForm(NomanslandEntityMixinForm):
    field_order = [
        "identifier",
        "name",
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
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "name_in_arabic",
            "notes",
            "references",
        ]
