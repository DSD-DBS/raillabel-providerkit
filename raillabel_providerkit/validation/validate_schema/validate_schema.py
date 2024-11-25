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


def _make_errors_readable(errors: ValidationError) -> list[str]:
    readable_errors = []
    for error in json.loads(errors.json()):
        if error["type"] == "missing":
            readable_errors.append(_convert_missing_error_to_string(error))
        else:
            raise ValueError

    return readable_errors


def _convert_missing_error_to_string(error: dict) -> str:
    return f"{_build_error_path(error["loc"][:-1])}: required field '{error["loc"][-1]}' is missing."


def _build_error_path(loc: list[str]) -> str:
    path = "$"
    for part in loc:
        path += f".{part}"
    return path
