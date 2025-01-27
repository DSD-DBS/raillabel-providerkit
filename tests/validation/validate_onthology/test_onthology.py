# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import UUID

from raillabel_providerkit.validation.validate_onthology._onthology_classes._onthology import (
    _Onthology,
)
from raillabel_providerkit.validation import IssueType
from raillabel.format import Point2d, Size2d
from raillabel.scene_builder import SceneBuilder


def test_fromdict__empty():
    onthology = _Onthology.fromdict({})
    assert len(onthology.classes) == 0
    assert len(onthology.errors) == 0


def test_fromdict__simple():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    assert len(onthology.classes) == 1
    assert "banana" in onthology.classes
    assert len(onthology.errors) == 0


def test_check__empty_scene():
    onthology = _Onthology.fromdict({})
    scene = SceneBuilder.empty().result
    issues = onthology.check(scene)
    assert len(issues) == 0
    assert issues == onthology.errors


def test_check__correct():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": True},
        )
        .result
    )
    issues = onthology.check(scene)
    assert len(issues) == 0
    assert issues == onthology.errors


def test_check__undefined_object_type():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="apple",
            object_name="apple_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": True},
        )
        .result
    )
    issues = onthology.check(scene)
    assert len(issues) == 1
    assert issues == onthology.errors
    assert issues[0].type == IssueType.OBJECT_TYPE_UNDEFINED


def test_check__invalid_attribute_type():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": "i-like-trains"},
        )
        .result
    )
    issues = onthology.check(scene)
    assert len(issues) == 1
    assert issues == onthology.errors
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE


def test_check_class_validity__empty_scene():
    onthology = _Onthology.fromdict({})
    scene = SceneBuilder.empty().result
    onthology._check_class_validity(scene)
    assert len(onthology.errors) == 0


def test_check_class_validity__correct():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .result
    )
    onthology._check_class_validity(scene)
    assert len(onthology.errors) == 0


def test_check_class_validity__incorrect():
    onthology = _Onthology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = SceneBuilder.empty().add_bbox(object_name="apple_0000").result
    onthology._check_class_validity(scene)
    assert len(onthology.errors) == 1
    assert onthology.errors[0].type == IssueType.OBJECT_TYPE_UNDEFINED


def test_compile_annotations__empty_scene():
    scene = SceneBuilder.empty().result
    annotations = _Onthology._compile_annotations(scene)
    assert len(annotations) == 0


def test_compile_annotations__three_annotations_in_two_frames():
    scene = (
        SceneBuilder.empty()
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="box_0001",
            sensor_id="rgb_center",
            attributes={},
        )
        .add_bbox(
            UUID("157ae432-95b0-4e7d-86c5-414c3308e171"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="box_0002",
            sensor_id="rgb_center",
            attributes={},
        )
        .add_bbox(
            UUID("711cf3f3-fb2b-4f64-a785-c94bbda9b8c5"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=1,
            object_name="box_0003",
            sensor_id="rgb_center",
            attributes={},
        )
        .result
    )
    annotations = _Onthology._compile_annotations(scene)
    assert len(annotations) == 3
