"""
This script imports data from https://github.com/StAResComp/IslamAnatoliaData
"""

import os
import csv
import glob
from xml.etree import ElementTree as ET
from tqdm import tqdm
import pandas as pd
from enum import Enum

from django.core.management.base import BaseCommand

NS = {"mods": "http://www.loc.gov/mods/v3", "tei": "http://www.tei-c.org/ns/1.0"}


class ResourceType(Enum):
    BOOK = "book"
    MANUSCRIPT = "manuscript"
    EXPRESSION = "expression"
    TEI = "TEI"
    AUTHORITY = "authority"
    UNKNOWN = "unknown"


class Command(BaseCommand):  # noqa: D101
    help = "Import data from IslamAnatoliaData"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--data_dir",
            type=str,
            help="Directory containing IslamAnatoliaData XML files",
            default="../../../data/IslamAnatoliaData",
        )

    def handle(self, *args, **options):  # noqa: D102
        def get_filetype(root):
            match root.tag:
                case tag if tag.endswith("mods"):
                    for genre in root.findall("mods:genre", NS):
                        authority = genre.attrib.get("authority", "")
                        if genre.text == "book" and authority in ("local", "marcgt"):
                            return ResourceType.BOOK.value
                        elif genre.text:
                            return genre.text.lower()
                case tag if tag.endswith("TEI"):
                    ms_desc = root.find(".//tei:msDesc", NS)
                    if ms_desc is not None:
                        return ResourceType.MANUSCRIPT.value

                    return ResourceType.TEI.value
                case tag if tag.endswith("mads"):
                    return ResourceType.AUTHORITY.value

            return root.tag

        def extract_mods_info(root):

            # Extract title
            title = None
            title_info = root.find("mods:titleInfo", NS)
            if title_info is not None:
                title_element = title_info.find("mods:title", NS)
                if title_element is not None:
                    title = title_element.text

            # Extract publication date (copyrightDate)
            pub_date = None
            origin_info = root.find("mods:originInfo", NS)
            if origin_info is not None:
                copyright_date = origin_info.find("mods:copyrightDate", NS)
                if copyright_date is not None:
                    pub_date = copyright_date.text

            # Extract author(s) (personal name with role='aut')
            authors = []
            for name in root.findall("mods:name", NS):
                role_term = name.find("mods:role/mods:roleTerm", NS)
                if (
                    role_term is not None
                    and role_term.attrib.get("type") == "code"
                    and role_term.text == "aut"
                ):
                    surname = name.find('mods:namePart[@type="family"]', NS)
                    forename = name.find('mods:namePart[@type="given"]', NS)
                    authors.append(
                        [
                            {
                                "forename": forename.text if forename else "",
                                "surname": surname if surname else "",
                            }
                        ]
                    )

            return {
                "title": title,
                "publication_date": pub_date,
                "authors": authors if authors else None,
            }

        print("Starting import of IslamAnatoliaData...")
        # get data_dir from arg

        data_dir = options.get("data_dir", "../../../data/IslamAnatoliaData")

        data_files = glob.glob(os.path.join(data_dir, "*.xml"))
        print("Found {} files to import.".format(len(data_files)))
        file_info = []
        works = []
        for filename in tqdm(data_files, desc="Importing files", total=len(data_files)):

            with open(filename, "r", encoding="utf-8") as f:
                xml_content = ET.parse(f)
                root = xml_content.getroot()
                filetype = get_filetype(root)
                file_info.append({"source": filename, "type": filetype})

                match filetype:
                    case ResourceType.BOOK:
                        w = extract_mods_info(root)
                        w.update({"source_file": filename})
                        works.append(w)
                    case _:
                        # Skip other types for now
                        continue
        df = pd.DataFrame(file_info)
        df.to_csv(
            "islam_anatolia_summary.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
        )
        print(df["type"].value_counts())
        pd.DataFrame(works).to_csv("islam_anatolia_works.csv", index=False)
        print(
            "Successfully imported IslamAnatoliaData; summary saved to islam_anatolia_summary.csv"
        )
