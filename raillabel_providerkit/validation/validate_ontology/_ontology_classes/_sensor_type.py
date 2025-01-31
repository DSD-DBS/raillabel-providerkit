# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class _SensorType(Enum):
    CAMERA = "camera"
    LIDAR = "lidar"
    RADAR = "radar"
