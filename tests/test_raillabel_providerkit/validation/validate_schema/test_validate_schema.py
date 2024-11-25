# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.validation import validate_schema


def test_no_errors__empty():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}

    actual = validate_schema(data)
    assert actual == []


def test_required_field_missing():
    data = {"openlabel": {}}

    actual = validate_schema(data)
    assert len(actual) == 1
    assert "$.openlabel" in actual[0]
    assert "required" in actual[0]
    assert "metadata" in actual[0]
    assert "missing" in actual[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
