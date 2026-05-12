import ast
from collections import defaultdict

from apis_core.collections.models import SkosCollection
from django.core.management.base import BaseCommand
from django.db.models import CharField, Value
from django.db.models.functions import Concat
import pandas as pd
from tqdm import tqdm

from apis_ontology.models import *


def extract_manuscript_data(manuscript_str):
    manuscript_data = ast.literal_eval(manuscript_str)
    try:
        manuscript_data["name"] = " ".join(
            manuscript_data.get("xml_id", "").split("_")[2:]
        )
    except Exception:
        manuscript_data["name"] = manuscript_data.get("xml_id", "")

    return manuscript_data


def extract_copied_dates(copied_date_str):
    copied_date_dict = ast.literal_eval(copied_date_str)
    copy_dates = {}
    if "notBefore" in copied_date_dict:
        copy_dates["start"] = copied_date_dict["notBefore"]
    if "notAfter" in copied_date_dict:
        copy_dates["end"] = copied_date_dict["notAfter"]
    if "when" in copied_date_dict:
        copy_dates["start"] = copied_date_dict["when"]
        copy_dates["end"] = copied_date_dict["when"]
    return copy_dates


def extract_person_data(row):
    try:
        author_list = ast.literal_eval(row["author_names"])
    except Exception:
        return []
    names = []
    refs = []  #
    name_in_arabic = ""
    for aut in author_list:
        aut_text = aut.get("text", "")
        refs.append(aut.get("ref", ""))
        if aut_text:
            if aut.get("lang") == "ara":
                name_in_arabic = aut_text

            else:
                names.append(aut_text)

    refs = [ref.strip() for ref in refs if ref]
    return {
        "name_in_arabic": name_in_arabic,
        "bio": row.get("bio", ""),
        "alternative_names": "\n".join(names[1:]),
        "surname": names[0] if names else "",
        "references": "\n".join(set(refs)),
    }


def extract_copyist_data(row):
    """Extracts a list of copyist names from a stringified list of dicts in the 'copyist_names' column."""
    copyist_data = {"surname": "Unknown", "name_in_arabic": ""}
    refs = []
    try:
        copyist_list = ast.literal_eval(row["copyist_names"])
        for copyist in copyist_list:
            refs.append(copyist.get("ref", ""))
            copyist_text = copyist.get("text", "")
            if "(" in copyist_text:
                parts = copyist_text.split("(")
                copyist_data["surname"] = parts[0].strip()
                copyist_data["name_in_arabic"] = " ".join(parts[1:]).rstrip(")").strip()
    except Exception:
        pass

    refs = [ref.strip() for ref in refs if ref]
    copyist_data["references"] = "\n".join(set(refs))

    return copyist_data


def match_person_from_names(names):
    """
    Given a stringified list of author dicts, return the first matching Person record or None.
    Checks alternative_names, name_in_arabic, and forename+surname combinations.
    """
    try:
        author_list = ast.literal_eval(names)
    except Exception:
        return None
    for aut in author_list:
        aut_text = aut.get("text", "").strip()
        # Check alternative_names
        found_person = Person.objects.filter(
            alternative_names__icontains=aut_text
        ).first()
        if found_person:
            return found_person
        # Check name_in_arabic
        found_person = Person.objects.filter(name_in_arabic__iexact=aut_text).first()
        if found_person:
            return found_person
        # Check forename + surname as a single field
        found_person = (
            Person.objects.annotate(
                full_name=Concat(
                    "forename", Value(" "), "surname", output_field=CharField()
                )
            )
            .filter(full_name__iexact=aut_text)
            .first()
        )
        if found_person:
            return found_person
    return None


