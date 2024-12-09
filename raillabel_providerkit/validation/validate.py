# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from raillabel import Scene
from raillabel.json_format import JSONScene

from raillabel_providerkit.validation import Issue

from . import validate_empty_frames, validate_rail_side, validate_schema


def validate(
    scene_dict: dict,
    validate_for_empty_frames: bool = True,
    validate_for_rail_side_order: bool = True,
) -> list[Issue]:
    """Validate a scene based on the Deutsche Bahn Requirements.

    Args:
        scene_dict: The scene as a dictionary directly from `json.load()` in the raillabel format.
        validate_for_empty_frames (optional): If True, issues are returned if the scene contains
            frames without annotations. Default is True.
        validate_for_rail_side_order: If True, issues are returned if the scene contains track with
            a mismatching rail side order. Default is True.

    Returns:
        List of all requirement errors in the scene. If an empty list is returned, then there are no
        errors present and the scene is valid.
    """
    schema_errors = validate_schema(scene_dict)
    if schema_errors != []:
        return schema_errors

    scene = Scene.from_json(JSONScene(**scene_dict))
    errors = []

    if validate_for_empty_frames:
        errors.extend(validate_empty_frames(scene))

    if validate_for_rail_side_order:
        errors.extend(validate_rail_side(scene))

    return errors
