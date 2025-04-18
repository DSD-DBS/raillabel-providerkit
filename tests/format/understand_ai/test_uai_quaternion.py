# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import raillabel_providerkit.format.understand_ai as uai_format

# == Fixtures =========================


@pytest.fixture
def quaternion_uai_dict() -> dict:
    return {
        "x": 0.75318325,
        "y": -0.10270147,
        "z": 0.21430262,
        "w": -0.61338551,
    }


@pytest.fixture
def quaternion_uai() -> dict:
    return uai_format.Quaternion(
        x=0.75318325,
        y=-0.10270147,
        z=0.21430262,
        w=-0.61338551,
    )


@pytest.fixture
def quaternion_vec() -> dict:
    return [0.75318325, -0.10270147, 0.21430262, -0.61338551]


# == Tests ============================


def test_fromdict():
    quaternion = uai_format.Quaternion.fromdict(
        {
            "x": 0.75318325,
            "y": -0.10270147,
            "z": 0.21430262,
            "w": -0.61338551,
        }
    )

    assert quaternion.x == 0.75318325
    assert quaternion.y == -0.10270147
    assert quaternion.z == 0.21430262
    assert quaternion.w == -0.61338551


if __name__ == "__main__":
    import os

    os.system("clear")
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
