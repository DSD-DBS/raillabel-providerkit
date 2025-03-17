# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

import raillabel

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_ontology._ontology_classes._sensor_type import (
    _SensorType,
)

from ._attributes._attribute_abc import _Attribute, attribute_classes


@dataclass
class _ObjectClass:
    attributes: dict[str, _Attribute]

    @classmethod
    def fromdict(cls, data: dict) -> _ObjectClass:
        return _ObjectClass(
            attributes={attr_name: cls._attribute_fromdict(attr) for attr_name, attr in data.items()}
        )

    def check(
        self,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        errors = []
        errors.extend(self._check_undefined_attributes(annotation, sensor_type, identifiers))
        errors.extend(self._check_missing_attributes(annotation, sensor_type, identifiers))
        errors.extend(self._check_false_attribute_type(annotation, sensor_type, identifiers))
        return errors

    @classmethod
    def _attribute_fromdict(cls, attribute: dict) -> _Attribute:
        for attribute_class in attribute_classes():
            if attribute_class.supports(attribute):
                return attribute_class.fromdict(attribute)

        raise ValueError

    def _check_undefined_attributes(
        self,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_UNDEFINED,
                identifiers=identifiers,
            )
            for attr_name in annotation.attributes
            if attr_name not in self._compile_applicable_attributes(sensor_type)
        ]

    def _check_missing_attributes(
        self,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_MISSING,
                identifiers=identifiers,
            )
            for attr_name, attr in self._compile_applicable_attributes(sensor_type).items()
            if attr_name not in annotation.attributes and not attr.optional
        ]

    def _check_false_attribute_type(
        self,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        errors = []

        applicable_attributes = self._compile_applicable_attributes(sensor_type)
        for attr_name, attr_value in annotation.attributes.items():
            if attr_name not in applicable_attributes:
                continue

            identifiers.attribute = attr_name
            errors.extend(
                applicable_attributes[attr_name].check_type_and_value(
                    attr_name,
                    attr_value,
                    identifiers=identifiers,
                )
            )

        return errors

    def _compile_applicable_attributes(
        self,
        sensor_type: _SensorType,
    ) -> dict[str, _Attribute]:
        return {
            attr_name: attr
            for attr_name, attr in self.attributes.items()
            if sensor_type in [_SensorType(sensor_type_str) for sensor_type_str in attr.sensor_types]
        }
