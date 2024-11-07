# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import raillabel


def filter_sensor_uids_by_type(
    sensors: list[raillabel.format.Sensor], sensor_type: raillabel.format.SensorType
) -> set[str]:
    """Get the uids of all given sensors matching the given SensorType.

    Parameters
    ----------
    sensors : list[raillabel.format.Sensor]
        The sensors to filter.
    sensor_type : raillabel.format.SensorType
        The SensorType to filter by.

    Returns
    -------
    set[str]
        The list of uids of matching sensors.

    """
    return {sensor.uid for sensor in sensors if sensor.type == sensor_type}
