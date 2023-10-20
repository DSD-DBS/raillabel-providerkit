# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import typing as t
from pathlib import Path
from uuid import uuid4

import pytest
import raillabel

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from raillabel_providerkit import validate

# == Tests ============================

def test_no_errors(demo_onthology, valid_onthology_scene):
    assert validate(valid_onthology_scene, demo_onthology) == []

def test_onthology_errors(demo_onthology, invalid_onthology_scene):
    assert len(validate(invalid_onthology_scene, demo_onthology)) == 1


if __name__ == "__main__":
    os.system("clear")
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
