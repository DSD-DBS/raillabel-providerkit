# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from typing import List

import raillabel


def validate_rail_side(scene: raillabel.Scene) -> List[str]:
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
