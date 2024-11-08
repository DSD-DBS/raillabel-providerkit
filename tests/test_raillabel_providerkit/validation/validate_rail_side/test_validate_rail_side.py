# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import raillabel

from raillabel_providerkit.validation.validate_rail_side.validate_rail_side import (
    validate_rail_side,
    _count_rails_per_track_in_frame,
)


@pytest.fixture
def example_camera_1() -> raillabel.format.Sensor:
    return raillabel.format.Sensor(
        uid="rgb_center",
        type=raillabel.format.SensorType.CAMERA,
    )


@pytest.fixture
def example_camera_2() -> raillabel.format.Sensor:
    return raillabel.format.Sensor(
        uid="ir_center",
        type=raillabel.format.SensorType.CAMERA,
    )


@pytest.fixture
def example_track_1() -> raillabel.format.Object:
    return raillabel.format.Object(
        uid="a1082ef9-555b-4b69-a888-7da531d8a2eb", name="track0001", type="track"
    )


@pytest.fixture
def example_track_2() -> raillabel.format.Object:
    return raillabel.format.Object(
        uid="6e92e7af-3bc8-4225-b538-16d19e3f8aa7", name="track0002", type="track"
    )


def test_count_rails_per_track_in_frame__empty(empty_frame):
    frame = empty_frame
    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 0


def test_count_rails_per_track_in_frame__many_rails_for_one_track(
    empty_frame, example_camera_1, example_track_1
):
    frame = empty_frame
    sensor = example_camera_1
    object = example_track_1

    LEFT_COUNT = 32
    RIGHT_COUNT = 42

    for i in range(LEFT_COUNT):
        uid = f"test_left_{i}"
        frame.annotations[uid] = raillabel.format.Poly2d(
            uid=uid,
            object=object,
            sensor=sensor,
            points=[
                raillabel.format.Point2d(0, 0),
                raillabel.format.Point2d(0, 1),
            ],
            closed=False,
            attributes={"railSide": "leftRail"},
        )

    for i in range(RIGHT_COUNT):
        uid = f"test_right_{i}"
        frame.annotations[uid] = raillabel.format.Poly2d(
            uid=uid,
            object=object,
            sensor=sensor,
            points=[
                raillabel.format.Point2d(1, 0),
                raillabel.format.Point2d(1, 1),
            ],
            closed=False,
            attributes={"railSide": "rightRail"},
        )

    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 1
    assert object.uid in results.keys()
    assert results[object.uid] == (LEFT_COUNT, RIGHT_COUNT)


def test_count_rails_per_track_in_frame__many_rails_for_two_tracks(
    empty_frame, example_camera_1, example_track_1, example_track_2
):
    frame = empty_frame
    sensor = example_camera_1
    object1 = example_track_1
    object2 = example_track_2

    LEFT_COUNT = 32
    RIGHT_COUNT = 42

    for object in [object1, object2]:
        for i in range(LEFT_COUNT):
            uid = f"test_left_{i}_object_{object.uid}"
            frame.annotations[uid] = raillabel.format.Poly2d(
                uid=uid,
                object=object,
                sensor=sensor,
                points=[
                    raillabel.format.Point2d(0, 0),
                    raillabel.format.Point2d(0, 1),
                ],
                closed=False,
                attributes={"railSide": "leftRail"},
            )

        for i in range(RIGHT_COUNT):
            uid = f"test_right_{i}_object_{object.uid}"
            frame.annotations[uid] = raillabel.format.Poly2d(
                uid=uid,
                object=object,
                sensor=sensor,
                points=[
                    raillabel.format.Point2d(1, 0),
                    raillabel.format.Point2d(1, 1),
                ],
                closed=False,
                attributes={"railSide": "rightRail"},
            )

    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 2
    assert object1.uid in results.keys()
    assert object2.uid in results.keys()
    assert results[object1.uid] == (LEFT_COUNT, RIGHT_COUNT)
    assert results[object2.uid] == (LEFT_COUNT, RIGHT_COUNT)


