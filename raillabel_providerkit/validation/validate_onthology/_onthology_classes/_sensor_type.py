# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _SensorType:
    @classmethod
    def fromdict(cls) -> _SensorType:
        return _SensorType()
