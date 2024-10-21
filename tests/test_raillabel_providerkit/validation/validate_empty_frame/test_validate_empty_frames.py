# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import raillabel

from raillabel_providerkit.validation.validate_empty_frames.validate_empty_frames import (
    _is_frame_empty,
)


def test_is_frame_empty__true():
    frame = raillabel.format.Frame(uid=0, annotations={})
    assert _is_frame_empty(frame)

def test_is_frame_empty__false(empty_annotation):
    frame = raillabel.format.Frame(
        uid=0,
        annotations={
            "581b0df1-c4cf-4a97-828e-13dd740defe5": empty_annotation
        }
    )
    assert not _is_frame_empty(frame)


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
