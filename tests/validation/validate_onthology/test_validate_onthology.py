# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from uuid import UUID

from raillabel_providerkit.validation.validate_onthology.validate_onthology import (
    validate_onthology,
    _validate_onthology_schema,
    _load_onthology,
    OnthologySchemaError,
)
from raillabel_providerkit.validation import IssueType
from raillabel.scene_builder import SceneBuilder
from raillabel.format import Point2d, Size2d

ONTHOLOGY_PATH = Path(__file__).parent.parent.parent / "__assets__/osdar23_onthology.yaml"


@pytest.fixture
def example_onthology_dict() -> dict:
    return {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}


def test_validate_onthology__empty_scene(example_onthology_dict):
    scene = SceneBuilder.empty().result
    issues = validate_onthology(scene, example_onthology_dict)
    assert issues == []


def test_validate_onthology__correct(example_onthology_dict):
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
    issues = validate_onthology(scene, example_onthology_dict)
    assert issues == []


def test_validate_onthology__invalid_attribute_type(example_onthology_dict):
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
    issues = validate_onthology(scene, example_onthology_dict)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE


def test_load_onthology__invalid_path():
    invalid_path = Path("/this/should/point/nowhere")
    with pytest.raises(FileNotFoundError):
        _load_onthology(invalid_path)


def test_load_onthology__osdar23():
    onthology_dict = _load_onthology(ONTHOLOGY_PATH)
    assert isinstance(onthology_dict, dict)


def test_validate_onthology_schema__none():
    with pytest.raises(OnthologySchemaError):
        _validate_onthology_schema(None)


def test_validate_onthology_schema__empty():
    _validate_onthology_schema({})


def test_validate_onthology_schema__invalid():
    invalid_dict = {"foo": "bar"}
    with pytest.raises(OnthologySchemaError):
        _validate_onthology_schema(invalid_dict)


def test_validate_onthology_schema__valid(example_onthology_dict):
    _validate_onthology_schema(example_onthology_dict)


def test_unexpected_class(example_onthology_dict):
    scene = SceneBuilder.empty().add_bbox(object_name="apple_0001").result

    validate_onthology(scene, example_onthology_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
