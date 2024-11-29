# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

from pydantic_core import ValidationError
from raillabel.json_format import JSONScene


def validate_schema(data: dict) -> list[str]:
    """Validate a scene for adherence to the raillabel schema."""
    try:
        JSONScene(**data)
    except ValidationError as errors:
        return _make_errors_readable(errors)
    else:
        return []


def _make_errors_readable(errors: ValidationError) -> list[str]:  # noqa: C901
    readable_errors = []
    for error in json.loads(errors.json()):
        match error["type"]:
            case "missing":
                readable_errors.append(_convert_missing_error_to_string(error))

            case "extra_forbidden":
                readable_errors.append(_convert_unexpected_field_error_to_string(error))

            case "literal_error":
                readable_errors.append(_convert_literal_error_to_string(error))

            case "bool_type" | "bool_parsing":
                readable_errors.append(_convert_false_type_error_to_string(error, "bool"))

            case "int_type" | "int_parsing" | "int_from_float":
                readable_errors.append(_convert_false_type_error_to_string(error, "int"))

            case "decimal_type" | "decimal_parsing":
                readable_errors.append(_convert_false_type_error_to_string(error, "Decimal"))

            case "string_type" | "string_parsing":
                readable_errors.append(_convert_false_type_error_to_string(error, "str"))

            case "float_type" | "float_parsing":
                readable_errors.append(_convert_false_type_error_to_string(error, "float"))

            case "uuid_type" | "uuid_parsing":
                readable_errors.append(_convert_false_type_error_to_string(error, "UUID"))

            case "too_long":
                readable_errors.append(_convert_too_long_error_to_string(error))

            case _:
                readable_errors.append(str(error))

    return readable_errors


def _build_error_path(loc: list[str]) -> str:
    path = "$"
    for part in loc:
        path += f".{part}"
    return path


def _convert_missing_error_to_string(error: dict) -> str:
    return f"{_build_error_path(error['loc'][:-1])}: required field '{error['loc'][-1]}' is missing."


def _convert_unexpected_field_error_to_string(error: dict) -> str:
    return f"{_build_error_path(error['loc'][:-1])}: found unexpected field '{error['loc'][-1]}'."


def _convert_literal_error_to_string(error: dict) -> str:
    return (
        f"{_build_error_path(error['loc'])}: value '{error['input']}' does not match allowed values "
        f"({error['ctx']['expected']})."
    )


def _convert_false_type_error_to_string(error: dict, target_type: str) -> str:
    if "[key]" in error["loc"]:
        error_path = _build_error_path(error["loc"][:-2])
    else:
        error_path = _build_error_path(error["loc"])

    return f"{error_path}: value '{error['input']}' could not be interpreted " f"as {target_type}."


def _convert_too_long_error_to_string(error: dict) -> str:
    return (
        f"{_build_error_path(error['loc'])}: should have length of {error['ctx']['actual_length']} "
        f"but has length of {error['ctx']['max_length']}."
    )
