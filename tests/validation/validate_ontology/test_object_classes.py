# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from uuid import UUID

from raillabel_providerkit.validation.validate_ontology._ontology_classes import (
    _ObjectClass,
    _BooleanAttribute,
    _IntegerAttribute,
    _MultiReferenceAttribute,
    _MultiSelectAttribute,
    _SingleSelectAttribute,
    _StringAttribute,
    _VectorAttribute,
    _SensorType,
)
from raillabel_providerkit.validation import IssueType, IssueIdentifiers
from raillabel.format import Bbox, Point2d, Size2d


def build_bbox_with_attributes(attributes: dict) -> Bbox:
    return Bbox(
        pos=Point2d(0, 0),
        size=Size2d(1, 1),
        object_id=UUID("00000000-0000-0000-0000-000000000000"),
        sensor_id="some_sensor_id",
        attributes=attributes,
    )


def build_identifiers(annotation: Bbox) -> IssueIdentifiers:
    return IssueIdentifiers(
        annotation=UUID("00000000-0000-0000-0000-000000000000"),
        frame=0,
        object=annotation.object_id,
        sensor=annotation.sensor_id,
    )


def test_fromdict__empty():
    object_class = _ObjectClass.fromdict({})
    assert len(object_class.attributes) == 0


def test_fromdict__simple(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"isSomething": example_boolean_attribute_dict})
    assert len(object_class.attributes) == 1
    assert "isSomething" in object_class.attributes


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


def test_attribute_fromdict__empty():
    with pytest.raises(ValueError):
        _ObjectClass._attribute_fromdict({})


def test_attribute_fromdict__invalid_attribute_type():
    with pytest.raises(ValueError):
        _ObjectClass._attribute_fromdict(
            {"attribute_type": "some-invalid-attribute-type", "scope": "annotation"}
        )


def test_check__correct(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = build_bbox_with_attributes({"test_attribute": True})
    identifiers = build_identifiers(annotation)

    issues = object_class.check(annotation, _SensorType.CAMERA, identifiers)
    assert issues == []


def test_check__all_error_types(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = build_bbox_with_attributes(
        {"test_attribute_1": "not-a-boolean", "unknown-attribute": False},
    )
    identifiers = build_identifiers(annotation)

    issues = object_class.check(annotation, _SensorType.CAMERA, identifiers)
    assert len(issues) == 3
    issue_types_found = [issue.type for issue in issues]
    assert IssueType.ATTRIBUTE_UNDEFINED in issue_types_found
    assert IssueType.ATTRIBUTE_MISSING in issue_types_found
    assert IssueType.ATTRIBUTE_TYPE in issue_types_found


def test_check_undefined_attributes__correct(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = build_bbox_with_attributes({"test_attribute": True})
    identifiers = build_identifiers(annotation)

    issues = object_class._check_undefined_attributes(annotation, _SensorType.CAMERA, identifiers)
    assert issues == []


def test_check_undefined_attributes__two_undefined(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = build_bbox_with_attributes(
        {"test_attribute": True, "color": "yellow", "is_a_banana": False}
    )
    identifiers = build_identifiers(annotation)

    issues = object_class._check_undefined_attributes(annotation, _SensorType.CAMERA, identifiers)
    assert len(issues) == 2
    for issue in issues:
        assert issue.type == IssueType.ATTRIBUTE_UNDEFINED


def test_check_missing_attributes__correct(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = build_bbox_with_attributes({"test_attribute_1": True, "test_attribute_2": True})
    identifiers = build_identifiers(annotation)

    issues = object_class._check_missing_attributes(annotation, _SensorType.CAMERA, identifiers)
    assert issues == []


def test_check_missing_attributes__one_missing(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict(
        {
            "test_attribute_1": example_boolean_attribute_dict,
            "test_attribute_2": example_boolean_attribute_dict,
        }
    )
    annotation = build_bbox_with_attributes({"test_attribute_2": True})
    identifiers = build_identifiers(annotation)

    issues = object_class._check_missing_attributes(annotation, _SensorType.CAMERA, identifiers)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_MISSING


def test_check_false_attribute_type__correct(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = build_bbox_with_attributes({"test_attribute": True})
    identifiers = build_identifiers(annotation)

    issues = object_class._check_false_attribute_type(annotation, _SensorType.CAMERA, identifiers)
    assert issues == []


def test_check_false_attribute_type__incorrect(example_boolean_attribute_dict):
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    annotation = build_bbox_with_attributes({"test_attribute": "i-like-trains"})
    identifiers = build_identifiers(annotation)

    issues = object_class._check_false_attribute_type(annotation, _SensorType.CAMERA, identifiers)
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


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
