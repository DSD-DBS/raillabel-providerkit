# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import numpy as np
import raillabel
from raillabel.filter import IncludeObjectTypeFilter, IncludeSensorIdFilter, IncludeAnnotationTypeFilter, IncludeSensorTypeFilter, IncludeAttributesFilter

from raillabel_providerkit._util._filters import filter_sensor_uids_by_type


def validate_rail_side(scene: raillabel.Scene) -> list[str]:
    """Validate whether all tracks have <= one left and right rail, and that they have correct order.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene, that should be validated.

    Returns
    -------
    list[str]
        list of all rail side errors in the scene. If an empty list is returned, then there are no
        errors present.

    """
    errors: list[str] = []

    # Get a list of camera uids
    cameras = list(scene.filter([IncludeSensorTypeFilter("camera")]).sensors.keys())

    # Check per camera
    for camera in cameras:
        # Filter scene for track annotations in the selected camera sensor
        filtered_scene = scene.filter([
            IncludeObjectTypeFilter(["track"]),
            IncludeSensorIdFilter([camera]),
            IncludeAnnotationTypeFilter(["poly2d"]),
        ])

        # Check per frame
        for frame_uid, frame in filtered_scene.frames.items():
            # Count rails per track
            counts_per_track = _count_rails_per_track_in_frame(frame)

            # Add errors if there is more than one left or right rail
            for object_uid, (left_count, right_count) in counts_per_track.items():
                if left_count > 1 or right_count > 1:
                    if left_count > 1:
                        errors.append(
                            f"In sensor {camera} frame {frame_uid}, the track with"
                            f" object_uid {object_uid} has more than one ({left_count}) left rail."
                        )
                    if right_count > 1:
                        errors.append(
                            f"In sensor {camera} frame {frame_uid}, the track with"
                            f" object_uid {object_uid} has more than one ({right_count}) right rail."
                        )
                    continue

                # If exactly one left and right rail exists, check if the track has its rails swapped
                # or intersects with itself
                # Get the two annotations in question
                left_rail: raillabel.format.Poly2d | None = _get_track_from_frame(
                    frame, object_uid, "leftRail"
                )
                right_rail: raillabel.format.Poly2d | None = _get_track_from_frame(
                    frame, object_uid, "rightRail"
                )
                if left_rail is None or right_rail is None:
                    continue

                swap_error: str | None = _check_rails_for_swap(left_rail, right_rail, frame_uid)
                if swap_error is not None:
                    errors.append(swap_error)

    return errors


def _check_rails_for_swap(
    left_rail: raillabel.format.Poly2d,
    right_rail: raillabel.format.Poly2d,
    frame_uid: str | int = "unknown",
) -> str | None:
    # Ensure the rails belong to the same track
    if left_rail.object_id != right_rail.object_id:
        return None

    max_common_y = _find_max_common_y(left_rail, right_rail)
    if max_common_y is None:
        return None

    left_x = _find_x_by_y(max_common_y, left_rail)
    right_x = _find_x_by_y(max_common_y, right_rail)
    if left_x is None or right_x is None:
        return None

    object_uid = left_rail.object_id
    sensor_uid = left_rail.sensor_id if left_rail.sensor_id is not None else "unknown"

    if left_x >= right_x:
        return (
            f"In sensor {sensor_uid} frame {frame_uid}, the track with"
            f" object_uid {object_uid} has its rails swapped."
            f" At the maximum common y={max_common_y}, the left rail has x={left_x}"
            f" while the right rail has x={right_x}."
        )

    intersect_interval = _find_intersect_interval(left_rail, right_rail)
    if intersect_interval is not None:
        return (
            f"In sensor {sensor_uid} frame {frame_uid}, the track with"
            f" object_uid {object_uid} intersects with itself."
            f" The left and right rail intersect in y interval {intersect_interval}."
        )

    return None


def _count_rails_per_track_in_frame(frame: raillabel.format.Frame) -> dict[str, tuple[int, int]]:
    # For each track, the left and right rail counts are stored as a list (left, right)
    counts: dict[str, list[int, int]] = {}

    # For each track, count the left and right rails
    unfiltered_annotations = list(frame.annotations.values())
    # Ensure we work only on Poly2d annotations
    poly2ds: list[raillabel.format.Poly2d] = _filter_for_poly2ds(unfiltered_annotations)

    # Count left and right rails
    for poly2d in poly2ds:
        object_id = poly2d.object_id
        if object_id not in counts:
            counts[object_id] = [0, 0]

        rail_side = poly2d.attributes["railSide"]
        if rail_side == "leftRail":
            counts[object_id][0] += 1
        elif rail_side == "rightRail":
            counts[object_id][1] += 1
        else:
            # NOTE: This is ignored because it is covered by validate_onthology
            continue

    # Return results
    return {key: tuple(value) for key, value in counts.items()}


