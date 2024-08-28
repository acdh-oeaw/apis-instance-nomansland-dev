from collections import defaultdict
from django.core.management.base import BaseCommand
import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import pandas as pd
from tqdm.auto import tqdm

from apis_core.collections.models import SkosCollection, SkosCollectionContentObject

from apis_ontology.models import (
    Event,
    EventType,
    Institution,
    InstitutionType,
    Person,
    Place,
    PlaceType,
    Profession,
    PrincipalRole,
    Title,
)

df = pd.read_json("data/dump_3105.json")


def get_base_vocab_data(vocab_pk):
    match = df[(df.model == "apis_vocabularies.vocabsbaseclass") & (df.pk == vocab_pk)]
    if match.shape[0]:
        return {"name": match.iloc[0].fields["name"]}
    return {}


def get_labels(pk):
    label_rows = df[df.model == "apis_labels.label"]
    labels_match = label_rows[
        label_rows.apply(lambda row: row.fields["temp_entity"] == pk, axis=1)
    ]
    labels = defaultdict(str)
    for i, row in labels_match.iterrows():
        if row.fields["label_type"] in (26, 114):
            labels["alternative_names"] = (
                labels["alternative_names"] + row.fields["label"] + "\n"
            )
        if row.fields["label_type"] == 29:
            labels["name_in_arabic"] = row.fields["label"]

    return labels


class Command(BaseCommand):
    help = "import entities from vanilla APIS in data/dump_3105.json"

    def handle(self, *args, **kwargs):
        FIELDNAME_MAPPING = {
            "apis_entities.person": {"first_name": "forename", "name": "surname"},
            "apis_entities.place": {
                "lat": "latitude",
                "lng": "longitude",
                "name": "label",
            },
        }
        parent_skoscol, _ = SkosCollection.objects.get_or_create(name="nomansland")
