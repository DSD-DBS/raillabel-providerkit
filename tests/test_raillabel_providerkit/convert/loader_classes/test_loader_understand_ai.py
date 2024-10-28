# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from raillabel_providerkit.convert.loader_classes.loader_understand_ai import LoaderUnderstandAi


def test_supports__true(json_data):
    assert LoaderUnderstandAi().supports(json_data["understand_ai_real_life"])


def test_supports__false(json_data):
    data = json_data["understand_ai_real_life"]
    del data["metadata"]["project_id"]
    assert not LoaderUnderstandAi().supports(data)


def test_validate_schema__real_life_file__no_errors(json_data):
    actual = LoaderUnderstandAi().validate_schema(json_data["understand_ai_real_life"])
    assert actual == []


def test_validate_schema__real_life_file__errors(json_data):
    data = json_data["understand_ai_real_life"]
    del data["coordinateSystems"][0]["topic"]

    actual = LoaderUnderstandAi().validate_schema(json_data["understand_ai_real_life"])
    assert len(actual) == 1
    assert "topic" in actual[0]


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear"])