def _filter_for_poly2ds(
    unfiltered_annotations: list[type[raillabel.format._ObjectAnnotation]],
) -> list[raillabel.format.Poly2d]:
    return [
        annotation
        for annotation in unfiltered_annotations
        if isinstance(annotation, raillabel.format.Poly2d)
    ]


def _find_intersect_interval(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> tuple[float, float] | None:
    # If the two polylines intersect anywhere, return the y interval where they intersect.

    # Get all y values where either polyline has points
    y_values: list[float] = sorted(
        _get_y_of_all_points_of_poly2d(line1).union(_get_y_of_all_points_of_poly2d(line2))
    )

    order: bool | None = None
    last_y: float | None = None
    for y in y_values:
        x1 = _find_x_by_y(y, line1)
        x2 = _find_x_by_y(y, line2)

        if x1 is None or x2 is None:
            order = None
            continue

        if x1 == x2:
            return (y, y)

        new_order = x1 < x2

        if order is not None and new_order != order and last_y is not None:
            # The order has flipped. There is an intersection between previous and current y
            return (last_y, y)

        order = new_order
        last_y = y

    return None


def _find_max_y(poly2d: raillabel.format.Poly2d) -> float:
    return np.max([point.y for point in poly2d.points])


def _find_max_common_y(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> float | None:
    if len(line1.points) == 0 or len(line2.points) == 0:
        # One of the lines is empty
        return None

    max_y_of_line1: float = _find_max_y(line1)
    if _y_in_poly2d(max_y_of_line1, line2):
        # The highest y is the bottom of line 1
        return max_y_of_line1

    max_y_of_line2: float = _find_max_y(line2)
    if _y_in_poly2d(max_y_of_line2, line1):
        # The highest y is the bottom of line 2
        return max_y_of_line2

    # There is no y overlap
    return None


def _find_x_by_y(y: float, poly2d: raillabel.format.Poly2d) -> float | None:
    """Find the x value of the first point where the polyline passes through y.

    Parameters
    ----------
    y : float
        The y value to check.
    poly2d : raillabel.format.Poly2d
       The Poly2D whose points will be checked against.

    Returns
    -------
    float | None
        The x value of a point (x,y) that poly2d passes through,
        or None if poly2d doesn't go through y.

    """
    # 1. Find the first two points between which y is located
    points = poly2d.points
    p1: raillabel.format.Point2d | None = None
    p2: raillabel.format.Point2d | None = None
    for i in range(len(points) - 1):
        current = points[i]
        next_ = points[i + 1]
        if (current.y >= y >= next_.y) or (current.y <= y <= next_.y):
            p1 = current
            p2 = next_
            break

    # 2. Abort if no valid points have been found
    if not (p1 and p2):
        return None

    # 3. Return early if p1=p2 (to avoid division by zero)
    if p1.x == p2.x:
        return p1.x

    # 4. Calculate m and n for the line g(x)=mx+n connecting p1 and p2
    m = (p2.y - p1.y) / (p2.x - p1.x)
    n = p1.y - (m * p1.x)

    # 5. Return early if m is 0, as that means p2.y=p1.y, which implies p2.y=p1.y=y
    if m == 0:
        return p1.x

    # 6. Calculate the x we were searching for and return it
    return (y - n) / m


def _get_track_from_frame(
    frame: raillabel.format.Frame, object_uid: str, rail_side: str
) -> raillabel.format.Poly2d | None:
    for annotation in frame.annotations.values():
        if annotation.object_id != object_uid:
            continue

        if "railSide" not in annotation.attributes:
            continue

        if annotation.attributes["railSide"] == rail_side:
            return annotation

    return None


def _get_y_of_all_points_of_poly2d(poly2d: raillabel.format.Poly2d) -> set[float]:
    y_values: set[float] = set()
    for point in poly2d.points:
        y_values.add(point.y)
    return y_values


def _y_in_poly2d(y: float, poly2d: raillabel.format.Poly2d) -> bool:
    """Check whether the polyline created by the given Poly2d passes through the given y value.

    Parameters
    ----------
    y : float
        The y value to check.
    poly2d : raillabel.format.Poly2d
        The Poly2D whose points will be checked against.

    Returns
    -------
    bool
        Does the Poly2d pass through the given y value?

    """
    # For every point (except the last), check if the y is between them
    for i in range(len(poly2d.points) - 1):
        current = poly2d.points[i]
        next_ = poly2d.points[i + 1]
        if (current.y >= y >= next_.y) or (current.y <= y <= next_.y):
            return True
    return False
