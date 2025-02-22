from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
import pandas as pd
from django.apps import apps
from tqdm.auto import tqdm
import re
import pandas as pd


class Command(BaseCommand):
    help = "import relations from file"

    def add_arguments(self, parser):
        parser.add_argument("dump", type=str, help="dump file name")

    def handle(self, *args, **kwargs):
        def extract_relation_models():
            df_vocabsbaseclass = df[
                df["model"] == "apis_vocabularies.vocabsbaseclass"
            ].copy()
            df_relationbaseclass = df[
                df["model"] == "apis_vocabularies.relationbaseclass"
            ].copy()
            df_vocabnames = df[df["model"] == "apis_vocabularies.vocabnames"].copy()

            # Extract necessary fields from the fields dictionaries
            df_vocabsbaseclass["name"] = df_vocabsbaseclass["fields"].apply(
                lambda x: x.get("name", "")
            )
            df_vocabsbaseclass["vocab_name"] = df_vocabsbaseclass["fields"].apply(
                lambda x: x.get("vocab_name", None)
            )
            df_relationbaseclass["name_reverse"] = df_relationbaseclass["fields"].apply(
                lambda x: x.get("name_reverse", "")
            )
            df_vocabnames["vocabnames"] = df_vocabnames["fields"].apply(
                lambda x: x.get("name", "")
            )

            # Filter the vocabnames DataFrame to include only rows with pk in df_vocabsbaseclass['vocab_name']
            filtered_vocabnames_df = df_vocabnames[
                df_vocabnames["pk"].isin(df_vocabsbaseclass["vocab_name"])
            ]

            # Merge the DataFrames on the 'pk' column using inner joins
            merged_df = pd.merge(
                df_relationbaseclass[["pk", "name_reverse"]],
                df_vocabsbaseclass[["pk", "name", "vocab_name"]],
                on="pk",
                how="inner",
            )
            relations_df = pd.merge(
                merged_df,
                filtered_vocabnames_df[["pk", "vocabnames"]],
                left_on="vocab_name",
                right_on="pk",
                how="left",
                suffixes=("", "_vocabname"),
            )

            # Drop redundant columns
            relations_df = relations_df.drop(columns=["vocab_name", "pk_vocabname"])
            relations_df.rename(columns={"name": "name_forward"}, inplace=True)

            # Function to split vocabnames into two words based on uppercase transition
            def split_vocabname(vocabname):
                matches = re.findall(r"[A-Z][a-z]*", vocabname)
                if len(matches) >= 2:
                    return (
                        f"apis_ontology.{matches[0].lower()}",
                        f"apis_ontology.{matches[1].lower()}",
                    )
                return vocabname, ""

            def new_rel_classname(property_name):
                return f"{property_name.title().replace('-','').replace(' ', '')}"

            # Apply the function to split the vocabnames column
            relations_df[["subj_class", "obj_class"]] = relations_df[
                "vocabnames"
            ].apply(lambda x: pd.Series(split_vocabname(x)))
            relations_df["class_name"] = relations_df["name_forward"].apply(
                new_rel_classname
            )
            df_grouped = (
                relations_df.groupby("class_name")
                .agg(
                    {
                        "subj_class": lambda x: sorted(set(x)),
                        "obj_class": lambda x: sorted(set(x)),
                        "name_reverse": "first",
                        "name_forward": "first",
                        "pk": list,
                    }
                )
                .reset_index()
            )

            return df_grouped

        def get_rel_class(rel_pk):
            match = df_relations[df_relations["pk"].apply(lambda x: rel_pk in x)]
            if match.shape[0] != 1:
                self.stdout.write(
                    self.style.ERROR("Cannot finf the correct match for %s.", rel_pk)
                )
                print(match)

            return "apis_ontology." + match.iloc[0].class_name.lower()

        def validate_relations_model():
            print("Validating relations model ...")
            model_is_valid = True
            df_relations = extract_relation_models()
            for i, p in tqdm(
                df_relations.sort_values(by="class_name").iterrows(),
                total=df_relations.shape[0],
            ):
                class_name = p.class_name
                try:
                    model = apps.get_model(f"apis_ontology.{class_name.lower()}")
                except LookupError as le:
                    model_is_valid = False
                    print(
                        f"class {class_name}(Relation, NomanslandRelationMixin, VersionMixin): "
                    )
                    print(
                        f"\trelation_type_old = {p.pk} # pk of Property in apis_relations"
                    )
                    print(f"\tsubj_model = {p.subj_class}")
                    print(f"\tobj_model = {p.obj_class}")
                    print(f"\t@classmethod")
                    print(f"\tdef reverse_name(cls) -> str:")
                    print(f'\t\treturn "{p.name_reverse}"\n')

            return model_is_valid, df_relations

        def create_relations_instances():
            print("Creating relations instances ...")
            relation_rows = df[df.model.str.startswith("apis_relations.")]
            for i, row in tqdm(relation_rows.iterrows(), total=relation_rows.shape[0]):
                RelModel = apps.get_model(get_rel_class(row.fields["relation_type"]))
                rel_data = {"pk_old": row.pk, **row.fields}
                subj_key = ""
                obj_key = ""
                for subj_model in RelModel.subj_model:
                    subj_model = subj_model.__name__.lower()
                    if f"related_{subj_model}A" in rel_data.keys():
                        subj_key = f"related_{subj_model}A"
                        obj_key = f"related_{subj_model}B"
                        break
                    if f"related_{subj_model}" in rel_data.keys():
                        subj_key = f"related_{subj_model}"
                        try:
                            obj_key = [
                                f"related_{obj_model.__name__.lower()}"
                                for obj_model in RelModel.obj_model
                                if f"related_{obj_model.__name__.lower()}"
                                in rel_data.keys()
                            ][0]
                            break
                        except IndexError:
                            continue

                try:
                    subj_pk, obj_pk = (rel_data[subj_key], rel_data[obj_key])
                    subj_model_name = f"apis_ontology.{subj_key.removeprefix('related_').removesuffix('A')}"
                    obj_model_name = f"apis_ontology.{obj_key.removeprefix('related_').removesuffix('B')}"
                    subj = apps.get_model(subj_model_name).objects.get(pk_old=subj_pk)
                    obj = apps.get_model(obj_model_name).objects.get(pk_old=obj_pk)
                    temp_entity_match = (
                        df[
                            (df.pk == row.pk)
                            & (df.model == "apis_metainfo.tempentityclass")
                        ]
                        .iloc[0]
                        .fields
                    )
                    data = {
                        "subj_object_id": subj.pk,
                        "obj_object_id": obj.pk,
                        "pk_old": row.pk,
                        "certainty": (
                            rel_data.get("certainty")
                            if rel_data.get("certainty")
                            else "unknown"
                        ),
                        "subj_content_type": ContentType.objects.get(
                            app_label="apis_ontology",
                            model=subj_model_name.split(".")[-1],
                        ),
                        "obj_content_type": ContentType.objects.get(
                            app_label="apis_ontology",
                            model=obj_model_name.split(".")[-1],
                        ),
                        "start": temp_entity_match.get("start_date_written"),
                        "end": temp_entity_match.get("end_date_written"),
                    }
                    rel, _ = RelModel.objects.get_or_create(**data)
                except Exception as e:
                    print(repr(e))
                    break

        ### handle command
        try:
            df = pd.read_json(kwargs["dump"])
            model_is_valid, df_relations = validate_relations_model()
            if not model_is_valid:
                self.stdout.write(
                    self.style.ERROR(
                        "Please update the Relations model before importing."
                    )
                )
            create_relations_instances()
        except KeyError:
            # print help message and quit
            self.stdout.write(self.style.ERROR("Please provide a dump file."))
            return

        self.stdout.write(self.style.SUCCESS("Relations imported."))
