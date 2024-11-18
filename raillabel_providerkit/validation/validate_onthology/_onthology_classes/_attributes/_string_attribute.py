# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _StringAttribute(_Attribute):
    @classmethod
    def supports(cls, data_dict: dict) -> bool:
        return data_dict == "string"

    @classmethod
    def fromdict(cls, _: dict) -> _StringAttribute:
        return _StringAttribute()

    def check(
        self, attribute_name: str, attribute_value: bool | float | str | list, annotation_id: str
    ) -> list[str]:
        errors = []

        if type(attribute_value) is not str:
            errors.append(
                f"Attribute '{attribute_name}' of annotation {annotation_id} is of type "
                f"'{attribute_value.__class__.__name__}' (should be 'str')."
            )

        return errors
