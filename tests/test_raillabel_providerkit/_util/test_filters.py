# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
import raillabel

from raillabel_providerkit._util._filters import filter_sensor_uids_by_type


@pytest.fixture
def sensor_types() -> list[raillabel.format.SensorType]:
    return [sensor_type for sensor_type in raillabel.format.SensorType]


def test_filter_sensor_uids_by_type__empty(sensor_types):
    sensors = []
    for sensor_type in sensor_types:
        assert len(filter_sensor_uids_by_type(sensors, sensor_type)) == 0


def test_filter_sensor_uids_by_type__exactly_one_match(sensor_types):
    # Create a list of sensors where each sensor type occurs exactly once
    sensors = []
    for i in range(len(sensor_types)):
        sensors.append(raillabel.format.Sensor(uid=f"test_{i}", type=sensor_types[i]))

    # Ensure the filter works for each sensor type
    for sensor_type in sensor_types:
        results = filter_sensor_uids_by_type(sensors, sensor_type)
        assert len(results) == 1
        # Assert the result is of correct type
        matches = 0
        for sensor in sensors:
            if sensor.uid in results:
                assert sensor.type == sensor_type
                matches += 1
        assert matches == len(results)


def test_filter_sensor_uids_by_type__multiple_matches(sensor_types):
    # Create a list of sensors where each sensor type occurs three times
    sensors = []
    i = 0
    for sensor_type in sensor_types:
        for j in range(3):
            sensors.append(raillabel.format.Sensor(uid=f"test_{i}", type=sensor_type))
            i += 1

    # Ensure the filter works for each sensor type
    for sensor_type in sensor_types:
        results = filter_sensor_uids_by_type(sensors, sensor_type)
        assert len(results) == 3
        # Assert the results are of correct type
        matches = 0
        for sensor in sensors:
            if sensor.uid in results:
                assert sensor.type == sensor_type
                matches += 1
        assert matches == len(results)
