# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import argparse
import csv
import json
import sys
from pathlib import Path

import jsonschema
from tqdm import tqdm

from raillabel_providerkit import validate
from raillabel_providerkit.validation.issue import Issue

ISSUES_SCHEMA = Path(__file__).parent / "validation" / "issues_schema.json"


def store_issues_to_json(issues: list[Issue], filepath: Path) -> None:
    """Store the given issues in a .json file under the given filepath.

    Parameters
    ----------
    issues : list[Issue]
        The issues to store
    filepath : Path
        The path to the .json file to store the issues in
    """
    issues_serialized = [issue.serialize() for issue in issues]
    if not _adheres_to_issues_schema(issues_serialized):
        raise AssertionError
    issues_json = json.dumps(issues_serialized, indent=2)
    with Path.open(filepath, "w") as file:
        file.write(issues_json)


def _adheres_to_issues_schema(
    data: list[dict[str, str | dict[str, str | int] | list[str | int]]],
) -> bool:
    schema: dict
    with ISSUES_SCHEMA.open("r") as file:
        schema = json.load(file)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError:
        return False

    return True


def store_issues_to_csv(issues: list[Issue], filepath: Path) -> None:
    """Store the given issues in a .csv file under the given filepath.

    Parameters
    ----------
    issues : list[Issue]
        The issues to store
    filepath : Path
        The path to the .csv file to store the issues in

    Raises
    ------
    TypeError
        If the issues are malformed after serialization
    """
    issues_serialized = [issue.serialize() for issue in issues]

    file = Path.open(filepath, "w")

    writer = csv.writer(file, dialect="excel-tab")
    writer.writerow(
        [
            "issue_type",
            "frame",
            "sensor",
            "object_type",
            "object",
            "annotation",
            "attribute",
            "schema_path",
            "reason",
        ]
    )

    for issue in issues_serialized:
        issue_type = issue["type"]
        reason = issue.get("reason", "")
        if not isinstance(issue_type, str) or not isinstance(reason, str):
            raise TypeError

        row: list[str | int] = []
        row.append(issue_type)
        identifiers = issue["identifiers"]
        if isinstance(identifiers, dict):
            row.append(identifiers.get("frame", ""))
            row.append(identifiers.get("sensor", ""))
            row.append(identifiers.get("object_type", ""))
            row.append(identifiers.get("object", ""))
            row.append(identifiers.get("annotation", ""))
            row.append(identifiers.get("attribute", ""))
            row.append("")
        else:
            # It's a schema issue, so there are no standard identifiers
            row.extend(["", "", "", "", "", ""])
            row.append(str(identifiers))
        row.append(reason)

        writer.writerow(row)

    file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="raillabel_providerkit",
        description="Check a raillabel scene's annotations for errors",
        allow_abbrev=False,
    )
    parser.add_argument(
        "annotations_folder",
        help="The path to the folder that contains the annotation scenes to check",
    )
    parser.add_argument(
        "output_folder",
        help="The path to the folder where the validation results should be output",
    )
    parser.add_argument(
        "--ontology",
        metavar="FILEPATH",
        help="The path to the ontology against which to validate attributes of all annotations,"
        " by default none",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        default=False,
        help="Create human-readable .csv files containing the issues in addition to .json output",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        default=False,
        help="Don't create .json files containing the issues",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", default=False, help="Disable progress bars"
    )
    args = parser.parse_args()

    annotations_folder = Path(args.annotations_folder)
    output_folder = Path(args.output_folder)
    ontology_path = Path(args.ontology) if args.ontology is not None else None
    create_csv = args.csv
    create_json = not args.no_json
    quiet = args.quiet

    # Stop early if there is nothing to output
    if not create_csv and not create_json:
        sys.exit(0)

    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Get all scenes (.json files) in the folder and subfolders but ignore hidden folders
    scene_files = list(
        set(annotations_folder.glob("**/*.json")) - set(annotations_folder.glob(".*/**/*"))
    )

    for scene_path in tqdm(scene_files, desc="Validating files", disable=quiet):
        issues = validate(
            scene_path,
            ontology_path,
        )

        scene_name = scene_path.name
        if create_json:
            store_issues_to_json(issues, output_folder / scene_name.replace(".json", ".issues.json"))
        if create_csv:
            store_issues_to_csv(issues, output_folder / scene_name.replace(".json", ".issues.csv"))
