# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import pytest

from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit import validate


def test_no_errors_in_empty_scene():
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    actual = validate(scene_dict)
    assert len(actual) == 0


def test_schema_errors():
    scene_dict = {"openlabel": {}}
    actual = validate(scene_dict)
    assert len(actual) == 1


def test_empty_frame_errors():
    scene_dict = json.loads(SceneBuilder.empty().add_frame().result.to_json().model_dump_json())

    actual = validate(scene_dict)
    assert len(actual) == 1



if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
