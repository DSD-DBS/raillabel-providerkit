# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.validation.validate_ontology._ontology_classes._scope import _Scope
from raillabel_providerkit.validation.validate_ontology._ontology_classes._attributes._any_attribute import (
    _AnyAttribute,
)
from raillabel_providerkit.validation import IssueIdentifiers, IssueType


def test_supports__empty_dict():
    assert not _AnyAttribute.supports({})


def test_supports__correct(example_any_attribute_dict):
    assert _AnyAttribute.supports(example_any_attribute_dict)


def test_supports__invalid_type_string(example_string_attribute_dict):
    assert not _AnyAttribute.supports(example_string_attribute_dict)


def test_supports__invalid_type_dict(example_single_select_attribute_dict):
    assert not _AnyAttribute.supports(example_single_select_attribute_dict)


def test_fromdict__empty():
    with pytest.raises(ValueError):
        _AnyAttribute.fromdict({})


def test_fromdict__optional(example_any_attribute_dict):
    for val in [False, True]:
        example_any_attribute_dict["optional"] = val
        assert _AnyAttribute.fromdict(example_any_attribute_dict).optional == val


def test_fromdict__scope_invalid(example_any_attribute_dict):
    with pytest.raises(ValueError):
        example_any_attribute_dict["scope"] = "some random string"
        _AnyAttribute.fromdict(example_any_attribute_dict)


def test_fromdict__scope_empty(example_any_attribute_dict):
    del example_any_attribute_dict["scope"]
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.ANNOTATION


def test_fromdict__scope_annotation(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "annotation"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.ANNOTATION


def test_fromdict__scope_frame(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "frame"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.FRAME


def test_fromdict__scope_object(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "object"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.OBJECT


def test_check_type_and_value__correct_boolean(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", True, IssueIdentifiers()) == []


def test_check_type_and_value__correct_string(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", "hello_there", IssueIdentifiers()) == []


def test_check_type_and_value__correct_int(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", 42, IssueIdentifiers()) == []


def test_check_type_and_value__correct_list(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_type_and_value("example_name", ["this", "is", "a", "test"], IssueIdentifiers())
        == []
    )
