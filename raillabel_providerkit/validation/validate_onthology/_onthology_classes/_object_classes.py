# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

import raillabel

from ._attributes._attribute_abc import _Attribute, attribute_classes
from ._sensor_type import _SensorType


@dataclass
class _ObjectClass:
    attributes: dict[str, type[_Attribute]]
    sensor_types: dict[raillabel.format.SensorType, _SensorType]

    @classmethod
    def fromdict(cls, data_dict: dict) -> _ObjectClass:
        if "attributes" not in data_dict:
            data_dict["attributes"] = {}

        if "sensor_types" not in data_dict:
            data_dict["sensor_types"] = {}

        return _ObjectClass(
            attributes={
                attr_name: cls._attribute_fromdict(attr)
                for attr_name, attr in data_dict["attributes"].items()
            },
            sensor_types=cls._sensor_types_fromdict(data_dict["sensor_types"]),
        )

    def check(self, annotation: type[raillabel.format._ObjectAnnotation]) -> list[str]:
        errors = []

        errors.extend(self._check_undefined_attributes(annotation))
        errors.extend(self._check_missing_attributes(annotation))
        errors.extend(self._check_false_attribute_type(annotation))

        return errors

    @classmethod
    def _attribute_fromdict(cls, attribute: dict or str) -> type[_Attribute]:
        for attribute_class in attribute_classes():
            if attribute_class.supports(attribute):
                return attribute_class.fromdict(attribute)

        raise ValueError

    @classmethod
    def _sensor_types_fromdict(cls, sensor_types_dict: dict) -> dict[str, _SensorType]:
        return {
            raillabel.format.SensorType(type_id): _SensorType.fromdict(sensor_type_dict)
            for type_id, sensor_type_dict in sensor_types_dict.items()
        }

    def _check_undefined_attributes(
        self, annotation: type[raillabel.format._ObjectAnnotation]
    ) -> list[str]:
        return [
            f"Undefined attribute '{attr_name}' in annotation {annotation.uid}."
            for attr_name in annotation.attributes
            if attr_name not in self._compile_applicable_attributes(annotation)
        ]

    def _check_missing_attributes(
        self, annotation: type[raillabel.format._ObjectAnnotation]
    ) -> list[str]:
        return [
            f"Missing attribute '{attr_name}' in annotation {annotation.uid}."
            for attr_name in self._compile_applicable_attributes(annotation)
            if attr_name not in annotation.attributes
        ]

    def _check_false_attribute_type(
        self, annotation: type[raillabel.format._ObjectAnnotation]
    ) -> list[str]:
        errors = []

        applicable_attributes = self._compile_applicable_attributes(annotation)
        for attr_name, attr_value in annotation.attributes.items():
            if attr_name not in applicable_attributes:
                continue

            errors.extend(
                applicable_attributes[attr_name].check(attr_name, attr_value, annotation.uid)
            )

        return errors

    def _compile_applicable_attributes(
        self, annotation: type[raillabel.format._ObjectAnnotation]
    ) -> dict[str, type[_Attribute]]:
        applicable_attributes = self.attributes

        if annotation.sensor.type in self.sensor_types:
            applicable_attributes.update(self.sensor_types[annotation.sensor.type].attributes)

        return applicable_attributes
