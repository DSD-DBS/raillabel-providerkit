# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from raillabel.format import Poly2d, Point2d
from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.validation.validate_rail_side.validate_rail_side import (
    validate_rail_side,
    _count_rails_per_track_in_frame,
)


def test_count_rails_per_track_in_frame__empty(empty_frame):
    frame = empty_frame
    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 0


def test_count_rails_per_track_in_frame__many_rails_for_one_track(ignore_uuid):
    LEFT_COUNT = 32
    RIGHT_COUNT = 42
    TRACK_NAME = "track_0001"

    builder = SceneBuilder.empty()

    for _ in range(LEFT_COUNT):
        builder = builder.add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(0, 0),
                    Point2d(0, 1),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name=TRACK_NAME,
            sensor_id="rgb_center",
        )

    for _ in range(RIGHT_COUNT):
        builder = builder.add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name=TRACK_NAME,
            sensor_id="rgb_center",
        )

    scene = builder.result
    frame = scene.frames[list(scene.frames.keys())[0]]
    object_id = frame.annotations[list(frame.annotations.keys())[0]].object_id

    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 1
    assert object_id in results.keys()
    assert results[object_id] == (LEFT_COUNT, RIGHT_COUNT)


def test_count_rails_per_track_in_frame__many_rails_for_two_tracks(ignore_uuid):
    LEFT_COUNT = 32
    RIGHT_COUNT = 42

    builder = SceneBuilder.empty()

    for track_name in ["track_0001", "track_0002"]:
        for _ in range(LEFT_COUNT):
            builder = builder.add_annotation(
                annotation=Poly2d(
                    points=[
                        Point2d(0, 0),
                        Point2d(0, 1),
                    ],
                    closed=False,
                    attributes={"railSide": "leftRail"},
                    object_id=ignore_uuid,
                    sensor_id="IGNORE_THIS",
                ),
                object_name=track_name,
                sensor_id="rgb_center",
            )

        for _ in range(RIGHT_COUNT):
            builder = builder.add_annotation(
                annotation=Poly2d(
                    points=[
                        Point2d(1, 0),
                        Point2d(1, 1),
                    ],
                    closed=False,
                    attributes={"railSide": "rightRail"},
                    object_id=ignore_uuid,
                    sensor_id="IGNORE_THIS",
                ),
                object_name=track_name,
                sensor_id="rgb_center",
            )

    scene = builder.result
    frame = scene.frames[list(scene.frames.keys())[0]]

    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 2

    for object_id in scene.objects.keys():
        assert object_id in results.keys()
        assert results[object_id] == (LEFT_COUNT, RIGHT_COUNT)


def test_validate_rail_side__no_errors(ignore_uuid):
    scene = (
        SceneBuilder.empty()
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(0, 0),
                    Point2d(0, 1),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 0


def test_validate_rail_side__rail_sides_switched(ignore_uuid):
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
            sensor_id="rgb_center",
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
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__rail_sides_intersect_at_top(ignore_uuid):
    scene = (
        SceneBuilder.empty()
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(20, 0),
                    Point2d(20, 10),
                    Point2d(10, 20),
                    Point2d(10, 100),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(10, 0),
                    Point2d(10, 10),
                    Point2d(20, 20),
                    Point2d(20, 100),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__rail_sides_correct_with_early_end_of_one_side(ignore_uuid):
    scene = (
        SceneBuilder.empty()
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(70, 0),
                    Point2d(30, 20),
                    Point2d(15, 40),
                    Point2d(10, 50),
                    Point2d(10, 100),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(20, 50),
                    Point2d(20, 100),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 0


def test_validate_rail_side__two_left_rails(ignore_uuid):
    scene = (
        SceneBuilder.empty()
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(0, 0),
                    Point2d(0, 1),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
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
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__two_right_rails(ignore_uuid):
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
            sensor_id="rgb_center",
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__two_sensors_with_two_right_rails_each(ignore_uuid):
    SENSOR1_ID = "rgb_center"
    SENSOR2_ID = "ir_center"
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
            sensor_id=SENSOR1_ID,
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id=SENSOR1_ID,
        )
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
            sensor_id=SENSOR2_ID,
        )
        .add_annotation(
            annotation=Poly2d(
                points=[
                    Point2d(1, 0),
                    Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
                object_id=ignore_uuid,
                sensor_id="IGNORE_THIS",
            ),
            object_name="track_0001",
            sensor_id=SENSOR2_ID,
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 2


def test_validate_rail_side__two_sensors_with_one_right_rail_each(ignore_uuid):
    SENSOR1_ID = "rgb_center"
    SENSOR2_ID = "ir_center"
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
            sensor_id=SENSOR1_ID,
        )
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
            sensor_id=SENSOR2_ID,
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 0


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
