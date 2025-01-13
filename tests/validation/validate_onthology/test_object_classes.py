# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.validation.validate_onthology._onthology_classes._object_classes import (
    _ObjectClass,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._boolean_attribute import (
    _BooleanAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._integer_attribute import (
    _IntegerAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._multi_reference_attribute import (
    _MultiReferenceAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._multi_select_attribute import (
    _MultiSelectAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._single_select_attribute import (
    _SingleSelectAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._string_attribute import (
    _StringAttribute,
)
from raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes._vector_attribute import (
    _VectorAttribute,
)
from raillabel_providerkit.validation import IssueIdentifiers, IssueType


def test_fromdict__empty():
    object_class = _ObjectClass.fromdict({})
    assert len(object_class.attributes) == 0


def test_fromdict__simple(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"isSomething": example_boolean_attribute_dict})
    assert len(object_class.attributes) == 1
    assert "isSomething" in object_class.attributes


def test_attribute_fromdict__empty():
    with pytest.raises(ValueError):
        _ObjectClass._attribute_fromdict({})


def test_attribute_fromdict__invalid_attribute_type():
    with pytest.raises(ValueError):
        _ObjectClass._attribute_fromdict(
            {"attribute_type": "some-invalid-attribute-type", "scope": "annotation"}
        )


def test_attribute_fromdict__boolean(example_boolean_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_boolean_attribute_dict)
    assert isinstance(result, _BooleanAttribute)


def test_attribute_fromdict__integer(example_integer_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_integer_attribute_dict)
    assert isinstance(result, _IntegerAttribute)


def test_attribute_fromdict__multi_reference(example_multi_reference_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_multi_reference_attribute_dict)
    assert isinstance(result, _MultiReferenceAttribute)


def test_attribute_fromdict__multi_select(example_multi_select_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_multi_select_attribute_dict)
    assert isinstance(result, _MultiSelectAttribute)


def test_attribute_fromdict__single_select(example_single_select_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_single_select_attribute_dict)
    assert isinstance(result, _SingleSelectAttribute)


def test_attribute_fromdict__string(example_string_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_string_attribute_dict)
    assert isinstance(result, _StringAttribute)


def test_attribute_fromdict__vector(example_vector_attribute_dict):
    result = _ObjectClass._attribute_fromdict(example_vector_attribute_dict)
    assert isinstance(result, _VectorAttribute)
