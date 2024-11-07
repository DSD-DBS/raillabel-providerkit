# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import raillabel

from raillabel_providerkit.validation.validate_rail_side.validate_rail_side import (
    validate_rail_side,
)


def test_validate_rail_side__no_errors(empty_scene, empty_frame):
    scene = empty_scene
    object = raillabel.format.Object(
        uid="a1082ef9-555b-4b69-a888-7da531d8a2eb", name="track0001", type="track"
    )
    scene.objects[object.uid] = object
    sensor = raillabel.format.Sensor(
        uid="rgb_center",
        type=raillabel.format.SensorType.CAMERA,
    )
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


def test_validate_rail_side__rail_sides_switched(empty_scene, empty_frame):
    scene = empty_scene
    object = raillabel.format.Object(
        uid="a1082ef9-555b-4b69-a888-7da531d8a2eb", name="track0001", type="track"
    )
    scene.objects[object.uid] = object
    sensor = raillabel.format.Sensor(
        uid="rgb_center",
        type=raillabel.format.SensorType.CAMERA,
    )
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


def test_validate_rail_side__two_left_rails(empty_scene, empty_frame):
    scene = empty_scene
    object = raillabel.format.Object(
        uid="a1082ef9-555b-4b69-a888-7da531d8a2eb", name="track0001", type="track"
    )
    scene.objects[object.uid] = object
    sensor = raillabel.format.Sensor(
        uid="rgb_center",
        type=raillabel.format.SensorType.CAMERA,
    )
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


def test_validate_rail_side__two_right_rails(empty_scene, empty_frame):
    scene = empty_scene
    object = raillabel.format.Object(
        uid="a1082ef9-555b-4b69-a888-7da531d8a2eb", name="track0001", type="track"
    )
    scene.objects[object.uid] = object
    sensor = raillabel.format.Sensor(
        uid="rgb_center",
        type=raillabel.format.SensorType.CAMERA,
    )
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


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
