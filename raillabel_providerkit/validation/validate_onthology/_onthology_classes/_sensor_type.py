# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from ._attributes._attribute_abc import _Attribute, attribute_classes


@dataclass
class _SensorType:
    attributes: dict[str, type[_Attribute]]

    @classmethod
    def fromdict(cls, data_dict: dict) -> _SensorType:
        if "attributes" not in data_dict:
            data_dict["attributes"] = {}

        return _SensorType(
            attributes={
                attr_name: cls._attribute_fromdict(attr)
                for attr_name, attr in data_dict["attributes"].items()
            }
        )

    @classmethod
    def _attribute_fromdict(cls, attribute: dict | str) -> type[_Attribute]:
        for attribute_class in attribute_classes():
            if attribute_class.supports(attribute):
                return attribute_class.fromdict(attribute)

        raise ValueError
