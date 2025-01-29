# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import UUID

import pytest

from raillabel_providerkit.validation.validate_onthology._onthology_classes._onthology import (
    _Onthology,
    Issue,
    IssueType,
    IssueIdentifiers,
)
from raillabel_providerkit.validation import IssueType
from raillabel.format import Point2d, Size2d
from raillabel.scene_builder import SceneBuilder


def test_fromdict__empty():
    ontology = _Ontology.fromdict({})
    assert len(ontology.classes) == 0
    assert len(ontology.errors) == 0


def test_fromdict__simple():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    assert len(ontology.classes) == 1
    assert "banana" in ontology.classes
    assert len(ontology.errors) == 0


def test_check__empty_scene():
    ontology = _Ontology.fromdict({})
    scene = SceneBuilder.empty().result

    issues = onthology.check(scene)
    assert issues == []


def test_check__correct():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="banana_0001")
        .add_bbox(
            object_name="banana_0001",
            attributes={"is_peelable": True},
        )
        .result
    )

    issues = onthology.check(scene)
    assert issues == []


def test_check__undefined_object_type():
    ontology = _Ontology.fromdict(
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
            object_name="banana_0001",
            attributes={"is_peelable": True},
        )
        .result
    )

    issues = onthology.check(scene)
    assert issues == [
        Issue(
            IssueType.OBJECT_TYPE_UNDEFINED,
            IssueIdentifiers(
                object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_type="apple"
            ),
        )
    ]


def test_check__invalid_attribute_type():
    ontology = _Ontology.fromdict(
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
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_middle",
            attributes={"is_peelable": "i-like-trains"},
        )
        .result
    )
    issues = ontology.check(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE
    assert issues[0].identifiers == IssueIdentifiers(
        annotation=UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
        attribute="is_peelable",
        frame=0,
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
        object_type="banana",
        sensor="rgb_middle",
    )


def test_check_class_validity__empty_scene():
    ontology = _Ontology.fromdict({})
    scene = SceneBuilder.empty().result
    onthology._check_class_validity(scene)
    assert onthology.errors == []


def test_check_class_validity__correct():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = SceneBuilder.empty().add_object(object_type="banana").result
    onthology._check_class_validity(scene)
    assert onthology.errors == []


def test_check_class_validity__incorrect():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_name="apple_0000")
        .add_bbox(
            object_name="apple_0000",
        )
        .result
    )
    onthology._check_class_validity(scene)
    assert len(onthology.errors) == 1
    assert onthology.errors[0].type == IssueType.OBJECT_TYPE_UNDEFINED
    assert onthology.errors[0].identifiers == IssueIdentifiers(
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_type="apple"
    )


def test_compile_annotations__empty_scene():
    scene = SceneBuilder.empty().result
    annotations = _Ontology._compile_annotations(scene)
    assert len(annotations) == 0


def test_compile_annotations__three_annotations_in_two_frames():
    scene = (
        SceneBuilder.empty()
        .add_bbox(
            frame_id=0,
            object_name="box_0001",
        )
        .add_bbox(
            frame_id=0,
            object_name="box_0002",
        )
        .add_bbox(
            frame_id=1,
            object_name="box_0003",
        )
        .result
    )
    annotations = _Ontology._compile_annotations(scene)
    assert len(annotations) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
