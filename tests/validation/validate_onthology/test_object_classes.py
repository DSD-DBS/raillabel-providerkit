# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.validation.validate_onthology._onthology_classes._object_classes import (
    _ObjectClass,
)
from raillabel_providerkit.validation import IssueIdentifiers, IssueType


# @pytest.fixture
# def simple_object_class_dict() -> dict:
#     return


def test_fromdict__empty():
    object_class = _ObjectClass.fromdict({})
    assert len(object_class.attributes) == 0


def test_fromdict__no_attributes():
    object_class = _ObjectClass.fromdict({"attributes": {}})
    assert len(object_class.attributes) == 0


def test_fromdict__simple():
    object_class = _ObjectClass.fromdict(
        {"attributes": {"isSomething": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    assert len(object_class.attributes) == 1
    assert "isSomething" in object_class.attributes
