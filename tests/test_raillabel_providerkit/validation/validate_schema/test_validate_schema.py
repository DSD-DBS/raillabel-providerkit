# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.validation import validate_schema


def test_no_errors__empty():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}

    actual = validate_schema(data)
    assert actual == []


def test_required_field_missing():
    data = {"openlabel": {"metadata": {}}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.metadata" in actual[0]
    assert "required" in actual[0]
    assert "schema_version" in actual[0]
    assert "missing" in actual[0]


def test_unsupported_field():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}, "UNSUPPORTED_FIELD": {}}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel" in actual[0]
    assert "unexpected" in actual[0]
    assert "UNSUPPORTED_FIELD" in actual[0]


def test_unexpected_value():
    data = {"openlabel": {"metadata": {"schema_version": "SOMETHING UNSUPPORTED"}}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.metadata.schema_version" in actual[0]
    assert "value" in actual[0]
    assert "SOMETHING UNSUPPORTED" in actual[0]
    assert "'1.0.0'" in actual[0]


def test_wrong_type_bool():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "frames": {
                "1": {
                    "objects": {
                        "113c2b35-0965-4c80-a212-08b262e94203": {
                            "object_data": {
                                "poly2d": [
                                    {
                                        "closed": "NOT A BOOLEAN",
                                        "name": "not_important",
                                        "val": [],
                                        "mode": "MODE_POLY2D_ABSOLUTE",
                                        "coordinate_system": "not_important",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }
    }

    actual = validate_schema(data)
    assert len(actual) == 1
    assert (
        "$.openlabel.frames.1.objects.113c2b35-0965-4c80-a212-08b262e94203.object_data.poly2d.0"
        in actual[0]
    )
    assert "bool" in actual[0]
    assert "NOT A BOOLEAN" in actual[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