def extract_work_fields(row, description=None):
    name = None
    arabic_name = None
    try:
        work_list = ast.literal_eval(row["work"])
    except Exception:
        return {"name": None, "arabic_name": None, "description": description}
    if not isinstance(work_list, list):
        return {"name": None, "arabic_name": None, "description": description}
    for entry in work_list:
        if not isinstance(entry, dict):
            continue
        lang = entry.get("lang")
        typ = entry.get("type")
        text = entry.get("text")
        # Name: first Latin script, type None or 'standard'
        if (
            name is None
            and lang
            and "Latn" in lang
            and (typ is None or typ == "standard")
        ):
            name = text
        # Arabic name: first Arabic script, type None or 'standard'
        if arabic_name is None and lang == "ara" and (typ is None or typ == "standard"):
            arabic_name = text
        alternative_names = []
        if text not in [name, arabic_name]:
            alternative_names.append(text)

        if not name:
            name = alternative_names.pop(0) if alternative_names else None
    return {
        "name": name,
        "arabic_name": arabic_name,
        "alternative_names": alternative_names,
        "description": row["work_description"],
    }


class Command(BaseCommand):
    help = "Import Islam Anatolia data"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file to read.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, do not write to the database.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options.get("dry_run", True)
        entity_collection, _ = SkosCollection.objects.get_or_create(
            name="IslamAnatolia entities"
        )
        relation_collection, _ = SkosCollection.objects.get_or_create(
            name="IslamAnatolia relations"
        )
        try:
            df = pd.read_csv(csv_path).fillna("")
            self.stdout.write(
                self.style.SUCCESS(f"Successfully read CSV file: {csv_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {e}"))
            return

        import_log = defaultdict(list)  # To store import results for each row
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Importing…"):
            import_tracking = f"row_{idx}"
            manuscript_data = extract_manuscript_data(row["manuscript"])
            manuscript = Manuscript.objects.filter(
                identifier__iexact=manuscript_data.get("xml_id", "")
            ).first()
            if manuscript:
                import_log[row.source].append(f"Manuscript found: {manuscript.pk}")
                if not dry_run:
                    entity_collection.add(manuscript)
            else:
                import_log[row.source].append(f"New manuscript: {manuscript_data}")
                if not dry_run:
                    try:
                        manuscript = Manuscript.objects.create(
                            identifier=manuscript_data.get("xml_id", ""),
                            name=manuscript_data.get("name", ""),
                        )
                        import_log[row.source].append(
                            f"Created manuscript with ID: {manuscript.id}"
                        )
                        entity_collection.add(manuscript)
                    except Exception as e:
                        import_log[row.source].append(f"Error creating manuscript: {e}")
                        continue
            work_data = extract_work_fields(row)
            work = Work.objects.filter(name__unaccent__iexact=work_data["name"]).first()
            if work:
                import_log[row.source].append(f"Work found: {work.id}")
                if not dry_run:
                    entity_collection.add(work)
            else:
                import_log[row.source].append(f"New work: {work_data['name']}")
                if not dry_run:
                    try:
                        work = Work.objects.create(
                            name=work_data["name"],
                            name_in_arabic=work_data["arabic_name"],
                            description=work_data["description"],
                        )
                        import_log[row.source].append(
                            f"Created work with ID: {work.id}"
                        )
                        # Add to entity collection
                        entity_collection.add(work)
                    except Exception as e:
                        import_log[row.source].append(f"Error creating work: {e}")
                        continue
            contains_copy_of = ContainsCopyOf.objects.filter(
                subj_object_id=manuscript.pk, obj_object_id=work.pk
            ).first()
            if contains_copy_of:
                import_log[row.source].append(
                    f"Found manuscript {manuscript.id} contains copy of work {work.id} with ContainsCopyOf relation"
                )
            else:
                import_log[row.source].append(
                    f"New ContainsCopyOf relation between manuscript {manuscript.id} and work {work.id}"
                )

                if not dry_run:
                    contains_copy_of = ContainsCopyOf.objects.create(
                        subj=manuscript, obj=work
                    )
                    relation_collection.add(contains_copy_of)

            if not dry_run:
                expression, created = Expression.objects.get_or_create(
                    title=work_data["name"], hidden_import_log=import_tracking
                )
                entity_collection.add(expression)
                if created:
                    import_log[row.source].append(
                        f"Created expression with ID: {expression.id}"
                    )
                else:
                    import_log[row.source].append(
                        f"Found existing expression with ID: {expression.id}"
                    )

            a_copy_of = ACopyOf.objects.filter(
                subj_object_id=expression.pk, obj_object_id=work.pk
            ).first()
            if a_copy_of:
                import_log[row.source].append(
                    f"Found {expression.id} copy of work {work.id} with ACopyOf relation"
                )
            else:
                import_log[row.source].append(
                    f"New ACopyOf relation between expression {expression.id} and work {work.id}"
                )

                if not dry_run:
                    a_copy_of = ACopyOf.objects.create(subj=expression, obj=work)
                    relation_collection.add(a_copy_of)
            author = match_person_from_names(row["author_names"])
            if author:
                import_log[row.source].append(f"Author found: {author.id}")
                if not dry_run:
                    entity_collection.add(author)
            else:
                person_data = extract_person_data(row)
                import_log[row.source].append(f"New Person: {person_data}")
                if not dry_run:
                    author = Person.objects.create(**person_data)
                    entity_collection.add(author)
            if work and author:
                # Check if Author relation already exists to avoid duplicates
                existing_relation = AuthorOf.objects.filter(
                    subj_object_id=author.pk, obj_object_id=work.pk
                ).exists()
                if not existing_relation and not dry_run:
                    relation = AuthorOf.objects.create(subj=author, obj=work)
                    import_log[row.source].append(
                        f"Linked author {author.id} to work {work.id}"
                    )
                    # Add relation to relation collection
                    relation_collection.add(relation)

            copyist = match_person_from_names(row.copyist_names)
            if copyist:
                import_log[row.source].append(f"Copyist found: {copyist.id}")
                if not dry_run:
                    entity_collection.add(copyist)
            else:
                copyist_data = extract_copyist_data(row)
                import_log[row.source].append(f"New Copyist: {copyist_data}")
                if not dry_run:
                    copyist = Person.objects.create(**copyist_data)
                    entity_collection.add(copyist)

            if copyist and expression:
                existing_relation = CopiedBy.objects.filter(
                    subj_object_id=expression.pk, obj_object_id=copyist.pk
                ).exists()
                if not existing_relation and not dry_run:
                    copied_dates = extract_copied_dates(row.copied_date)
                    relation = CopiedBy.objects.create(
                        subj=expression, obj=copyist, **copied_dates
                    )
                    import_log[row.source].append(
                        f"Linked copyist {copyist.id} to expression {expression.id}"
                    )
                    relation_collection.add(relation)

            institution = Institution.objects.filter(
                name__unaccent__iexact=row["institution"]
            ).first()
            if institution:
                import_log[row.source].append(f"Institution found: {institution.id}")
                if not dry_run:
                    entity_collection.add(institution)
            else:
                import_log[row.source].append(f"New institution: {row['institution']}")
                if not dry_run:
                    try:
                        institution = Institution.objects.create(
                            name=row["institution"]
                        )
                        import_log[row.source].append(
                            f"Created institution with ID: {institution.id}"
                        )
                        # Add institution to entity collection
                        entity_collection.add(institution)
                    except Exception as e:
                        import_log[row.source].append(
                            f"Error creating institution: {e}"
                        )

            held_in = HeldIn.objects.filter(
                subj_object_id=manuscript.pk, obj_object_id=institution.pk
            ).first()
            if held_in:
                import_log[row.source].append(
                    f"Found manuscript {manuscript.id} held in institution {institution.id} with HeldIn relation"
                )
            else:
                import_log[row.source].append(
                    f"New HeldIn relation between manuscript {manuscript.id} and institution {institution.id}"
                )

                if not dry_run:
                    held_in = HeldIn.objects.create(subj=manuscript, obj=institution)
                    relation_collection.add(held_in)

        pd.DataFrame.from_dict(import_log, orient="index").to_csv("import_status.csv")
        self.stdout.write(
            self.style.SUCCESS(
                "Import process completed. Status saved to import_status.csv"
            )
        )
