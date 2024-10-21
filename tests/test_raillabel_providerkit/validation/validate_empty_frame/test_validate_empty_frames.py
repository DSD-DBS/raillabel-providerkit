# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from pathlib import Path

import pytest
import raillabel

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from raillabel_providerkit.validation.validate_empty_frames.validate_empty_frames import (
    _is_frame_empty,
)

# == Tests ============================

def test_is_frame_empty__true():
    frame = raillabel.format.Frame(uid=0, annotations={})
    assert _is_frame_empty(frame)

def test_is_frame_empty__false():
    frame = raillabel.format.Frame(
        uid=0, annotations={
            "581b0df1-c4cf-4a97-828e-13dd740defe5": raillabel.format.Bbox(
                uid=None,
                object=None,
                sensor=None,
                attributes=None,
                pos=raillabel.format.Point2d(0, 0),
                size=raillabel.format.Size2d(0, 0),
            )
        }
    )
    assert not _is_frame_empty(frame)


if __name__ == "__main__":
    os.system("clear")
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
