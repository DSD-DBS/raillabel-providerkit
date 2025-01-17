# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

from raillabel import Scene
from raillabel.json_format import JSONScene

from raillabel_providerkit.validation import Issue

from . import (
    validate_empty_frames,
    validate_missing_ego_track,
    validate_onthology,
    validate_rail_side,
    validate_schema,
)


def validate(
    scene_source: dict | Path,
    onthology_source: dict | Path | None = None,
    validate_for_empty_frames: bool = True,
    validate_for_rail_side_order: bool = True,
    validate_for_missing_ego_track: bool = True,
) -> list[Issue]:
    """Validate a scene based on the Deutsche Bahn Requirements.

    Args:
        scene_source: The scene either as a dictionary or as a Path to the scene source file.
        onthology_source: The dataset onthology as a dictionary or as a Path to the onthology YAML
            file. If not None, issues are returned if the scene contains annotations with invalid
            attributes or object types. Default is None.
        validate_for_empty_frames (optional): If True, issues are returned if the scene contains
            frames without annotations. Default is True.
        validate_for_rail_side_order: If True, issues are returned if the scene contains track with
            a mismatching rail side order. Default is True.
        validate_for_missing_ego_track: If True, issues are returned if the scene contains frames
            where the ego track (the track the recording train is driving on) is missing. Default is
            True.

    Returns:
        List of all requirement errors in the scene. If an empty list is returned, then there are no
        errors present and the scene is valid.
    """
    if isinstance(scene_source, Path):
        with scene_source.open() as scene_file:
            scene_source = json.load(scene_file)

    schema_errors = validate_schema(scene_source)
    if schema_errors != []:
        return schema_errors

    scene = Scene.from_json(JSONScene(**scene_source))
    errors = []

    if onthology_source is not None:
        errors.extend(validate_onthology(scene, onthology_source))

    if validate_for_empty_frames:
        errors.extend(validate_empty_frames(scene))

    if validate_for_rail_side_order:
        errors.extend(validate_rail_side(scene))

    if validate_for_missing_ego_track:
        errors.extend(validate_missing_ego_track(scene))

    return errors
