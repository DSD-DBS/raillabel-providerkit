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
from raillabel_providerkit.validation.validate_onthology._onthology_classes._sensor_type import (
    _SensorType,
)
from raillabel_providerkit.validation import IssueType
from raillabel.format import Bbox, Point2d, Size2d


def test_fromdict__empty():
    object_class = _ObjectClass.fromdict({})
    assert len(object_class.attributes) == 0


def test_fromdict__simple(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"isSomething": example_boolean_attribute_dict})
    assert len(object_class.attributes) == 1
    assert "isSomething" in object_class.attributes


def test_check__correct(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute": True},
    )
    issues = object_class.check(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert issues == []


def test_check__all_error_types(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute_1": "not-a-boolean", "unknown-attribute": False},
    )
    issues = object_class.check(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert len(issues) == 3
    issue_types_found = [issue.type for issue in issues]
    assert IssueType.ATTRIBUTE_UNDEFINED in issue_types_found
    assert IssueType.ATTRIBUTE_MISSING in issue_types_found
    assert IssueType.ATTRIBUTE_TYPE in issue_types_found


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


def test_check_undefined_attributes__correct(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute": True},
    )
    issues = object_class._check_undefined_attributes(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert issues == []


def test_check_undefined_attributes__two_undefined(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute": True, "color": "yellow", "is_a_banana": False},
    )
    issues = object_class._check_undefined_attributes(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert len(issues) == 2
    for issue in issues:
        assert issue.type == IssueType.ATTRIBUTE_UNDEFINED


def test_check_missing_attributes__correct(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute_1": True, "test_attribute_2": True},
    )
    issues = object_class._check_missing_attributes(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert issues == []


def test_check_missing_attributes__one_missing(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute_2": True},
    )
    issues = object_class._check_missing_attributes(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_MISSING


def test_check_false_attribute_type__correct(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute": True},
    )
    issues = object_class._check_false_attribute_type(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert issues == []


def test_check_false_attribute_type__incorrect(example_boolean_attribute_dict, ignore_uuid):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=ignore_uuid,
        sensor_id="some_sensor_id",
        attributes={"test_attribute": "i-like-trains"},
    )
    issues = object_class._check_false_attribute_type(ignore_uuid, annotation, _SensorType.CAMERA, 0)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE


def test_compile_applicable_attributes__not_matching(example_boolean_attribute_dict):
    example_boolean_attribute_dict["sensor_types"] = ["camera"]
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    assert object_class._compile_applicable_attributes(_SensorType.LIDAR) == {}


def test_compile_applicable_attributes__matching(example_boolean_attribute_dict):
    example_boolean_attribute_dict["sensor_types"] = ["camera"]
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    assert "test_attribute" in object_class._compile_applicable_attributes(_SensorType.CAMERA)
