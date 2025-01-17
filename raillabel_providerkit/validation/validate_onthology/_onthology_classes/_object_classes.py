# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import raillabel

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_onthology._onthology_classes._sensor_type import (
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
        annotation_uid: UUID,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        frame_id: int,
    ) -> list[Issue]:
        errors = []

        errors.extend(
            self._check_undefined_attributes(annotation_uid, annotation, sensor_type, frame_id)
        )
        errors.extend(
            self._check_missing_attributes(annotation_uid, annotation, sensor_type, frame_id)
        )
        errors.extend(
            self._check_false_attribute_type(annotation_uid, annotation, sensor_type, frame_id)
        )

        return errors

    @classmethod
    def _attribute_fromdict(cls, attribute: dict) -> _Attribute:
        for attribute_class in attribute_classes():
            if attribute_class.supports(attribute):
                return attribute_class.fromdict(attribute)

        raise ValueError

    def _check_undefined_attributes(
        self,
        annotation_uid: UUID,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        frame_id: int,
    ) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_UNDEFINED,
                identifiers=IssueIdentifiers(
                    annotation=annotation_uid,
                    attribute=attr_name,
                    frame=frame_id,
                    object=annotation.object_id,
                    sensor=annotation.sensor_id,
                ),
            )
            for attr_name in annotation.attributes
            if attr_name not in self._compile_applicable_attributes(sensor_type)
        ]

    def _check_missing_attributes(
        self,
        annotation_uid: UUID,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        frame_id: int,
    ) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_MISSING,
                identifiers=IssueIdentifiers(
                    annotation=annotation_uid,
                    attribute=attr_name,
                    frame=frame_id,
                    object=annotation.object_id,
                    sensor=annotation.sensor_id,
                ),
            )
            for attr_name, attr in self._compile_applicable_attributes(sensor_type).items()
            if attr_name not in annotation.attributes and not attr.optional
        ]

    def _check_false_attribute_type(
        self,
        annotation_uid: UUID,
        annotation: raillabel.format.Bbox
        | raillabel.format.Cuboid
        | raillabel.format.Poly2d
        | raillabel.format.Poly3d
        | raillabel.format.Seg3d,
        sensor_type: _SensorType,
        frame_id: int,
    ) -> list[Issue]:
        errors = []

        applicable_attributes = self._compile_applicable_attributes(sensor_type)
        for attr_name, attr_value in annotation.attributes.items():
            if attr_name not in applicable_attributes:
                continue

            errors.extend(
                applicable_attributes[attr_name].check_type_and_value(
                    attr_name,
                    attr_value,
                    identifiers=IssueIdentifiers(
                        annotation=annotation_uid,
                        attribute=attr_name,
                        frame=frame_id,
                        object=annotation.object_id,
                        sensor=annotation.sensor_id,
                    ),
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
