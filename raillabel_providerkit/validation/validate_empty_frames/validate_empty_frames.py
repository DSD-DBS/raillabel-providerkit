# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import raillabel


def validate_empty_frames(scene: raillabel.Scene) -> list[str]:
    """Validate whether all frames of a scene have at least one annotation.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene, that should be validated.

    Returns
    -------
    list[str]
        list of all empty frame errors in the scene. If an empty list is returned, then there are no
        errors present.

    """
    errors: list[str] = []

    for frame_uid, frame in scene.frames.items():
        if _is_frame_empty(frame):
            errors.append("Frame " + str(frame_uid) + " has no annotations!")

    return errors


def _is_frame_empty(frame: raillabel.format.Frame) -> bool:
    return len(frame.annotations) == 0
