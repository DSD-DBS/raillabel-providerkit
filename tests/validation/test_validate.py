# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import json
import pytest

from raillabel.scene_builder import SceneBuilder
from raillabel.format import Point2d

from raillabel_providerkit import validate


def write_to_json(content: dict, path: Path):
    with path.open("w") as f:
        json.dump(content, f)


def test_no_issues_in_empty_scene_dict():
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    actual = validate(scene_dict)
    assert len(actual) == 0


def test_no_issues_in_empty_scene_path(tmp_path):
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    scene_path = tmp_path / "empty_scene.json"
    write_to_json(scene_dict, scene_path)

    actual = validate(scene_path)
    assert len(actual) == 0


def test_schema_issues():
    scene_dict = {"openlabel": {}}
    actual = validate(scene_dict)
    assert len(actual) == 1


def test_empty_frame_issues():
    scene_dict = json.loads(SceneBuilder.empty().add_frame().result.to_json().model_dump_json())

    actual = validate(scene_dict)
    assert len(actual) == 1


def test_rail_side_issues():
    scene = (
        SceneBuilder.empty()
        .add_poly2d(
            points=[
                Point2d(0, 0),
                Point2d(0, 1),
            ],
            attributes={"railSide": "rightRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_poly2d(
            points=[
                Point2d(1, 0),
                Point2d(1, 1),
            ],
            attributes={"railSide": "leftRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )
    scene_dict = json.loads(scene.to_json().model_dump_json())

    actual = validate(scene_dict, validate_for_missing_ego_track=False)
    assert len(actual) == 1


def test_missing_ego_track_issue():
    scene_dict = json.loads(
        SceneBuilder.empty()
        .add_sensor("rgb_middle")
        .add_frame()
        .add_bbox()
        .result.to_json()
        .model_dump_json()
    )

    actual = validate(scene_dict)
    assert len(actual) == 1


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
