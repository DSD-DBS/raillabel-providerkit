# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import raillabel

from raillabel_providerkit.validation.validate_empty_frames.validate_empty_frames import (
    _is_frame_empty,
    validate_empty_frames,
)


def test_is_frame_empty__true():
    frame = raillabel.format.Frame(uid=0, annotations={})
    assert _is_frame_empty(frame)

def test_is_frame_empty__false(empty_annotation, empty_frame):
    frame = empty_frame
    frame.annotations["581b0df1-c4cf-4a97-828e-13dd740defe5"] = empty_annotation

    assert not _is_frame_empty(frame)

def test_validate_empty_frames__no_error(default_frame, empty_scene):
    scene = empty_scene
    scene.frames = {
        0: default_frame,
        1: default_frame,
        2: default_frame,
    }

    assert len(validate_empty_frames(scene)) == 0

def test_validate_empty_frames__one_error(default_frame, empty_frame, empty_scene):
    scene = empty_scene
    scene.frames = {
        0: default_frame,
        1: empty_frame,
        2: default_frame,
    }

    assert len(validate_empty_frames(scene)) == 1

def test_validate_empty_frames__two_errors(default_frame, empty_frame, empty_scene):
    scene = empty_scene
    scene.frames = {
        0: empty_frame,
        1: default_frame,
        2: empty_frame,
    }

    assert len(validate_empty_frames(scene)) == 2

def test_validate_empty_frames__error_message_contains_indentifying_info(empty_frame, empty_scene):
    scene = empty_scene
    scene.frames = {
        0: empty_frame,
    }

    error_message = validate_empty_frames(scene)[0].lower()
    assert "frame" in error_message
    assert "0" in error_message
    assert "empty" in error_message or "no annotations" in error_message


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])