# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

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

    # Filter scene for track annotations in camera sensors
    filtered_scene = raillabel.filter(scene, include_object_types=["track"], include_sensors=cameras)

    # Check per frame
    for frame_uid, frame in filtered_scene.frames.items():
        # Count rails per track
        counts_per_track = _count_rails_per_track_in_frame(frame)

        # Add errors if there is more than one left or right rail
        for object_uid, (left_count, right_count) in counts_per_track.items():
            if left_count > 1:
                errors.append(
                    f"In frame {frame_uid}, the track with object_uid {object_uid} "
                    f"has more than one ({left_count}) left rail."
                )
            if right_count > 1:
                errors.append(
                    f"In frame {frame_uid}, the track with object_uid {object_uid} "
                    f"has more than one ({right_count}) right rail."
                )

    return errors


def _count_rails_per_track_in_frame(frame: raillabel.format.Frame) -> dict[str, tuple[int, int]]:
    # For each track, the left and right rail counts are stored as a tuple (left, right)
    counts: dict[str, tuple[int, int]] = {}

    # For each track, count the left and right rails
    for object_uid, _annotations in frame.object_data.items():
        # Ensure we work only on Poly2d annotations
        poly2ds: list[raillabel.format.Poly2d] = [
            annotation
            for annotation in _annotations.values()
            if isinstance(annotation, raillabel.format.Poly2d)
        ]

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
