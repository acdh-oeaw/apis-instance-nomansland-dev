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


class ManuscriptPartForm(NomanslandEntityMixinForm):
    field_order = [
        "identifier",
        "name",
        "locus",
        "kind",
        "start",
        "end",
        "status",
        "description",
    ]

    class Meta(NomanslandEntityMixinForm.Meta):
        exclude = NomanslandEntityMixinForm.Meta.exclude + [
            "alternative_names",
            "name_in_arabic",
            "notes",
            "references",
        ]


class PersonForm(NomanslandEntityMixinForm):
    field_order = [
        "title",
        "forename",
        "surname",
        "alternative_names",
        "name_in_arabic",
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
