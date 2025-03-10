# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

from raillabel.format import Camera, GpsImu, Lidar, Radar


@dataclass
class _SensorMetadata:
    type: type
    uri: str


STANDARD_SENSORS = {
    "rgb_center": _SensorMetadata(
        type=Camera,
        uri="/S1206063/image",
    ),
    "rgb_left": _SensorMetadata(
        type=Camera,
        uri="/S1206062/image",
    ),
    "rgb_right": _SensorMetadata(
        type=Camera,
        uri="/S1206064/image",
    ),
    "rgb_highres_center": _SensorMetadata(
        type=Camera,
        uri="/S1213752/image",
    ),
    "rgb_highres_left": _SensorMetadata(
        type=Camera,
        uri="/S1213751/image",
    ),
    "rgb_highres_right": _SensorMetadata(
        type=Camera,
        uri="/S1213755/image",
    ),
    "rgb_longrange_center": _SensorMetadata(
        type=Camera,
        uri="/S1213752/image",
    ),
    "rgb_longrange_left": _SensorMetadata(
        type=Camera,
        uri="/S1213751/image",
    ),
    "rgb_longrange_right": _SensorMetadata(
        type=Camera,
        uri="/S1213755/image",
    ),
    "ir_center": _SensorMetadata(
        type=Camera,
        uri="/A0001781/image",
    ),
    "ir_left": _SensorMetadata(
        type=Camera,
        uri="/A0001780/image",
    ),
    "ir_right": _SensorMetadata(
        type=Camera,
        uri="/A0001782/image",
    ),
    "lidar": _SensorMetadata(
        type=Lidar,
        uri="/lidar_merged",
    ),
    "radar": _SensorMetadata(
        type=Radar,
        uri="/talker1/Nvt/Cartesian",
    ),
    "gps_imu": _SensorMetadata(
        type=GpsImu,
        uri="/novatel/oem7/inspva",
    ),
}
