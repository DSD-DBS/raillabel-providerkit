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
        "$.openlabel.frames.1.objects.113c2b35-0965-4c80-a212-08b262e94203.object_data.poly2d.0.closed:"
        in actual[0]
    )
    assert "bool" in actual[0]
    assert "NOT A BOOLEAN" in actual[0]


def test_wrong_type_int():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}, "frames": {"NOT AN INT": {}}}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.frames:" in actual[0]
    assert "int" in actual[0]
    assert "NOT AN INT" in actual[0]


def test_wrong_type_string():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0", "comment": False}}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.metadata.comment:" in actual[0]
    assert "str" in actual[0]
    assert "False" in actual[0]


def test_wrong_type_float():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "coordinate_systems": {
                "rgb_middle": {
                    "pose_wrt_parent": {
                        "translation": (None, 0.0, 0.0),
                        "quaternion": (0.0, 0.0, 0.0, 0.0),
                    },
                    "parent": "",
                    "type": "sensor",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.coordinate_systems.rgb_middle.pose_wrt_parent.translation.0:" in actual[0]
    assert "float" in actual[0]
    assert "None" in actual[0]


def test_wrong_type_uuid():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "objects": {
                "NOT A VALID UUID": {
                    "name": "person_0001",
                    "type": "person",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.objects:" in actual[0]
    assert "UUID" in actual[0]
    assert "NOT A VALID UUID" in actual[0]


def test_tuple_too_long():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "coordinate_systems": {
                "rgb_middle": {
                    "pose_wrt_parent": {
                        "translation": (0.0, 0.0, 0.0, 0.0),  # should have length of 3
                        "quaternion": (0.0, 0.0, 0.0, 0.0),
                    },
                    "parent": "",
                    "type": "sensor",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel.coordinate_systems.rgb_middle.pose_wrt_parent.translation:" in actual[0]
    assert "length" in actual[0]
    assert "4" in actual[0]
    assert "3" in actual[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
