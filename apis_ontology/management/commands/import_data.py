from django.core.management.base import BaseCommand
import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_relations.models import Property
import pandas as pd
from pandas.io.sql import is_dict_like
from tqdm.auto import tqdm

from apis_core.collections.models import SkosCollection, SkosCollectionContentObject

from apis_ontology.models import Person, Profession, PrincipalRole, Title


class Command(BaseCommand):
    help = "import entities from vanilla APIS in data/dump_3105.json"

    def handle(self, *args, **kwargs):
        df = pd.read_json("data/dump_3105.json")
        persons = df[df.model == "apis_entities.person"]
        FIELDNAME_MAPPING = {"first_name": "forename", "name": "surname"}
        parent_skoscol, _ = SkosCollection.objects.get_or_create(name="nomansland")
        ct = ContentType.objects.get_for_model(Person)

        def get_profession(profession_id):
            match = df[
                (df.model == "apis_vocabularies.vocabsbaseclass")
                & (df.pk == profession_id)
            ]
            if match.shape[0]:
                return {"name": match.iloc[0].fields["name"]}
            return {}

        def get_principal_role(role_pk):
            match = df[
                (df.model == "apis_vocabularies.vocabsbaseclass") & (df.pk == role_pk)
            ]
            if match.shape[0]:
                return {"name": match.iloc[0].fields["name"]}
            return {}

        def get_title(title_id):
            title_match = df[
                (df.model == "apis_vocabularies.vocabsbaseclass") & (df.pk == title_id)
            ]
            if title_match.shape[0]:
                return {"name": title_match.iloc[0].fields["name"]}
            return {}

        def get_texts(text_pk):
            match = df[(df.model == "apis_metainfo.text") & (df.pk == text_pk)]
            if match.shape[0]:
                if match.iloc[0].fields["kind"] == 73:
                    return {"bio": match.iloc[0].fields["text"]}

            return {}

        def get_labels(pk):
            label_rows = df[df.model == "apis_labels.label"]
            labels_match = label_rows[
                label_rows.apply(lambda row: row.fields["temp_entity"] == pk, axis=1)
            ]
            alternative_names = ""
            name_in_arabic = ""

            for i, row in labels_match.iterrows():
                if row.fields["label_type"] in (26, 114):
                    alternative_names = row.fields["label"] + "\n"
                if row.fields["label_type"] == 29:
                    name_in_arabic = row.fields["label"]

            return {
                "alternative_names": alternative_names.strip(),
                "name_in_arabic": name_in_arabic,
            }

        def get_temp_entity_data(pk):
            match = df[(df.pk == pk) & (df.model == "apis_metainfo.tempentityclass")]
            return match.iloc[0].fields

        def get_collection(collection_id):
            match = df[
                (df.model == "apis_metainfo.collection") & (df.pk == collection_id)
            ]
            if match.shape[0]:
                return SkosCollection.objects.get(
                    name=match.iloc[0].fields["name"], parent=parent_skoscol
                )

        def import_persons():
            for i, p in tqdm(persons.iterrows(), total=persons.shape[0]):
                old_data = p.fields

                ted = get_temp_entity_data(p.pk)
                old_data = {**old_data, **ted}
                # old_data["start_date"] = DateParser.parse_date(old_data["start_date"])
                # old_data["end_date"] = DateParser.parse_date(old_data["start_date"])
                old_data = {**old_data, **get_labels(p.pk)}
                text_id = old_data["text"]
                old_data.pop("text")
                if text_id:
                    old_data = {**old_data, **get_texts(text_id[0])}

                title_ids = old_data.get("title")
                old_data.pop("title")

                principal_role_pk = old_data.get("principal_role")
                old_data.pop("principal_role")

                collection_ids = old_data.get("collection")
                old_data.pop("collection")

                profession_ids = old_data.get("profession")
                old_data.pop("profession")

                person_data = {
                    FIELDNAME_MAPPING.get(k, k): v for k, v in old_data.items() if v
                }
                p, _ = Person.objects.get_or_create(**person_data)

                if title_ids:
                    for title_id in title_ids:
                        title_data = get_title(title_id)
                        t, _ = Title.objects.get_or_create(**title_data)
                        p.title.add(t)

                if principal_role_pk:
                    principal_role = get_principal_role(principal_role_pk)
                    pr, _ = PrincipalRole.objects.get_or_create(**principal_role)
                    p.principal_role = pr
                    p.save()

                if profession_ids:
                    for profession_id in profession_ids:
                        profession = get_profession(profession_id)
                        pro, _ = Profession.objects.get_or_create(**profession)
                        p.profession.add(pro)

                if collection_ids:
                    for collection_id in collection_ids:
                        skoscol = get_collection(collection_id)
                        scco, _ = SkosCollectionContentObject.objects.get_or_create(
                            collection=skoscol, content_type=ct, object_id=p.pk
                        )

        import_persons()

        self.stdout.write(
            self.style.SUCCESS("Collections have been successfully imported.")
        )
