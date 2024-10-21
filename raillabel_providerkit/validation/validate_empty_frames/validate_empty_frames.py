# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from typing import List

import raillabel


def validate_empty_frames(scene: raillabel.Scene) -> List[str]:
    """Validate whether all frames of a scene have at least one annotation.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene, that should be validated.

    Returns
    -------
    list[str]
        list of all onthology errors in the scene. If an empty list is returned, then there are no
        errors present.
    """


def _is_frame_empty(frame: raillabel.format.Frame) -> bool:
    return len(frame.annotations) == 0
