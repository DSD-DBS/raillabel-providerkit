# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path

from raillabel_providerkit.validation.validate_onthology.validate_onthology import (
    validate_onthology,
    _validate_onthology_schema,
    _load_onthology,
    OnthologySchemaError,
)

ONTHOLOGY_PATH = Path(__file__).parent.parent.parent / "__assets__/osdar23_onthology.yaml"


@pytest.fixture
def onthology_dict() -> dict:
    return _load_onthology(ONTHOLOGY_PATH)


def test_validate_onthology_schema__none():
    with pytest.raises(OnthologySchemaError):
        _validate_onthology_schema(None)


def test_validate_onthology_schema__empty():
    _validate_onthology_schema({})


def test_validate_onthology_schema__invalid():
    invalid_dict = {"foo": "bar"}
    with pytest.raises(OnthologySchemaError):
        _validate_onthology_schema(invalid_dict)


def test_validate_onthology_schema__valid(onthology_dict):
    _validate_onthology_schema(onthology_dict)
