# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import raillabel


def validate_rail_side(scene: raillabel.Scene) -> list[str]:
    """TODO.

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
