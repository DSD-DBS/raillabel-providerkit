# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import pytest

from raillabel.scene_builder import SceneBuilder
from raillabel.format import Poly2d, Point2d

from raillabel_providerkit import validate


def test_no_issues_in_empty_scene():
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    actual = validate(scene_dict)
    assert len(actual) == 0


def test_schema_issues():
    scene_dict = {"openlabel": {}}
    actual = validate(scene_dict)
    assert len(actual) == 1


def test_empty_frame_issues():
    scene_dict = json.loads(SceneBuilder.empty().add_frame().result.to_json().model_dump_json())

    actual = validate(scene_dict)
    assert len(actual) == 1


def test_rail_side_issues(ignore_uuid):
    SENSOR_ID = "rgb_center"
    scene = (
        SceneBuilder.empty()
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(0, 0),
                    Point2d(0, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id=SENSOR_ID,
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id=SENSOR_ID,
        )
        .result
    )
    scene_dict = json.loads(scene.to_json().model_dump_json())

    actual = validate(scene_dict)
    assert len(actual) == 1


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
