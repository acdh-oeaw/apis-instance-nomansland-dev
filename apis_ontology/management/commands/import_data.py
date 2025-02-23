from collections import defaultdict
from django.core.management.base import BaseCommand
import pandas as pd
from django.contrib.contenttypes.models import ContentType

from tqdm.auto import tqdm

from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_ontology.models import (
    Event,
    EventType,
    Institution,
    InstitutionType,
    Language,
    Person,
    Place,
    PlaceType,
    Profession,
    PrincipalRole,
    ScriptType,
    SubjectHeading,
    Title,
    WorkType,
    Work,
    Expression,
    Manuscript,
    ManuscriptPart,
    ManuscriptPartType,
    ManuscriptCondition,
)

TEXT_TYPES = {
    68: "illustration_notes",
    69: "diagrams",
    70: "marginal_annotations",
    71: "additions",
    72: "seal_description",
    73: "bio",
    149: "description",
    205: "description",
    206: "description",
    264: "description",
}


class Command(BaseCommand):
    help = "import entities from vanilla APIS"

    def add_arguments(self, parser):
        parser.add_argument("dump", type=str, help="dump file name")

    def handle(self, *args, **kwargs):
        df = pd.read_json(kwargs["dump"])
        FIELDNAME_MAPPING = {
            "apis_entities.person": {"first_name": "forename", "name": "surname"},
            "apis_entities.place": {
                "lat": "latitude",
                "lng": "longitude",
                "name": "label",
            },
        }
        parent_skoscol, _ = SkosCollection.objects.get_or_create(name="nomansland")

        def get_base_vocab_data(vocab_pk):
            match = df[
                (df.model == "apis_vocabularies.vocabsbaseclass") & (df.pk == vocab_pk)
            ]
            if match.shape[0]:
                return {"name": match.iloc[0].fields["name"]}
            return {}

        def get_text_field(text_pk):
            match = df[(df.model == "apis_metainfo.text") & (df.pk == text_pk)]
            if match.shape[0]:
                return {
                    TEXT_TYPES[match.iloc[0].fields["kind"]]: match.iloc[0].fields[
                        "text"
                    ]
                }

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

        def get_collection(collection_id):
            match = df[
                (df.model == "apis_metainfo.collection") & (df.pk == collection_id)
            ]
            if match.shape[0]:
                return SkosCollection.objects.get(
                    name=match.iloc[0].fields["name"], parent=parent_skoscol
                )

        def get_all_entity_data(pk, model_name):
            model_name = model_name
            base_data = df[(df.model == model_name) & (df.pk == pk)].iloc[0].fields
            match = df[(df.pk == pk) & (df.model == "apis_metainfo.tempentityclass")]
            ted = match.iloc[0].fields
            collections = None
            text_ids = []
            DROP_FIELDS = [
                "start_date",
                "end_date",
                "start_start_date",
                "end_start_date",
                "start_end_date",
                "end_end_date",
                "tempentityclass_ptr",
            ]
            if "source" in ted:
                ted.pop("source")
            if "collection" in ted:
                collections = ted["collection"]
                ted.pop("collection")
            if "text" in ted:
                text_ids = ted["text"]
                ted.pop("text")
            if "start_date_written" in ted:
                ted["start"] = ted["start_date_written"]
                ted.pop("start_date_written")
            if "end_date_written" in ted:
                ted["end"] = ted["end_date_written"]
                ted.pop("end_date_written")

            for field in DROP_FIELDS:
                if field in ted:
                    ted.pop(field)

            base_data = {**base_data, **ted, "pk_old": pk}
            data_new = {k: v for k, v in base_data.items() if v}
            if model_name in FIELDNAME_MAPPING:
                data_new = {
                    FIELDNAME_MAPPING[model_name].get(k, k): v
                    for k, v in base_data.items()
                    if v
                }

            texts = {}
            for text_id in text_ids:
                texts = {**texts, **get_text_field(text_id)}

            labels = get_labels(pk)

            return {
                "fields": {**data_new, **labels, **texts},
                "collections": collections,
            }

        def create_collections(collection_ids, entity):
            ct = ContentType.objects.get_for_model(entity)

            for collection_id in collection_ids:
                skoscol = get_collection(collection_id)
                scco, _ = SkosCollectionContentObject.objects.get_or_create(
                    collection=skoscol, content_type=ct, object_id=entity.pk
                )

        def import_persons():
            MODEL = "apis_entities.person"
            self.stdout.write("importing persons")
            persons = df[df.model == MODEL]
            for _, p in tqdm(persons.iterrows(), total=persons.shape[0]):
                try:
                    title_ids = None
                    principal_role_pk = None
                    profession_ids = None

                    ted = get_all_entity_data(p.pk, MODEL)
                    old_data = ted["fields"]

                    if "title" in old_data:
                        title_ids = old_data.get("title")
                        old_data.pop("title")

                    if "principal_role" in old_data:
                        principal_role_pk = old_data.get("principal_role")
                        old_data.pop("principal_role")

                    if "profession" in old_data:
                        profession_ids = old_data.get("profession")
                        old_data.pop("profession")

                    if "start" in old_data:
                        old_data["date_of_birth"] = old_data["start"]
                        old_data.pop("start")
                    if "end" in old_data:
                        old_data["date_of_death"] = old_data["end"]
                        old_data.pop("end")

                    p, _ = Person.objects.get_or_create(pk_old=old_data["pk_old"])
                    p.__dict__.update(**old_data)

                    if title_ids:
                        for title_id in title_ids:
                            title_data = get_base_vocab_data(title_id)
                            t, _ = Title.objects.get_or_create(**title_data)
                            p.title.add(t)

                    if principal_role_pk:
                        principal_role = get_base_vocab_data(principal_role_pk)
                        pr, _ = PrincipalRole.objects.get_or_create(**principal_role)
                        p.principal_role = pr

                    if profession_ids:
                        for profession_id in profession_ids:
                            profession = get_base_vocab_data(profession_id)
                            pro, _ = Profession.objects.get_or_create(**profession)
                            p.profession.add(pro)

                    p.save()
                    create_collections(ted["collections"], p)

                except Exception as e:
                    print("Error importing row ", p)
                    print(repr(e))

            self.stdout.write(
                self.style.SUCCESS("Persons have been successfully imported.")
            )

        def import_places():
            MODEL = "apis_entities.place"
            self.stdout.write("importing places")
            places = df[df.model == MODEL]
            for _, p in tqdm(places.iterrows(), total=places.shape[0]):
                place_type_pk = None
                ted = get_all_entity_data(p.pk, MODEL)
                old_data = ted["fields"]
                if "kind" in old_data:
                    place_type_pk = old_data.get("kind")
                    old_data.pop("kind")

                p, _ = Place.objects.get_or_create(pk_old=old_data["pk_old"])
                p.__dict__.update(**old_data)

                if place_type_pk:
                    place_type_data = get_base_vocab_data(place_type_pk)
                    place_type, _ = PlaceType.objects.get_or_create(**place_type_data)
                    p.kind = place_type

                p.save()
                create_collections(ted["collections"], p)

            self.stdout.write(
                self.style.SUCCESS("Places have been successfully imported.")
            )

        def import_institutions():
            MODEL = "apis_entities.institution"
            self.stdout.write("importing institutions")
            institutions = df[df.model == MODEL]
            for _, p in tqdm(institutions.iterrows(), total=institutions.shape[0]):
                i_type_pk = None
                ted = get_all_entity_data(p.pk, MODEL)
                old_data = ted["fields"]
                if "kind" in old_data:
                    i_type_pk = old_data.get("kind")
                    old_data.pop("kind")

                if old_data:
                    p, _ = Institution.objects.get_or_create(pk_old=old_data["pk_old"])
                    p.__dict__.update(**old_data)
                    if i_type_pk:
                        i_type_data = get_base_vocab_data(i_type_pk)
                        i_type, _ = InstitutionType.objects.get_or_create(**i_type_data)
                        p.kind = i_type

                    p.save()
                create_collections(ted["collections"], p)

            self.stdout.write(
                self.style.SUCCESS("Institutions have been successfully imported.")
            )

        def import_events():
            MODEL = "apis_entities.event"
            self.stdout.write("importing events")
            df_subset = df[df.model == MODEL]
            for _, row in tqdm(df_subset.iterrows(), total=df_subset.shape[0]):
                type_pk = None
                ted = get_all_entity_data(row.pk, MODEL)
                old_data = ted["fields"]
                if "kind" in old_data:
                    type_pk = old_data.get("kind")
                    old_data.pop("kind")

                if old_data:
                    p, _ = Event.objects.get_or_create(pk_old=old_data["pk_old"])
                    p.__dict__.update(**old_data)

                    if type_pk:
                        type_data = get_base_vocab_data(type_pk)
                        i_type, _ = EventType.objects.get_or_create(**type_data)
                        p.event_type = i_type

                    p.save()
                create_collections(ted["collections"], p)

            self.stdout.write(
                self.style.SUCCESS("Events have been successfully imported.")
            )

        def import_works():
            MODEL = "apis_entities.work"
            self.stdout.write("importing works")
            df_subset = df[df.model == MODEL]
            for _, row in tqdm(df_subset.iterrows(), total=df_subset.shape[0]):
                type_pk = None
                subject_heading_ids = None
                ted = get_all_entity_data(row.pk, MODEL)
                old_data = ted["fields"]
                if "kind" in old_data:
                    type_pk = old_data.get("kind")
                    old_data.pop("kind")
                if "subject_headings" in old_data:
                    subject_heading_ids = old_data.get("subject_headings")
                    old_data.pop("subject_headings")

                if old_data:
                    p, _ = Work.objects.get_or_create(pk_old=old_data["pk_old"])
                    p.__dict__.update(**old_data)

                    if type_pk:
                        type_data = get_base_vocab_data(type_pk)
                        kind, _ = WorkType.objects.get_or_create(**type_data)
                        p.kind = kind

                    if subject_heading_ids:
                        for id in subject_heading_ids:
                            val = get_base_vocab_data(id)
                            rec, _ = SubjectHeading.objects.get_or_create(**val)
                            p.subject_heading.add(rec)

                    p.save()

                create_collections(ted["collections"], p)

            self.stdout.write(
                self.style.SUCCESS("Works have been successfully imported.")
            )

        def import_expressions():
            MODEL = "apis_entities.expression"
            self.stdout.write("importing expressions")
            df_subset = df[df.model == MODEL]
            for _, row in tqdm(df_subset.iterrows(), total=df_subset.shape[0]):
                try:
                    ted = get_all_entity_data(row.pk, MODEL)
                    old_data = ted["fields"]
                    VOCAB_FIELDS = {"script_title": {}, "script_body": {}}
                    for f in VOCAB_FIELDS.keys():
                        if not f in old_data:
                            continue
                        VOCAB_FIELDS[f] = get_base_vocab_data(old_data[f])
                        old_data.pop(f)

                    language_ids = []
                    if "language" in old_data:
                        language_ids = old_data.get("language")
                        old_data.pop("language")

                    if old_data:
                        p, _ = Expression.objects.get_or_create(
                            pk_old=old_data["pk_old"]
                        )
                        p.__dict__.update(**old_data)

                        if language_ids:
                            for l_id in language_ids:
                                l, _ = Language.objects.get_or_create(
                                    **get_base_vocab_data(l_id)
                                )
                                p.language.add(l)

                        if VOCAB_FIELDS["script_title"]:
                            script_type_title, _ = ScriptType.objects.get_or_create(
                                **VOCAB_FIELDS["script_title"]
                            )
                            p.script_type_title = script_type_title

                        if VOCAB_FIELDS["script_body"]:
                            script_type_body, _ = ScriptType.objects.get_or_create(
                                **VOCAB_FIELDS["script_body"]
                            )
                            p.script_type_body = script_type_body

                        p.save()

                        create_collections(ted["collections"], p)

                except Exception as e:
                    print("Error importing row ", p)

            self.stdout.write(
                self.style.SUCCESS("Expressions have been successfully imported.")
            )

        def import_manuscripts():
            MODEL = "apis_entities.manuscript"
            self.stdout.write("importing manuscripts")
            df_subset = df[df.model == MODEL]
            for _, row in tqdm(df_subset.iterrows(), total=df_subset.shape[0]):
                try:
                    condition_pks = None
                    ted = get_all_entity_data(row.pk, MODEL)
                    old_data = ted["fields"]
                    if "manuscript_conditions" in old_data:
                        condition_pks = old_data.get("manuscript_conditions")
                        old_data.pop("manuscript_conditions")

                    p, _ = Manuscript.objects.get_or_create(pk_old=old_data["pk_old"])
                    p.__dict__.update(**old_data)

                    if condition_pks:
                        for pk in condition_pks:
                            condition_data = get_base_vocab_data(pk)
                            condition, _ = ManuscriptCondition.objects.get_or_create(
                                **condition_data
                            )
                            p.condition.add(condition)

                    p.save()
                    create_collections(ted["collections"], p)
                except Exception as e:
                    print("Error importing row ", row)

            self.stdout.write(
                self.style.SUCCESS("Manuscripts have been successfully imported.")
            )

        def import_manuscript_parts():
            MODEL = "apis_entities.manuscriptpart"
            self.stdout.write("importing manuscript parts")
            df_subset = df[df.model == MODEL]
            for _, row in tqdm(df_subset.iterrows(), total=df_subset.shape[0]):
                try:
                    mpart_type_pk = None
                    ted = get_all_entity_data(row.pk, MODEL)
                    old_data = ted["fields"]
                    if "type" in old_data:
                        mpart_type_pk = old_data.get("type")
                        old_data.pop("type")

                    p, _ = ManuscriptPart.objects.get_or_create(
                        pk_old=old_data["pk_old"]
                    )
                    p.__dict__.update(**old_data)
                    if mpart_type_pk:
                        mpart_type_data = get_base_vocab_data(mpart_type_pk)
                        mpart_type, _ = ManuscriptPartType.objects.get_or_create(
                            **mpart_type_data
                        )
                    p.kind = mpart_type

                    p.save()
                    create_collections(ted["collections"], p)
                except Exception as e:
                    print("Error importing row ", row)

            self.stdout.write(
                self.style.SUCCESS("Manuscript parts have been successfully imported.")
            )

        import_persons()
        import_places()
        import_institutions()
        import_events()
        import_works()
        import_expressions()
        import_manuscripts()
        import_manuscript_parts()

        self.stdout.write(
            self.style.SUCCESS("Entities have been successfully imported.")
        )