def test_validate_rail_side__no_errors(empty_scene, empty_frame, example_camera_1, example_track_1):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor = example_camera_1
    scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "leftRail"},
    )
    frame.annotations["be7d136a-8364-4fbd-b098-6f4a21205d22"] = raillabel.format.Poly2d(
        uid="be7d136a-8364-4fbd-b098-6f4a21205d22",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 0


def test_validate_rail_side__rail_sides_switched(
    empty_scene, empty_frame, example_camera_1, example_track_1
):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor = example_camera_1
    scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["be7d136a-8364-4fbd-b098-6f4a21205d22"] = raillabel.format.Poly2d(
        uid="be7d136a-8364-4fbd-b098-6f4a21205d22",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "leftRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__two_left_rails(
    empty_scene, empty_frame, example_camera_1, example_track_1
):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor = example_camera_1
    scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "leftRail"},
    )
    frame.annotations["be7d136a-8364-4fbd-b098-6f4a21205d22"] = raillabel.format.Poly2d(
        uid="be7d136a-8364-4fbd-b098-6f4a21205d22",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "leftRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__two_right_rails(
    empty_scene, empty_frame, example_camera_1, example_track_1
):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor = example_camera_1
    scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["be7d136a-8364-4fbd-b098-6f4a21205d22"] = raillabel.format.Poly2d(
        uid="be7d136a-8364-4fbd-b098-6f4a21205d22",
        object=object,
        sensor=sensor,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 1


def test_validate_rail_side__two_sensors_with_two_right_rails_each(
    empty_scene, empty_frame, example_camera_1, example_camera_2, example_track_1
):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor1 = example_camera_1
    sensor2 = example_camera_2
    for sensor in [sensor1, sensor2]:
        scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor1,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["be7d136a-8364-4fbd-b098-6f4a21205d22"] = raillabel.format.Poly2d(
        uid="be7d136a-8364-4fbd-b098-6f4a21205d22",
        object=object,
        sensor=sensor1,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["f6db5b28-bdcd-437f-bf39-c044bb516de8"] = raillabel.format.Poly2d(
        uid="f6db5b28-bdcd-437f-bf39-c044bb516de8",
        object=object,
        sensor=sensor2,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["89f8cf2c-1dc9-4956-9661-f1054ff069f9"] = raillabel.format.Poly2d(
        uid="89f8cf2c-1dc9-4956-9661-f1054ff069f9",
        object=object,
        sensor=sensor2,
        points=[
            raillabel.format.Point2d(1, 0),
            raillabel.format.Point2d(1, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 2


def test_validate_rail_side__two_sensors_with_one_right_rail_each(
    empty_scene, empty_frame, example_camera_1, example_camera_2, example_track_1
):
    scene = empty_scene
    object = example_track_1
    scene.objects[object.uid] = object
    sensor1 = example_camera_1
    sensor2 = example_camera_2
    for sensor in [sensor1, sensor2]:
        scene.sensors[sensor.uid] = sensor
    frame = empty_frame
    frame.annotations["325b1f55-a2ef-475f-a780-13e1a9e823c3"] = raillabel.format.Poly2d(
        uid="325b1f55-a2ef-475f-a780-13e1a9e823c3",
        object=object,
        sensor=sensor1,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    frame.annotations["f6db5b28-bdcd-437f-bf39-c044bb516de8"] = raillabel.format.Poly2d(
        uid="f6db5b28-bdcd-437f-bf39-c044bb516de8",
        object=object,
        sensor=sensor2,
        points=[
            raillabel.format.Point2d(0, 0),
            raillabel.format.Point2d(0, 1),
        ],
        closed=False,
        attributes={"railSide": "rightRail"},
    )
    scene.frames[frame.uid] = frame

    actual = validate_rail_side(scene)
    assert len(actual) == 0


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
