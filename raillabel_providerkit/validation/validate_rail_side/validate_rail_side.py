# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import numpy as np
import raillabel

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
    cameras = filter_sensor_uids_by_type(
        list(scene.sensors.values()), raillabel.format.SensorType.CAMERA
    )

    # Check per camera
    for camera in cameras:
        # Filter scene for track annotations in the selected camera sensor
        filtered_scene = raillabel.filter(
            scene, include_object_types=["track"], include_sensors=[camera]
        )

        # Check per frame
        for frame_uid, frame in filtered_scene.frames.items():
            # Count rails per track
            counts_per_track = _count_rails_per_track_in_frame(frame)

            # Find rail x limits per track
            track_limits_per_track = _get_track_limits_in_frame(frame)

            # Add errors if there is more than one left or right rail
            for object_uid, (left_count, right_count) in counts_per_track.items():
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

                # If left and right rails exist, check if the track has its rails swapped
                if left_count >= 1 and right_count >= 1:
                    # Add errors if any track has its rails swapped
                    (max_x_of_left, min_x_of_right) = track_limits_per_track[object_uid]
                    if max_x_of_left > min_x_of_right:
                        errors.append(
                            f"In sensor {camera} frame {frame_uid}, the track with"
                            f" object_uid {object_uid} has its rails swapped."
                            f" The right-most left rail has x={max_x_of_left} while"
                            f" the left-most right rail has x={min_x_of_right}."
                        )

    return errors


def _count_rails_per_track_in_frame(frame: raillabel.format.Frame) -> dict[str, tuple[int, int]]:
    # For each track, the left and right rail counts are stored as a tuple (left, right)
    counts: dict[str, tuple[int, int]] = {}

    # For each track, count the left and right rails
    for object_uid, unfiltered_annotations in frame.object_data.items():
        # Ensure we work only on Poly2d annotations
        poly2ds: list[raillabel.format.Poly2d] = _filter_for_poly2ds(
            list(unfiltered_annotations.values())
        )

        # Count left and right rails
        left_count: int = 0
        right_count: int = 0
        for poly2d in poly2ds:
            match poly2d.attributes["railSide"]:
                case "leftRail":
                    left_count += 1
                case "rightRail":
                    right_count += 1
                case _:
                    # NOTE: This is ignored because it is covered by validate_onthology
                    continue

        # Store counts of current track
        counts[object_uid] = (left_count, right_count)

    # Return results
    return counts


def _get_track_limits_in_frame(frame: raillabel.format.Frame) -> dict[str, tuple[float, float]]:
    # For each track, the largest x of any left rail and the smallest x of any right rail is stored
    # as a tuple (max_x_of_left, min_x_of_right)
    track_limits: dict[str, tuple[float, float]] = {}

    for object_uid, unfiltered_annotations in frame.object_data.items():
        # Ensure we work only on Poly2d annotations
        poly2ds: list[raillabel.format.Poly2d] = _filter_for_poly2ds(
            list(unfiltered_annotations.values())
        )

        # Get the largest x of any left rail and the smallest x of any right rail
        max_x_of_left: float = float("-inf")
        min_x_of_right: float = float("inf")
        for poly2d in poly2ds:
            rail_x_values: list[float] = [point.x for point in poly2d.points]
            match poly2d.attributes["railSide"]:
                case "leftRail":
                    max_x_of_rail_points: float = np.max(rail_x_values)
                    max_x_of_left = max(max_x_of_rail_points, max_x_of_left)
                case "rightRail":
                    min_x_of_rail_points: float = np.min(rail_x_values)
                    min_x_of_right = min(min_x_of_rail_points, min_x_of_right)
                case _:
                    # NOTE: This is ignored because it is covered by validate_onthology
                    continue

        # Store the calculated limits of current track
        track_limits[object_uid] = (max_x_of_left, min_x_of_right)

    return track_limits


def _filter_for_poly2ds(
    unfiltered_annotations: list[type[raillabel.format._ObjectAnnotation]],
) -> list[raillabel.format.Poly2d]:
    return [
        annotation
        for annotation in unfiltered_annotations
        if isinstance(annotation, raillabel.format.Poly2d)
    ]
