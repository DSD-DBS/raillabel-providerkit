# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import raillabel

from . import validate_onthology


def validate(scene: raillabel.Scene, onthology: dict | Path) -> list[str]:
    """Validate a scene based on the Deutsche Bahn Requirements.

    Parameters
    ----------
    scene : raillabel.Scene
        The scene containing the annotations.
    onthology : dict or Path
        Onthology YAML-data or file containing a information about all classes and their
        attributes. The onthology must adhere to the onthology_schema. If a path is provided, the
        file is loaded as a YAML.

    Returns
    -------
    list[str]
        list of all requirement errors in the scene. If an empty list is returned, then there are
        no errors present and the scene is valid.

    """
    errors = []

    errors += validate_onthology(scene, onthology)

    return errors
