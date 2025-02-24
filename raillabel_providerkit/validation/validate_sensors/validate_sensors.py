# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import raillabel
from raillabel.format import Camera, GpsImu, Lidar, Radar

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

SENSOR_TYPE_MAPPING = {
    "rgb_middle": Camera,
    "rgb_left": Camera,
    "rgb_right": Camera,
    "rgb_highres_middle": Camera,
    "rgb_highres_left": Camera,
    "rgb_highres_right": Camera,
    "rgb_longrange_middle": Camera,
    "rgb_longrange_left": Camera,
    "rgb_longrange_right": Camera,
    "ir_middle": Camera,
    "ir_left": Camera,
    "ir_right": Camera,
    "lidar": Lidar,
    "radar": Radar,
    "gps_imu": GpsImu,
}


def validate_sensors(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether whether all sensors have supported names and have the correct type."""
    issues = []

    for sensor_id in scene.sensors:
        if sensor_id in SENSOR_TYPE_MAPPING:
            continue
        issues.append(
            Issue(
                type=IssueType.SENSOR_ID_UNKNOWN,
                identifiers=IssueIdentifiers(sensor=sensor_id),
                reason=f"Supported sensor ids: {list(SENSOR_TYPE_MAPPING.keys())}",
            )
        )

    return issues
