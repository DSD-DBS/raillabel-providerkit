# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import typing as t
from pathlib import Path

import jsonschema
import pytest
import yaml

# == Fixtures =========================


@pytest.fixture
def schema_path() -> Path:
    return (
        Path(__file__).parent.parent.parent.parent.parent
        / "raillabel_providerkit"
        / "validation"
        / "validate_onthology"
        / "onthology_schema_v1.yaml"
    )


@pytest.fixture
def schema(schema_path) -> dict:
    with schema_path.open() as f:
        schema_data = yaml.safe_load(f)
    return schema_data


@pytest.fixture
def validator(schema) -> jsonschema.Draft7Validator:
    return jsonschema.Draft7Validator(schema)


def schema_errors(data: dict, validator: jsonschema.Draft7Validator) -> t.List[str]:
    errors = []

    for error in validator.iter_errors(data):
        errors.append("$" + error.json_path[1:] + ": " + str(error.message))

    return errors


# == Tests =========================


def test_classes(validator):
    data = {
        "person": {},
        "train": {},
    }

    assert schema_errors(data, validator) == []


def test_class_unsupported_field(validator):
    data = {"person": {"UNSUPPORTED_FIELD": {}}}

    assert schema_errors(data, validator) == [
        "$.person: Additional properties are not allowed ('UNSUPPORTED_FIELD' was unexpected)",
    ]


def test_attributes_field(validator):
    data = {"person": {"attributes": {}}}

    assert schema_errors(data, validator) == []


def test_attribute_string(validator):
    data = {"person": {"attributes": {"name": "string"}}}

    assert schema_errors(data, validator) == []


def test_attribute_integer(validator):
    data = {"person": {"attributes": {"number_of_fingers": "integer"}}}

    assert schema_errors(data, validator) == []


def test_attribute_boolean(validator):
    data = {"person": {"attributes": {"number_of_fingers": "boolean"}}}

    assert schema_errors(data, validator) == []


def test_attribute_single_select(validator):
    data = {
        "person": {
            "attributes": {
                "carrying": {
                    "type": "single-select",
                    "options": ["groceries", "a baby", "the new Slicer-Dicer 3000 (WOW!)"],
                }
            }
        }
    }

    assert schema_errors(data, validator) == []


def test_attribute_multi_select(validator):
    data = {
        "person": {
            "attributes": {
                "carrying": {
                    "type": "multi-select",
                    "options": ["groceries", "a baby", "the new Slicer-Dicer 3000 (WOW!)"],
                }
            }
        }
    }

    assert schema_errors(data, validator) == []


def test_attribute_vector(validator):
    data = {"person": {"attributes": {"carrying": "vector"}}}

    assert schema_errors(data, validator) == []


def test_sensor_types(validator):
    data = {
        "person": {
            "sensor_types": {
                "camera": {},
                "lidar": {},
                "radar": {},
            }
        }
    }

    assert schema_errors(data, validator) == []


def test_sensor_types_unsupported_type(validator):
    data = {
        "person": {
            "sensor_types": {
                "UNSUPPORTED_SENSOR_TYPE": {},
                "lidar": {},
            }
        }
    }

    assert len(schema_errors(data, validator)) == 1


def test_sensor_type_attributes(validator):
    data = {
        "person": {
            "sensor_types": {
                "lidar": {"attributes": {"name": "string"}},
            }
        }
    }

    assert schema_errors(data, validator) == []


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
