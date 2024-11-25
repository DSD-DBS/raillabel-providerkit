# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from uuid import UUID

import numpy as np
import raillabel
from raillabel.filter import (
    IncludeAnnotationTypeFilter,
    IncludeObjectTypeFilter,
    IncludeSensorIdFilter,
    IncludeSensorTypeFilter,
)


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

    camera_uids = list(scene.filter([IncludeSensorTypeFilter(["camera"])]).sensors.keys())

    for camera_uid in camera_uids:
        filtered_scene = scene.filter(
            [
                IncludeObjectTypeFilter(["track"]),
                IncludeSensorIdFilter([camera_uid]),
                IncludeAnnotationTypeFilter(["poly2d"]),
            ]
        )

        for frame_uid, frame in filtered_scene.frames.items():
            counts_per_track = _count_rails_per_track_in_frame(frame)

            for object_uid, (left_count, right_count) in counts_per_track.items():
                context = {
                    "frame_uid": frame_uid,
                    "object_uid": object_uid,
                    "camera_uid": camera_uid,
                }

                count_errors = _check_rail_counts(context, left_count, right_count)
                exactly_one_left_and_right_rail_exist = count_errors != []
                if exactly_one_left_and_right_rail_exist:
                    errors.extend(count_errors)
                    continue

                left_rail = _get_track_from_frame(frame, object_uid, "leftRail")
                right_rail = _get_track_from_frame(frame, object_uid, "rightRail")
                if left_rail is None or right_rail is None:
                    continue

                errors.extend(
                    _check_rails_for_swap_or_intersection(left_rail, right_rail, frame_uid)
                )

    return errors


def _check_rail_counts(context: dict, left_count: int, right_count: int) -> list[str]:
    errors = []
    if left_count > 1:
        errors.append(
            f"In sensor {context['camera_uid']} frame {context['frame_uid']}, the track with"
            f" object_uid {context['object_uid']} has more than one ({left_count}) left rail."
        )
    if right_count > 1:
        errors.append(
            f"In sensor {context['camera_uid']} frame {context['frame_uid']}, the track with"
            f" object_uid {context['object_uid']} has more than one ({right_count}) right rail."
        )
    return errors


def _check_rails_for_swap_or_intersection(
    left_rail: raillabel.format.Poly2d,
    right_rail: raillabel.format.Poly2d,
    frame_uid: str | int = "unknown",
) -> list[str]:
    if left_rail.object_id != right_rail.object_id:
        return []

    max_common_y = _find_max_common_y(left_rail, right_rail)
    if max_common_y is None:
        return []

    left_x = _find_x_by_y(max_common_y, left_rail)
    right_x = _find_x_by_y(max_common_y, right_rail)
    if left_x is None or right_x is None:
        return []

    object_uid = left_rail.object_id
    sensor_uid = left_rail.sensor_id if left_rail.sensor_id is not None else "unknown"

    if left_x >= right_x:
        return [
            f"In sensor {sensor_uid} frame {frame_uid}, the track with"
            f" object_uid {object_uid} has its rails swapped."
            f" At the maximum common y={max_common_y}, the left rail has x={left_x}"
            f" while the right rail has x={right_x}."
        ]

    intersect_interval = _find_intersect_interval(left_rail, right_rail)
    if intersect_interval is not None:
        return [
            f"In sensor {sensor_uid} frame {frame_uid}, the track with"
            f" object_uid {object_uid} intersects with itself."
            f" The left and right rail intersect in y interval {intersect_interval}."
        ]

    return []


def _count_rails_per_track_in_frame(frame: raillabel.format.Frame) -> dict[UUID, tuple[int, int]]:
    """For each track, count the left and right rails."""
    counts: dict[UUID, list[int]] = {}

    unfiltered_annotations = list(frame.annotations.values())
    poly2ds: list[raillabel.format.Poly2d] = _filter_for_poly2ds(unfiltered_annotations)

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

    return {
        object_id: (object_counts[0], object_counts[1])
        for object_id, object_counts in counts.items()
    }


def _filter_for_poly2ds(
    unfiltered_annotations: list,
) -> list[raillabel.format.Poly2d]:
    return [
        annotation
        for annotation in unfiltered_annotations
        if isinstance(annotation, raillabel.format.Poly2d)
    ]


def _find_intersect_interval(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> tuple[float, float] | None:
    """If the two polylines intersect anywhere, return the y interval where they intersect."""
    y_values_with_points_in_either_polyline: list[float] = sorted(
        _get_y_of_all_points_of_poly2d(line1).union(_get_y_of_all_points_of_poly2d(line2))
    )

    order: bool | None = None
    last_y: float | None = None
    for y in y_values_with_points_in_either_polyline:
        x1 = _find_x_by_y(y, line1)
        x2 = _find_x_by_y(y, line2)

        if x1 is None or x2 is None:
            order = None
            continue

        if x1 == x2:
            return (y, y)

        new_order = x1 < x2

        order_has_flipped = order is not None and new_order != order and last_y is not None
        if order_has_flipped:
            return (last_y, y)  # type: ignore  # noqa: PGH003

        order = new_order
        last_y = y

    return None


def _find_max_y(poly2d: raillabel.format.Poly2d) -> float:
    return np.max([point.y for point in poly2d.points])


def _find_max_common_y(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> float | None:
    one_line_is_empty = len(line1.points) == 0 or len(line2.points) == 0
    if one_line_is_empty:
        return None

    max_y_of_line1: float = _find_max_y(line1)
    highest_y_is_bottom_of_line1 = _y_in_poly2d(max_y_of_line1, line2)
    if highest_y_is_bottom_of_line1:
        return max_y_of_line1

    max_y_of_line2: float = _find_max_y(line2)
    highest_y_is_bottom_of_line2 = _y_in_poly2d(max_y_of_line2, line1)
    if highest_y_is_bottom_of_line2:
        return max_y_of_line2

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
    frame: raillabel.format.Frame, object_uid: UUID, rail_side: str
) -> raillabel.format.Poly2d | None:
    for annotation in frame.annotations.values():
        if not isinstance(annotation, raillabel.format.Poly2d):
            continue

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
