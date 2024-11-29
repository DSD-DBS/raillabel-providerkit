# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from . import validate_schema


def validate(scene_dict: dict) -> list[str]:
    """Validate a scene based on the Deutsche Bahn Requirements.

    Parameters
    ----------
    scene_dict : dict
        The scene as a dictionary directly from `json.load()` in the raillabel format.

    Returns
    -------
    list[str]
        list of all requirement errors in the scene. If an empty list is returned, then there are
        no errors present and the scene is valid.

    """
    errors = []

    errors.extend(validate_schema(scene_dict))

    return errors
